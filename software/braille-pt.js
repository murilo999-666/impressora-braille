/*
 * braille-pt.js - texto em portugues -> celas braille (Grau 1, integral)
 * Segue a Grafia Braille para a Lingua Portuguesa (MEC, 3a ed., 2018).
 *
 * Cada cela e um numero de 0 a 63: bit 0 = ponto 1, bit 1 = ponto 2, ... bit 5 = ponto 6.
 *      1 o o 4
 *      2 o o 5
 *      3 o o 6
 * Funciona no navegador (window.BraillePT) e no Node (require).
 */
(function (raiz, fabrica) {
  if (typeof module === "object" && module.exports) module.exports = fabrica();
  else raiz.BraillePT = fabrica();
})(typeof self !== "undefined" ? self : this, function () {
  "use strict";

  /** "1245" -> mascara de bits */
  function P(pontos) {
    var m = 0;
    String(pontos).split("").forEach(function (d) { m |= 1 << (parseInt(d, 10) - 1); });
    return m;
  }

  var LETRAS = {
    a: P(1), b: P(12), c: P(14), d: P(145), e: P(15), f: P(124), g: P(1245), h: P(125), i: P(24), j: P(245),
    k: P(13), l: P(123), m: P(134), n: P(1345), o: P(135), p: P(1234), q: P(12345), r: P(1235), s: P(234),
    t: P(2345), u: P(136), v: P(1236), w: P(2456), x: P(1346), y: P(13456), z: P(1356),
    "ç": P(12346), "é": P(123456), "á": P(12356), "è": P(2346), "ú": P(23456),
    "â": P(16), "ê": P(126), "ì": P(146), "ô": P(1456), "ù": P(156), "à": P(1246), "ï": P(12456),
    "ü": P(1256), "õ": P(246), "í": P(34), "ã": P(345), "ó": P(346),
    "î": P(146), "û": P(156), "ñ": P(12456), "ò": P(346), "ä": P(345), "ö": P(246), "ë": P(1246)
  };

  var DIGITOS = { "1": P(1), "2": P(12), "3": P(14), "4": P(145), "5": P(15), "6": P(124), "7": P(1245),
                  "8": P(125), "9": P(24), "0": P(245) };

  var SINAL_NUMERO = P(3456);
  var SINAL_MAIUSCULA = P(46);
  var SINAL_LETRA = P(5);      // separa numero de uma letra a-j que venha colada
  var ESPACO = 0;

  // pontuacao e sinais: cada entrada e uma lista de celas
  var SINAIS = {
    ",": [P(2)], ";": [P(23)], ":": [P(25)], ".": [P(3)], "?": [P(26)], "!": [P(235)],
    "-": [P(36)], "–": [P(36), P(36)], "—": [P(36), P(36)], "…": [P(3), P(3), P(3)],
    '"': [P(236)], "“": [P(236)], "”": [P(236)], "«": [P(236)], "»": [P(236)],
    "'": [P(3)], "‘": [P(3)], "’": [P(3)],
    "(": [P(126), P(3)], ")": [P(6), P(345)], "[": [P(12356), P(3)], "]": [P(6), P(23456)],
    "*": [P(35)], "/": [P(6), P(2)], "$": [P(56)], "%": [P(456), P(356)], "&": [P(12346)], "@": [P(156)],
    "+": [P(235)], "=": [P(2356)], "×": [P(236)], "÷": [P(256)], "§": [P(234), P(234)],
    "°": [P(356)], "_": [P(46), P(36)], "#": [P(3456), P(13)]
  };

  function ehLetra(c) { return Object.prototype.hasOwnProperty.call(LETRAS, c.toLowerCase()); }
  function ehMaiuscula(c) { return ehLetra(c) && c !== c.toLowerCase() && c === c.toUpperCase(); }
  function ehDigito(c) { return c >= "0" && c <= "9"; }

  /**
   * Traduz um texto. Devolve { celas, origem, avisos }:
   *   celas  = lista de mascaras (0..63); "\n" do texto vira o marcador -1 (quebra de paragrafo)
   *   origem = para cada cela, o indice do caractere do texto que a gerou
   *   avisos = caracteres que nao tem cela definida (foram trocados por espaco)
   * opcoes.caixaAltaLonga = false desliga a regra das mais de tres palavras em maiusculas
   * (e assim que o firmware traduz quando recebe texto direto).
   */
  function traduz(texto, opcoes) {
    var regraLonga = !(opcoes && opcoes.caixaAltaLonga === false);
    texto = String(texto).normalize("NFC").replace(/\r\n?/g, "\n").replace(/\t/g, " ")
      .replace(/º/g, "o").replace(/ª/g, "a");
    var cs = Array.from(texto);
    var n = cs.length;

    // 1) palavras (sequencias de letras) e quais sao inteiras em maiusculas
    var palavras = [];           // {ini, fim, caixaAlta}
    for (var i = 0; i < n;) {
      if (ehLetra(cs[i])) {
        var j = i;
        var todas = true;
        while (j < n && ehLetra(cs[j])) { if (!ehMaiuscula(cs[j])) todas = false; j++; }
        palavras.push({ ini: i, fim: j, caixaAlta: todas && (j - i) >= 2 });
        i = j;
      } else i++;
    }
    // 2) sequencias de palavras em caixa alta. Mais de tres seguidas: (25)(46)(46) antes da
    //    primeira e (46)(46) antes da ultima. Ate tres: (46)(46) antes de cada uma.
    var prefixo = {};            // indice do caractere inicial -> lista de celas
    for (var a = 0; a < palavras.length;) {
      if (!palavras[a].caixaAlta) { a++; continue; }
      var b = a;
      while (b + 1 < palavras.length && palavras[b + 1].caixaAlta &&
             soEspacos(cs, palavras[b].fim, palavras[b + 1].ini)) b++;
      var qtd = b - a + 1;
      if (qtd > 3 && regraLonga) {
        prefixo[palavras[a].ini] = [P(25), SINAL_MAIUSCULA, SINAL_MAIUSCULA];
        prefixo[palavras[b].ini] = [SINAL_MAIUSCULA, SINAL_MAIUSCULA];
        for (var k = a + 1; k < b; k++) prefixo[palavras[k].ini] = [];
      } else {
        for (var k2 = a; k2 <= b; k2++) prefixo[palavras[k2].ini] = [SINAL_MAIUSCULA, SINAL_MAIUSCULA];
      }
      a = b + 1;
    }
    var emCaixaAlta = new Array(n).fill(false);
    palavras.forEach(function (p) { if (p.caixaAlta) for (var q = p.ini; q < p.fim; q++) emCaixaAlta[q] = true; });

    // 3) gera as celas
    var celas = [], origem = [], avisos = [];
    var numero = false;          // dentro de um numero (sinal de numero ja emitido)
    function poe(c, idx) { celas.push(c); origem.push(idx); }
    for (var x = 0; x < n; x++) {
      var ch = cs[x];
      if (ch === "\n") { poe(-1, x); numero = false; continue; }
      if (ch === " " || ch === " ") { poe(ESPACO, x); numero = false; continue; }
      if (ehDigito(ch)) {
        if (!numero) { poe(SINAL_NUMERO, x); numero = true; }
        poe(DIGITOS[ch], x);
        continue;
      }
      if (numero && (ch === "," || ch === ".") && x + 1 < n && ehDigito(cs[x + 1])) {
        poe(ch === "," ? P(2) : P(3), x);          // virgula decimal / ponto de milhar
        continue;
      }
      if (ehLetra(ch)) {
        var min = ch.toLowerCase();
        if (numero && min >= "a" && min <= "j" && min.length === 1) poe(SINAL_LETRA, x);
        numero = false;
        if (prefixo[x]) prefixo[x].forEach(function (c) { poe(c, x); });
        else if (ehMaiuscula(ch) && !emCaixaAlta[x]) poe(SINAL_MAIUSCULA, x);
        poe(LETRAS[min], x);
        continue;
      }
      numero = false;
      if (Object.prototype.hasOwnProperty.call(SINAIS, ch)) {
        SINAIS[ch].forEach(function (c) { poe(c, x); });
        continue;
      }
      avisos.push(ch);
      poe(ESPACO, x);
    }
    return { celas: celas, origem: origem, avisos: avisos };
  }

  function soEspacos(cs, de, ate) {
    if (ate <= de) return false;
    for (var i = de; i < ate; i++) if (cs[i] !== " ") return false;
    return true;
  }

  /**
   * Quebra as celas em linhas de ate `largura` celas, sem partir palavras (so parte a
   * palavra que sozinha nao cabe na linha). `recuo` = celas em branco no inicio de cada
   * paragrafo (o padrao em braille e 2: o texto comeca na 3a cela).
   */
  function quebra(celas, largura, recuo) {
    recuo = recuo || 0;
    var linhas = [];
    var paragrafos = [[]];
    celas.forEach(function (c) { if (c === -1) paragrafos.push([]); else paragrafos[paragrafos.length - 1].push(c); });
    paragrafos.forEach(function (par) {
      // separa em palavras (sequencias sem espaco)
      var pal = [], atual = [];
      par.forEach(function (c) { if (c === ESPACO) { if (atual.length) pal.push(atual); atual = []; } else atual.push(c); });
      if (atual.length) pal.push(atual);
      if (!pal.length) { linhas.push([]); return; }
      var linha = [];
      for (var r = 0; r < recuo; r++) linha.push(ESPACO);
      var vazia = true;
      pal.forEach(function (w) {
        var precisa = (vazia ? 0 : 1) + w.length;
        if (linha.length + precisa > largura && !vazia) { linhas.push(linha); linha = []; vazia = true; }
        if (!vazia) linha.push(ESPACO);
        while (w.length > largura - linha.length) {          // palavra maior que a linha: parte com hifen
          var cabe = largura - linha.length - 1;
          if (cabe < 1) { linhas.push(linha); linha = []; continue; }
          linha = linha.concat(w.slice(0, cabe)); linha.push(P(36));
          linhas.push(linha); linha = []; w = w.slice(cabe);
        }
        linha = linha.concat(w); vazia = false;
      });
      linhas.push(linha);
    });
    return linhas;
  }

  /** celas -> caracteres Unicode braille (U+2800...) para mostrar na tela */
  function paraUnicode(celas) {
    return celas.map(function (c) { return c < 0 ? "\n" : String.fromCharCode(0x2800 + c); }).join("");
  }

  /** mascara -> lista de pontos, ex.: 0b001011 -> [1, 2, 4] */
  function pontos(cela) {
    var r = [];
    for (var i = 0; i < 6; i++) if (cela & (1 << i)) r.push(i + 1);
    return r;
  }

  /** linha de celas -> "0a1f..." (2 digitos hexadecimais por cela), formato do comando $C do firmware */
  function paraHex(linha) {
    return linha.map(function (c) { return (c < 16 ? "0" : "") + c.toString(16); }).join("");
  }

  return { traduz: traduz, quebra: quebra, paraUnicode: paraUnicode, pontos: pontos, paraHex: paraHex,
           P: P, LETRAS: LETRAS, DIGITOS: DIGITOS, SINAIS: SINAIS,
           SINAL_NUMERO: SINAL_NUMERO, SINAL_MAIUSCULA: SINAL_MAIUSCULA, SINAL_LETRA: SINAL_LETRA };
});
