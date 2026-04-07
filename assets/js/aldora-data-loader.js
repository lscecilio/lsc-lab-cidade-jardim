/**
 * AL'DORA City — Data Loader
 * Carrega aldora-data.json e expõe o objeto global ALDORA com helpers.
 * Compatível com qualquer browser (sem módulos ES, sem async/await).
 */
(function () {
  'use strict';

  var ALDORA = {
    _data: null,
    _ready: false,

    // --- Helpers de formatação ---

    formatCurrency: function (value) {
      if (value == null || isNaN(value)) return '—';
      var parts = Number(value).toFixed(0).split('');
      var formatted = '';
      var count = 0;
      for (var i = parts.length - 1; i >= 0; i--) {
        if (count > 0 && count % 3 === 0) formatted = '.' + formatted;
        formatted = parts[i] + formatted;
        count++;
      }
      return 'R$' + formatted;
    },

    formatArea: function (value) {
      if (value == null || isNaN(value)) return '—';
      var parts = Number(value).toFixed(0).split('');
      var formatted = '';
      var count = 0;
      for (var i = parts.length - 1; i >= 0; i--) {
        if (count > 0 && count % 3 === 0) formatted = '.' + formatted;
        formatted = parts[i] + formatted;
        count++;
      }
      return formatted + ' m²';
    },

    // --- Lookups ---

    getQuadra: function (id) {
      if (!ALDORA._data) return null;
      var quadras = ALDORA._data.ativo.quadras;
      for (var i = 0; i < quadras.length; i++) {
        if (quadras[i].id === id) return quadras[i];
      }
      return null;
    },

    getTipologia: function (codigo) {
      if (!ALDORA._data) return null;
      var tipos = ALDORA._data.tipologias;
      for (var i = 0; i < tipos.length; i++) {
        if (tipos[i].codigo === codigo) return tipos[i];
      }
      return null;
    },

    getEmpreendimento: function (id) {
      if (!ALDORA._data) return null;
      var emps = ALDORA._data.empreendimentos;
      for (var i = 0; i < emps.length; i++) {
        if (emps[i].id === id) return emps[i];
      }
      return null;
    }
  };

  // --- Resolve caminho relativo do JSON ---

  function resolveJsonPath() {
    var scripts = document.getElementsByTagName('script');
    for (var i = 0; i < scripts.length; i++) {
      var src = scripts[i].getAttribute('src') || '';
      if (src.indexOf('aldora-data-loader') !== -1) {
        return src.replace(/aldora-data-loader\.js.*$/, 'aldora-data.json');
      }
    }
    return 'assets/js/aldora-data.json';
  }

  // --- Carrega dados via fetch (com fallback XMLHttpRequest) ---

  function loadData() {
    var url = resolveJsonPath();

    if (typeof fetch === 'function') {
      fetch(url).then(function (res) {
        if (!res.ok) throw new Error('HTTP ' + res.status);
        return res.json();
      }).then(onDataLoaded).catch(function (err) {
        console.error('[ALDORA] Fetch falhou, tentando XMLHttpRequest:', err);
        loadViaXHR(url);
      });
    } else {
      loadViaXHR(url);
    }
  }

  function loadViaXHR(url) {
    var xhr = new XMLHttpRequest();
    xhr.open('GET', url, true);
    xhr.onreadystatechange = function () {
      if (xhr.readyState === 4) {
        if (xhr.status === 200) {
          try {
            onDataLoaded(JSON.parse(xhr.responseText));
          } catch (e) {
            console.error('[ALDORA] Erro ao parsear JSON:', e);
          }
        } else {
          console.error('[ALDORA] XHR falhou:', xhr.status);
        }
      }
    };
    xhr.send();
  }

  function onDataLoaded(data) {
    ALDORA._data = data;
    ALDORA._ready = true;

    // Expõe seções de primeiro nível como atalhos
    var keys = ['projeto', 'ativo', 'empreendimentos', 'tipologias', 'gates', 'mercado'];
    for (var i = 0; i < keys.length; i++) {
      if (data[keys[i]]) ALDORA[keys[i]] = data[keys[i]];
    }

    // Dispara evento custom
    var evt;
    if (typeof CustomEvent === 'function') {
      evt = new CustomEvent('aldora-data-ready', { detail: data });
    } else {
      evt = document.createEvent('CustomEvent');
      evt.initCustomEvent('aldora-data-ready', true, true, data);
    }
    document.dispatchEvent(evt);

    console.log('[ALDORA] Dados carregados —', data.projeto.nome);
  }

  // Expõe globalmente
  window.ALDORA = ALDORA;

  // Inicia carregamento quando DOM estiver pronto
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', loadData);
  } else {
    loadData();
  }
})();
