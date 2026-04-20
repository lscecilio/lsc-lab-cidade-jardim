#!/usr/bin/env python3
APP_VERSION = "1.1.0"

import base64, pathlib, mimetypes, json, time, threading, sqlite3, os, uuid, hmac, binascii
import urllib.request
from flask import Flask, request, Response, jsonify

DOC_DIR = pathlib.Path('/opt/lsc-lab/apps/lsc-hub')
DB_PATH = DOC_DIR / 'tasks.db'
VALID_TASK_STATUSES = {'pending', 'in_progress', 'done', 'blocked'}
VALID_TASK_PRIORITIES = {'baixa', 'media', 'alta'}

SYSTEM_PROMPT = """Você é o Assistente Jurídico e Operacional da LSC-Lab — empresa de tecnologia e SaaS.
Produtos: Atlas Platform, Atlas-Vendas, Atlas-Healer, Atlas-Hub, bots IA (CLO, CMO, CTO, COO, CFO, CBO, CRO).
Infraestrutura: Hetzner (Hock server 100.77.253.80), Tailscale, Cloudflare.
Stack: Python/Flask, Node.js, PostgreSQL, SQLite, Redis, Docker.
Responda em português brasileiro, seja técnico e direto.
Quando souber, cite o ID do processo relevante (ex: LSC-001)."""

app = Flask(__name__)

chat_sessions: dict = {}
chat_lock = threading.Lock()


def get_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'pending',
                priority TEXT DEFAULT 'media',
                module TEXT,
                process_id TEXT,
                assigned_to TEXT,
                due_date TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS task_comments (
                id TEXT PRIMARY KEY,
                task_id TEXT NOT NULL,
                comment TEXT NOT NULL,
                author TEXT,
                created_at TEXT
            )
        """)
        conn.commit()


def load_basic_auth_users():
    users = {}

    env_user = os.environ.get('LSC_HUB_BASIC_AUTH_USER')
    env_pass = os.environ.get('LSC_HUB_BASIC_AUTH_PASS')
    if env_user and env_pass:
        users[env_user] = env_pass

    raw_json = os.environ.get('LSC_HUB_BASIC_AUTH_JSON')
    if raw_json:
        data = json.loads(raw_json)
        if not isinstance(data, dict):
            raise ValueError('LSC_HUB_BASIC_AUTH_JSON deve ser um objeto JSON.')
        users.update({str(k): str(v) for k, v in data.items() if str(k) and str(v)})

    auth_file = os.environ.get('LSC_HUB_BASIC_AUTH_FILE')
    candidate_paths = [
        pathlib.Path(auth_file) if auth_file else None,
        pathlib.Path('/home/claw/.openclaw/secrets/lsc_hub_basic_auth.json'),
        pathlib.Path('/root/.openclaw/secrets/lsc_hub_basic_auth.json'),
    ]
    for path in candidate_paths:
        if not path or not path.exists():
            continue
        data = json.loads(path.read_text())
        if not isinstance(data, dict):
            raise ValueError(f'Arquivo de auth inválido: {path}')
        users.update({str(k): str(v) for k, v in data.items() if str(k) and str(v)})

    return users


def _parse_basic_auth(auth_header):
    if not auth_header.startswith('Basic '):
        return None, None
    try:
        decoded = base64.b64decode(auth_header[6:].strip()).decode('utf-8')
    except (binascii.Error, UnicodeDecodeError):
        return None, None
    if ':' not in decoded:
        return None, None
    return decoded.split(':', 1)


def check_auth():
    username, password = _parse_basic_auth(request.headers.get('Authorization', ''))
    if username is None:
        return False
    try:
        valid_users = load_basic_auth_users()
    except (json.JSONDecodeError, OSError, ValueError):
        app.logger.exception('Falha ao carregar credenciais do lsc-hub.')
        return False
    expected = valid_users.get(username)
    return expected is not None and hmac.compare_digest(expected, password)


def resp_401():
    return Response('Acesso restrito.', 401,
                    {'WWW-Authenticate': 'Basic realm="LSC-Hub"',
                     'Content-Type': 'text/plain'})


def get_anthropic_key():
    key_path = pathlib.Path('/home/claw/.openclaw/secrets/anthropic_api_key')
    try:
        return key_path.read_text().strip()
    except Exception:
        return os.environ.get('ANTHROPIC_API_KEY', '')


def _extract_processes(payload):
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        processes = payload.get('processes', [])
        return processes if isinstance(processes, list) else []
    return []


def load_process_context():
    data_dir = DOC_DIR / 'data'
    if not data_dir.exists():
        return ''

    ids = []
    seen = set()
    for proc_path in sorted(data_dir.glob('*processes.json')):
        try:
            data = json.loads(proc_path.read_text())
        except (json.JSONDecodeError, OSError):
            app.logger.exception('Falha ao ler base processual: %s', proc_path)
            continue
        for process in _extract_processes(data):
            process_id = process.get('id')
            if process_id and process_id not in seen:
                seen.add(process_id)
                ids.append(process_id)

    if not ids:
        return ''

    preview = ', '.join(ids[:50])
    suffix = '...' if len(ids) > 50 else ''
    return f"\nProcessos LSC disponíveis: {preview}{suffix}."


def _validate_task_status(value):
    if value not in VALID_TASK_STATUSES:
        raise ValueError('status inválido')
    return value


def _validate_task_priority(value):
    if value not in VALID_TASK_PRIORITIES:
        raise ValueError('priority inválido')
    return value


def _resolve_doc_path(fpath):
    doc_root = DOC_DIR.resolve()
    rel_path = pathlib.PurePosixPath(fpath)
    candidates = [doc_root / rel_path]
    if not rel_path.suffix:
        candidates.append(doc_root / (str(rel_path) + '.html'))

    for candidate in candidates:
        resolved = candidate.resolve()
        try:
            resolved.relative_to(doc_root)
        except ValueError:
            return None, 403
        if resolved.is_file():
            return resolved, 200

    return None, 404


@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'app': 'lsc-hub', 'version': APP_VERSION, 'ts': int(time.time())})


@app.route('/api/chat', methods=['POST'])
def api_chat():
    if not check_auth():
        return resp_401()
    body = request.get_json(silent=True) or {}
    message = (body.get('message') or '').strip()
    if not message:
        return jsonify({'ok': False, 'error': 'message é obrigatório'}), 400

    session_id = body.get('session_id') or str(uuid.uuid4())

    with chat_lock:
        history = chat_sessions.get(session_id, [])
        history = history[-20:]  # keep last 10 turns (20 msgs)
        history.append({'role': 'user', 'content': message})
        chat_sessions[session_id] = history

    anthropic_key = get_anthropic_key()
    if not anthropic_key:
        return jsonify({'ok': False, 'error': 'Chave Anthropic não configurada'}), 500

    proc_ctx = load_process_context()
    system = SYSTEM_PROMPT + proc_ctx

    try:
        payload = json.dumps({
            'model': 'claude-haiku-4-5',
            'max_tokens': 1024,
            'system': system,
            'messages': history
        }).encode('utf-8')
        req = urllib.request.Request(
            'https://api.anthropic.com/v1/messages',
            data=payload,
            headers={
                'Content-Type': 'application/json',
                'x-api-key': anthropic_key,
                'anthropic-version': '2023-06-01'
            },
            method='POST'
        )
        with urllib.request.urlopen(req, timeout=30) as r:
            result = json.loads(r.read().decode())

        assistant_msg = result['content'][0]['text']
        with chat_lock:
            chat_sessions[session_id].append({'role': 'assistant', 'content': assistant_msg})

        return jsonify({'ok': True, 'response': assistant_msg, 'session_id': session_id})
    except Exception:
        app.logger.exception('Falha ao processar chat do lsc-hub.')
        return jsonify({'ok': False, 'error': 'Falha ao processar chat'}), 502


@app.route('/api/tasks', methods=['GET', 'POST'])
def api_tasks():
    if not check_auth():
        return resp_401()

    if request.method == 'GET':
        status = request.args.get('status')
        priority = request.args.get('priority')
        module = request.args.get('module')
        sql = 'SELECT * FROM tasks WHERE 1=1'
        params: list = []
        if status:
            sql += ' AND status=?'; params.append(status)
        if priority:
            sql += ' AND priority=?'; params.append(priority)
        if module:
            sql += ' AND module=?'; params.append(module)
        sql += ' ORDER BY created_at DESC'
        with get_db() as conn:
            rows = conn.execute(sql, params).fetchall()
        return jsonify({'ok': True, 'tasks': [dict(r) for r in rows]})

    body = request.get_json(silent=True) or {}
    title = (body.get('title') or '').strip()
    if not title:
        return jsonify({'ok': False, 'error': 'title é obrigatório'}), 400
    try:
        status = _validate_task_status(body.get('status', 'pending'))
        priority = _validate_task_priority(body.get('priority', 'media'))
    except ValueError as exc:
        return jsonify({'ok': False, 'error': str(exc)}), 400
    now = time.strftime('%Y-%m-%dT%H:%M:%S')
    task = {
        'id': str(uuid.uuid4()),
        'title': title,
        'description': body.get('description', ''),
        'status': status,
        'priority': priority,
        'module': body.get('module', ''),
        'process_id': body.get('process_id', ''),
        'assigned_to': body.get('assigned_to', ''),
        'due_date': body.get('due_date', ''),
        'created_at': now,
        'updated_at': now,
    }
    with get_db() as conn:
        conn.execute(
            'INSERT INTO tasks VALUES (:id,:title,:description,:status,:priority,:module,:process_id,:assigned_to,:due_date,:created_at,:updated_at)',
            task
        )
        conn.commit()
    return jsonify({'ok': True, 'task': task}), 201


@app.route('/api/tasks/<task_id>', methods=['GET', 'PUT', 'DELETE'])
def api_task(task_id):
    if not check_auth():
        return resp_401()

    def fetch():
        with get_db() as conn:
            row = conn.execute('SELECT * FROM tasks WHERE id=?', [task_id]).fetchone()
        return dict(row) if row else None

    if request.method == 'GET':
        t = fetch()
        return (jsonify({'ok': True, 'task': t}) if t
                else jsonify({'ok': False, 'error': 'não encontrada'}), 404)

    if request.method == 'DELETE':
        with get_db() as conn:
            conn.execute('DELETE FROM tasks WHERE id=?', [task_id])
            conn.execute('DELETE FROM task_comments WHERE task_id=?', [task_id])
            conn.commit()
        return jsonify({'ok': True})

    body = request.get_json(silent=True) or {}
    if 'status' in body:
        try:
            body['status'] = _validate_task_status(body['status'])
        except ValueError as exc:
            return jsonify({'ok': False, 'error': str(exc)}), 400
    if 'priority' in body:
        try:
            body['priority'] = _validate_task_priority(body['priority'])
        except ValueError as exc:
            return jsonify({'ok': False, 'error': str(exc)}), 400

    allowed = ('title', 'description', 'status', 'priority', 'module', 'process_id', 'assigned_to', 'due_date')
    sets = [f"{k}=?" for k in allowed if k in body]
    vals = [body[k] for k in allowed if k in body]
    if not sets:
        return jsonify({'ok': False, 'error': 'nenhum campo para atualizar'}), 400
    sets.append('updated_at=?')
    vals.append(time.strftime('%Y-%m-%dT%H:%M:%S'))
    vals.append(task_id)
    with get_db() as conn:
        conn.execute(f"UPDATE tasks SET {', '.join(sets)} WHERE id=?", vals)
        conn.commit()
    return jsonify({'ok': True, 'task': fetch()})


@app.route('/api/tasks/<task_id>/comments', methods=['GET', 'POST'])
def api_task_comments(task_id):
    if not check_auth():
        return resp_401()

    if request.method == 'GET':
        with get_db() as conn:
            rows = conn.execute(
                'SELECT * FROM task_comments WHERE task_id=? ORDER BY created_at',
                [task_id]
            ).fetchall()
        return jsonify({'ok': True, 'comments': [dict(r) for r in rows]})

    body = request.get_json(silent=True) or {}
    comment = (body.get('comment') or '').strip()
    if not comment:
        return jsonify({'ok': False, 'error': 'comment é obrigatório'}), 400
    row = {
        'id': str(uuid.uuid4()),
        'task_id': task_id,
        'comment': comment,
        'author': body.get('author', 'lsc'),
        'created_at': time.strftime('%Y-%m-%dT%H:%M:%S'),
    }
    with get_db() as conn:
        conn.execute(
            'INSERT INTO task_comments VALUES (:id,:task_id,:comment,:author,:created_at)',
            row
        )
        conn.commit()
    return jsonify({'ok': True, 'comment': row}), 201


@app.route('/', defaults={'fpath': 'hub.html'})
@app.route('/<path:fpath>', methods=['GET', 'HEAD'])
def serve_file(fpath):
    if not check_auth():
        return resp_401()
    p, status = _resolve_doc_path(fpath)
    if status == 403:
        return Response('Caminho inválido.', 403, {'Content-Type': 'text/plain'})
    if status == 404:
        return Response('Arquivo não encontrado.', 404, {'Content-Type': 'text/plain'})
    try:
        data = p.read_bytes()
        ct = mimetypes.guess_type(str(p))[0] or 'text/html'
        return Response(data, 200, {'Content-Type': ct})
    except OSError:
        app.logger.exception('Falha ao servir arquivo %s', p)
        return Response('Erro interno ao servir arquivo.', 500, {'Content-Type': 'text/plain'})


if __name__ == '__main__':
    init_db()
    print(f'[lsc-hub v{APP_VERSION}] :3091 (Flask)')
    app.run(host='127.0.0.1', port=3091, threaded=True)
