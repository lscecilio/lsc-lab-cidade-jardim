# Missão: QC02 — Correção e Visualização 3D Completa
> Criada: 2026-04-08 | Status: EM ANDAMENTO | Sessões: 7 estimadas

## Objetivo
Corrigir o posicionamento estratégico da QC02 no masterplan, atualizar para 4 torres (não 2), criar mapa 3D interativo com prédios, esboço do parque, vídeo, novas imagens e auditar tudo.

## Diagnóstico Inicial

### Problemas Encontrados
1. **Coordenadas falsas nos HTMLs** — `aldora-mapa-3d.html` usa coordenadas inventadas (~-48.28, ~-18.91) que NÃO correspondem aos KMZ reais
2. **Coordenadas reais dos KMZ**:
   - QC01: centróide ~ -48.3063, -18.9577 (polígono de 13 vértices)
   - QC02: centróide ~ -48.3061, -18.5999 (polígono de 5 vértices)
   - QC03: centróide ~ -48.3061, -18.9617 (polígono de 5 vértices)
   - Al'Dora City (macro): centróide ~ -48.2983, -18.9669 (polígono de 22 vértices)
3. **QC02 mostra apenas 2 torres (E/F)** — Leandro confirma que são 4 torres
4. **Parque entre QC02 e Jardins Versailles** — não existe representação ainda
5. **Nenhum vídeo** do projeto

## Sessões

### M1 — Correção Geoespacial + Estrutural (~1.5h) [Opus]
- [ ] Extrair coordenadas EXATAS de todos os KMZ (QC01, QC02, QC03, Al'Dora City)
- [ ] Confirmar com Leandro: quais são as 4 torres da QC02? (E/F/I/J? ou renumerar?)
- [ ] Corrigir `aldora-mapa-3d.html` com coordenadas reais dos KMZ
- [ ] Corrigir `aldora-3d-avancado.html` — adicionar 4 torres na QC02
- [ ] Corrigir `aldora-implantacao.html` — atualizar diagrama SVG
- [ ] Corrigir `aldora-3d-terreno.html` e `aldora-satellite-real.html`
- [ ] Corrigir centro do mapa para coordenadas reais
- [ ] Atualizar `CLAUDE.md` e dados JSON com 4 torres QC02
Critério: Todos os HTMLs com coordenadas reais + QC02 com 4 torres

### M2 — Pesquisa de Ferramentas 3D (~1h) [Sonnet]
- [ ] Pesquisar GitHub: "3D building visualization mapbox", "cesium 3d buildings", "three.js architecture"
- [ ] Avaliar: CesiumJS, Deck.gl, Three.js + Mapbox, OSM Buildings, iTwin.js
- [ ] Pesquisar apps comerciais: SketchUp Web, Spline, Matterport, Modelo.io
- [ ] Avaliar viabilidade de cada solução pro nosso caso (HTML standalone)
- [ ] Documentar top 3 opções com prós/contras
- [ ] Selecionar stack final para implementação
Critério: Documento de decisão com stack escolhida

### M3 — Mapa 3D Interativo com 4 Torres QC02 (~2h) [Opus]
Depende de: M1, M2
- [ ] Implementar mapa 3D com a stack escolhida na M2
- [ ] Posicionar as 3 quadras com polígonos reais dos KMZ
- [ ] QC01: 4 torres (A/B/C/D) com alturas corretas
- [ ] QC02: 4 torres (confirmar nomes) com alturas corretas
- [ ] QC03: 2 torres (G/H) premium, mais altas
- [ ] Texturização diferenciada por empreendimento
- [ ] Labels interativos com dados de cada torre
- [ ] Orbit camera + controles touch
- [ ] Skyline view lateral mostrando escalonamento
Critério: HTML standalone abrível no browser com 10 torres 3D posicionadas corretamente

### M4 — Esboço do Parque Central (~1h) [Opus]
Depende de: M1
- [ ] Definir limites do parque (entre QC02 e área Versailles)
- [ ] Criar planta baixa ilustrativa (SVG/HTML)
- [ ] Elementos: caminhos, áreas verdes, espelhos d'água, playground, fitness
- [ ] Integrar com o mapa de implantação
- [ ] Vista aérea conceitual do parque
Critério: HTML com visualização do parque integrado ao masterplan

### M5 — Novas Imagens e Renders (~1h) [Opus]
Depende de: M3, M4
- [ ] Gerar screenshots do mapa 3D em múltiplos ângulos
- [ ] Criar composições visuais para apresentação
- [ ] Atualizar thumbnails em assets/img/
- [ ] Gerar prompts Midjourney atualizados (4 torres QC02)
- [ ] Criar mockup de skyline com as 10 torres
Critério: Mínimo 6 novas imagens + prompts atualizados

### M6 — Vídeo Flythrough (~1.5h) [Opus]
Depende de: M3, M5
- [ ] Pesquisar libs de animação 3D (anime.js, GSAP, Three.js camera path)
- [ ] Criar roteiro: overview → QC01 → parque → QC02 → QC03 → skyline
- [ ] Implementar animação de câmera orbital progressiva
- [ ] Adicionar overlays de dados durante flythrough
- [ ] Exportar como HTML interativo + pesquisar captura para MP4
Critério: Animação de 30-60s mostrando todo o masterplan

### M7 — Auditoria Dupla + Deploy + Notificação (~1h) [Opus]
Depende de: M1–M6
- [ ] **Auditoria Humana**: revisar visualmente cada HTML no browser
  - Posições geográficas conferem com Google Earth?
  - 4 torres na QC02 visíveis?
  - Parque está entre as quadras corretas?
  - Dados numéricos batem com CLAUDE.md?
- [ ] **Auditoria Técnica**: validar HTML, links, responsividade, performance
- [ ] Corrigir qualquer inconsistência encontrada
- [ ] Git add + commit + push
- [ ] Enviar mensagem no Telegram para Leandro
- [ ] NÃO fechar a sessão (aguardar feedback)
Critério: Zero erros + deploy + Leandro notificado

## Pontos de Decisão (precisa Leandro)
- M1: Quais são as 4 torres da QC02? São E/F + mais 2? Como nomear?
- M2: Preferência por alguma ferramenta 3D específica?
- M4: Referência visual para o parque? (Parque Barigui, Central Park, etc.)
- M6: Música/narração no vídeo? Ou silencioso?

## Progresso
| Sessão | Status | Data | Score |
|--------|--------|------|-------|
| M1 | pendente | - | - |
| M2 | pendente | - | - |
| M3 | pendente | - | - |
| M4 | pendente | - | - |
| M5 | pendente | - | - |
| M6 | pendente | - | - |
| M7 | pendente | - | - |
