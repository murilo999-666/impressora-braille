/*
 * leiaute.js - transforma linhas de celas braille em pontos (mm) na folha e na sequencia
 * de movimentos da maquina. E a MESMA conta que o firmware faz; os valores padrao
 * abaixo tem de bater com os do firmware (firmware/ImpressoraBraille/config.h).
 *
 * Coordenadas na FOLHA, do lado da leitura: u = mm a partir da borda esquerda,
 * v = mm a partir da borda de cima. Como a maquina marca de cima para baixo e a folha
 * entra com o topo na frente, u cresce junto com o X da maquina (nao ha espelhamento).
 */
(function (raiz, fabrica) {
  if (typeof module === "object" && module.exports) module.exports = fabrica();
  else raiz.Leiaute = fabrica();
})(typeof self !== "undefined" ? self : this, function () {
  "use strict";

  var PADRAO = {
    papelLargura: 210, papelAltura: 297,
    ponto: 2.5,            // entre pontos da mesma cela (horizontal e vertical)
    cela: 6.0,             // entre celas
    linha: 10.0,           // entre linhas
    margemEsq: 20.0,       // da borda esquerda ate a 1a coluna de pontos
    margemTopo: 12.0,      // da borda de cima ate a 1a fileira de pontos
    celasPorLinha: 30,
    linhasPorPagina: 23,
    distRoletePuncao: 48.0,  // o papel so e empurrado ate a borda de tras chegar no rolete
    folgaFim: 4.0,
    xPapel0: 54.0,         // X da maquina na borda esquerda da folha
    xMin: 62.0, xMax: 258.0,
    vaiEVem: true          // fileiras alternam o sentido (mais rapido)
  };

  function config(extra) {
    var c = {};
    Object.keys(PADRAO).forEach(function (k) { c[k] = PADRAO[k]; });
    if (extra) Object.keys(extra).forEach(function (k) { c[k] = extra[k]; });
    return c;
  }

  /** maior numero de linhas que cabe na folha com esta configuracao */
  function linhasQueCabem(c) {
    var vMax = c.papelAltura - c.distRoletePuncao - c.folgaFim;
    return Math.floor((vMax - c.margemTopo - 2 * c.ponto) / c.linha) + 1;
  }

  /** maior numero de celas por linha que o curso do carro permite */
  function celasQueCabem(c) {
    var u0 = Math.max(c.margemEsq, c.xMin - c.xPapel0);
    var uMax = Math.min(c.papelLargura - 4, c.xMax - c.xPapel0);
    return Math.floor((uMax - u0 - c.ponto) / c.cela) + 1;
  }

  /**
   * Pontos de uma pagina. linhas = lista de linhas (cada uma, lista de celas 0..63).
   * Devolve { pontos: [{u, v, linha, cela, ponto}], fileiras: [{v, us: [...]}] } onde
   * `fileiras` ja esta na ordem em que a maquina marca (3 fileiras por linha de texto).
   */
  function pagina(linhas, c) {
    c = config(c);
    var pts = [], fileiras = [];
    var sentido = 1;
    linhas.forEach(function (lin, li) {
      for (var f = 0; f < 3; f++) {
        var v = c.margemTopo + li * c.linha + f * c.ponto;
        var us = [];
        lin.forEach(function (cela, ci) {
          if (cela <= 0) return;
          var u = c.margemEsq + ci * c.cela;
          if (cela & (1 << f)) { us.push(u); pts.push({ u: u, v: v, linha: li, cela: ci, ponto: f + 1 }); }
          if (cela & (1 << (f + 3))) { us.push(u + c.ponto); pts.push({ u: u + c.ponto, v: v, linha: li, cela: ci, ponto: f + 4 }); }
        });
        us.sort(function (a, b) { return a - b; });
        if (!us.length) { fileiras.push({ v: v, us: [] }); continue; }
        if (c.vaiEVem && sentido < 0) us.reverse();
        if (c.vaiEVem) sentido = -sentido;
        fileiras.push({ v: v, us: us });
      }
    });
    return { pontos: pts, fileiras: fileiras };
  }

  /** separa as linhas em paginas */
  function paginas(linhas, c) {
    c = config(c);
    var n = Math.min(c.linhasPorPagina, linhasQueCabem(c));
    var r = [];
    for (var i = 0; i < linhas.length; i += n) r.push(linhas.slice(i, i + n));
    if (!r.length) r.push([]);
    return r;
  }

  /** estimativa de tempo (s) para marcar uma pagina, com os mesmos parametros do firmware */
  function tempo(pag, c, mov) {
    mov = mov || {};
    var vmax = mov.vmax || 120, acel = mov.acel || 3000, tOn = mov.tOn || 0.025, tOff = mov.tOff || 0.030;
    var vY = mov.vY || 30;
    function t(d) {
      d = Math.abs(d); if (d <= 0) return 0;
      var dAcel = vmax * vmax / acel;
      return d < dAcel ? 2 * Math.sqrt(d / acel) : d / vmax + vmax / acel;
    }
    var total = 0, x = 8, v = 0;       // parte do home (u = 8 mm)
    pag.fileiras.forEach(function (f) {
      total += Math.abs(f.v - v) / vY; v = f.v;
      f.us.forEach(function (u) { total += t(u - x) + tOn + tOff; x = u; });
    });
    return total;
  }

  return { PADRAO: PADRAO, config: config, pagina: pagina, paginas: paginas,
           linhasQueCabem: linhasQueCabem, celasQueCabem: celasQueCabem, tempo: tempo };
});
