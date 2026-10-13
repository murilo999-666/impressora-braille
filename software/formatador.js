/*
 * formatador.js - diagrama um documento em paginas braille.
 *
 * Em braille nao existe tamanho de letra, negrito, cor nem fonte: a cela tem um tamanho so.
 * A estrutura do texto e mostrada pela POSICAO (centralizar, recuar, pular linha) e por sinais.
 * As regras abaixo vem das Normas Tecnicas para a Producao de Textos em Braille (MEC) e da
 * Grafia Braille para a Lingua Portuguesa:
 *   - a 1a linha da pagina e da paginacao: numero da pagina braille a direita; numero da
 *     pagina em tinta a partir da 3a cela, quando se conhece (Normas, 5.17);
 *   - paragrafo comeca na 3a cela e continua na 1a (5.19);
 *   - titulo centralizado, ou na margem com continuacao na 3a cela; sempre entre linhas em
 *     branco; nunca sozinho no fim da pagina: precisa caber com 2 linhas do texto (5.25);
 *   - item de lista e verso comecam na 1a cela e continuam na 3a (5.20 e 5.26);
 *   - italico, negrito e sublinhado viram o sinal (35) antes e depois do trecho (Grafia, 30);
 *   - titulo nao leva sinal de destaque: as linhas em branco ja destacam (Grafia, 46).
 *
 * O texto de entrada usa marcas simples (as mesmas do editor do programa):
 *   # Titulo        ## Subtitulo        - item        1. item        > verso
 *   **destaque** ou *destaque*          ---  separador      ===  nova pagina
 *   [[pagina 12]]  numero da pagina em tinta          linha em branco separa paragrafos
 *
 * Funciona no navegador (window.Formatador) e no Node (require).
 */
(function (raiz, fabrica) {
  if (typeof module === "object" && module.exports) module.exports = fabrica(require("./braille-pt.js"));
  else raiz.Formatador = fabrica(raiz.BraillePT);
})(typeof self !== "undefined" ? self : this, function (B) {
  "use strict";

  var PADRAO = {
    celas: 30,                 // celas por linha (a maquina aceita ate 33)
    linhasPagina: 23,          // linhas por folha (limite da maquina)
    numerarPaginas: true,      // reserva a 1a linha para a paginacao
    paginaTinta: true,         // mostra o numero da pagina do original, quando houver
    recuoParagrafo: 2,         // paragrafo comeca na 3a cela
    tituloCentralizado: true,  // falso: titulo na margem, continuacao na 3a cela
    sublinharTitulo: false,    // linha de pontos 25 embaixo do titulo principal
    destaques: true,           // mantem negrito/italico com o sinal 35
    capituloPaginaNova: false  // titulo principal sempre abre pagina nova
  };
  var SINAL_DESTAQUE = B.P(35), PONTOS_25 = B.P(25), HIFEN = B.P(36);

  function config(extra) {
    var c = {}, k;
    for (k in PADRAO) c[k] = PADRAO[k];
    if (extra) for (k in extra) if (extra[k] !== undefined) c[k] = extra[k];
    c.celas = Math.max(10, Math.min(40, Math.round(c.celas)));
    c.linhasPagina = Math.max(4, Math.min(29, Math.round(c.linhasPagina)));
    return c;
  }

  // ------------------------------------------------------------------ leitura das marcas
  /** "texto com **destaque**" -> [{txt, dest}] */
  function trechos(s) {
    var out = [], re = /\\([*_#>\\+=-])|\*\*([^*]+?)\*\*|\*([^*\s][^*]*?)\*|(^|[^\wÀ-ÿ])_([^_\s][^_]*?)_(?![\wÀ-ÿ])/g;
    var ult = 0, m, buf = "";
    function solta() { if (buf) { out.push({ txt: buf, dest: false }); buf = ""; } }
    while ((m = re.exec(s))) {
      buf += s.slice(ult, m.index);
      ult = re.lastIndex;
      if (m[1] !== undefined) { buf += m[1]; continue; }
      if (m[4] !== undefined && m[5] !== undefined) { buf += m[4]; solta(); out.push({ txt: m[5], dest: true }); continue; }
      solta();
      out.push({ txt: m[2] !== undefined ? m[2] : m[3], dest: true });
    }
    buf += s.slice(ult);
    solta();
    return out;
  }

  /** texto marcado -> lista de blocos */
  function analisa(texto) {
    var linhas = String(texto).replace(/\r\n?/g, "\n").replace(/\f/g, "\n===\n").split("\n");
    var blocos = [], par = null, brancos = 0;
    function fecha() { if (par) { blocos.push({ t: "par", runs: trechos(par.join(" ")) }); par = null; } }
    for (var i = 0; i < linhas.length; i++) {
      var bruta = linhas[i].replace(/\t/g, "  ").replace(/\s+$/, "");
      var l = bruta.trim(), m;
      if (!l) {
        fecha();
        if (++brancos === 2 && blocos.length && blocos[blocos.length - 1].t !== "branco") blocos.push({ t: "branco" });
        continue;
      }
      brancos = 0;
      if (/^={3,}$/.test(l)) { fecha(); blocos.push({ t: "quebra" }); continue; }
      if (/^(-{3,}|\*{3,}|_{3,})$/.test(l)) { fecha(); blocos.push({ t: "sep" }); continue; }
      if ((m = /^\[\[\s*p[aá]gina\s+(\d+)\s*\]\]$/i.exec(l))) { fecha(); blocos.push({ t: "pagtinta", n: +m[1] }); continue; }
      if ((m = /^(#{1,6})\s+(.*)$/.exec(l))) {
        fecha();
        blocos.push({ t: "titulo", nivel: Math.min(m[1].length, 2), runs: [{ txt: semMarcas(m[2].replace(/\s+#+$/, "")), dest: false }] });
        continue;
      }
      if ((m = /^>\s?(.*)$/.exec(l))) { fecha(); blocos.push({ t: "verso", runs: trechos(m[1]) }); continue; }
      var nivel = Math.min(3, Math.floor((bruta.length - bruta.replace(/^\s+/, "").length) / 2));
      if ((m = /^[-*+•]\s+(.*)$/.exec(l))) { fecha(); blocos.push({ t: "item", nivel: nivel, marca: "-", runs: trechos(m[1]) }); continue; }
      if ((m = /^(\d{1,3}[.)]|[a-zA-Z]\))\s+(.*)$/.exec(l))) { fecha(); blocos.push({ t: "item", nivel: nivel, marca: m[1], runs: trechos(m[2]) }); continue; }
      if (!par) par = [];
      par.push(l);
    }
    fecha();
    while (blocos.length && blocos[blocos.length - 1].t === "branco") blocos.pop();
    return blocos;
  }
  function semMarcas(s) { return trechos(s).map(function (r) { return r.txt; }).join(""); }

  // ------------------------------------------------------------------ bloco -> celas
  /** junta os trechos de um bloco: { cel: [], orig: [], pontos: [codigos do texto] } */
  function celasDoBloco(runs, usaDestaque, prefixo) {
    var cel = [], orig = [], pontos = [], avisos = [];
    function poeTexto(txt, dest) {
      txt = txt.normalize("NFC").replace(/\u00BA/g, "o").replace(/\u00AA/g, "a");
      var cps = Array.from(txt), base = pontos.length;
      var tr = B.traduz(txt);
      var c = tr.celas.map(function (x) { return x < 0 ? 0 : x; });
      var o = tr.origem.map(function (x) { return base + x; });
      avisos = avisos.concat(tr.avisos);
      if (dest && usaDestaque) {
        var a = 0, b = c.length - 1;
        while (a <= b && c[a] === 0) a++;
        while (b >= a && c[b] === 0) b--;
        if (a <= b) { c.splice(b + 1, 0, SINAL_DESTAQUE); o.splice(b + 1, 0, o[b]); c.splice(a, 0, SINAL_DESTAQUE); o.splice(a, 0, o[a]); }
      }
      cel = cel.concat(c); orig = orig.concat(o); pontos = pontos.concat(cps);
    }
    if (prefixo) poeTexto(prefixo + " ", false);
    runs.forEach(function (r) { poeTexto(r.txt.replace(/\s+/g, " "), r.dest); });
    return { cel: cel, orig: orig, pontos: pontos, avisos: avisos };
  }

  /** quebra em linhas sem partir palavras. rec1 = recuo da 1a linha, rec2 = das demais. */
  function quebra(bl, larg, rec1, rec2) {
    var pal = [], at = null, i;
    for (i = 0; i < bl.cel.length; i++) {
      if (bl.cel[i] === 0) { at = null; continue; }
      if (!at) { at = { c: [], o: [] }; pal.push(at); }
      at.c.push(bl.cel[i]); at.o.push(bl.orig[i]);
    }
    var linhas = [], cur = null;
    function nova(rec) { cur = { celas: [], o: [], vazia: true }; for (var k = 0; k < rec; k++) cur.celas.push(0); }
    function fecha() { if (!cur.vazia) linhas.push(cur); nova(rec2); }
    nova(rec1);
    pal.forEach(function (w) {
      var c = w.c.slice(), o = w.o.slice();
      if (!cur.vazia && cur.celas.length + 1 + c.length > larg) fecha();
      if (!cur.vazia) cur.celas.push(0);
      while (c.length > larg - cur.celas.length) {            // palavra maior que a linha: parte com hifen
        var cabe = larg - cur.celas.length - 1;
        if (cabe < 1) { fecha(); continue; }
        cur.celas = cur.celas.concat(c.splice(0, cabe)); cur.o = cur.o.concat(o.splice(0, cabe)); cur.celas.push(HIFEN);
        cur.vazia = false; fecha();
      }
      cur.celas = cur.celas.concat(c); cur.o = cur.o.concat(o); cur.vazia = false;
    });
    if (!cur.vazia) linhas.push(cur);
    return linhas.map(function (l) {
      var tinta = "";
      if (l.o.length) tinta = bl.pontos.slice(Math.min.apply(null, l.o), Math.max.apply(null, l.o) + 1).join("");
      return { celas: l.celas, tinta: tinta };
    });
  }

  function centraliza(linha, larg) {
    var n = linha.celas.length, esq = Math.max(0, Math.floor((larg - n) / 2)), pad = [];
    for (var i = 0; i < esq; i++) pad.push(0);
    return { celas: pad.concat(linha.celas), tinta: linha.tinta };
  }

  /** numero -> celas (sinal de numero + algarismos) */
  function numero(n) { return B.traduz(String(n)).celas; }

  // ------------------------------------------------------------------ documento -> paginas
  /**
   * formata(blocos ou texto, cfg) -> { paginas: [{ numero, tinta, linhas: [{celas, tinta, tipo}] }],
   *                                    avisos: [], totais: { paginas, linhas, celas, pontos } }
   */
  function formata(entrada, extra) {
    var c = config(extra);
    var blocos = typeof entrada === "string" ? analisa(entrada) : entrada;
    var W = c.celas, util = c.linhasPagina - (c.numerarPaginas ? 1 : 0);
    var avisos = [], grupos = [], pagTinta = null;

    // 1) cada bloco vira um grupo de linhas com as suas regras de espacamento
    blocos.forEach(function (b, idx) {
      var bl, ls, g = { tipo: b.t, linhas: [], antes: false, depois: false, junto: 0, novaPagina: false, pagTinta: pagTinta };
      if (b.t === "pagtinta") { pagTinta = b.n; return; }
      if (b.t === "quebra") { g.novaPagina = true; grupos.push(g); return; }
      if (b.t === "branco") { g.linhas = [{ celas: [], tinta: "" }]; grupos.push(g); return; }
      if (b.t === "sep") {
        var n = Math.min(18, W - 6), tr = [];
        for (var k = 0; k < n; k++) tr.push(PONTOS_25);
        g.linhas = [centraliza({ celas: tr, tinta: "" }, W)]; g.antes = g.depois = true; grupos.push(g); return;
      }
      if (b.t === "titulo") {
        bl = celasDoBloco(b.runs, false);
        if (b.nivel === 1 && c.tituloCentralizado) {
          ls = quebra(bl, Math.max(10, W - 6), 0, 0);
          var maior = ls.reduce(function (m, l) { return Math.max(m, l.celas.length); }, 0);
          g.linhas = ls.map(function (l) { return centraliza(l, W); });
          if (c.sublinharTitulo) {
            var su = [];
            for (var q = 0; q < maior; q++) su.push(PONTOS_25);
            g.linhas.push(centraliza({ celas: su, tinta: "" }, W));
          }
        } else g.linhas = quebra(bl, W, 0, 2);
        g.antes = g.depois = true; g.junto = 2;
        g.novaPagina = b.nivel === 1 && c.capituloPaginaNova && grupos.some(function (x) { return x.linhas.length; });
      } else if (b.t === "item") {
        var rec = 2 * (b.nivel || 0);
        bl = celasDoBloco(b.runs, c.destaques, b.marca === "-" ? "-" : b.marca);
        g.linhas = quebra(bl, W, rec, rec + 2);
      } else if (b.t === "verso") {
        bl = celasDoBloco(b.runs, c.destaques);
        g.linhas = quebra(bl, W, 0, 2);
      } else {
        bl = celasDoBloco(b.runs, c.destaques);
        g.linhas = quebra(bl, W, Math.min(c.recuoParagrafo, W - 4), 0);
      }
      if (bl) avisos = avisos.concat(bl.avisos);
      if (g.linhas.length) grupos.push(g);
    });

    // 2) distribui nas paginas
    var paginas = [], pag = null;
    function abre(tinta) { pag = { numero: paginas.length + 1, tinta: tinta, linhas: [] }; paginas.push(pag); }
    function cheia() { return pag.linhas.length >= util; }
    function ultimaEmBranco() { return !pag.linhas.length || !pag.linhas[pag.linhas.length - 1].celas.length; }
    function poe(linha, tipo, tinta) {
      if (!pag || cheia()) abre(tinta);
      if (!linha.celas.length && !pag.linhas.length) return;       // pagina nao comeca com linha em branco
      pag.linhas.push({ celas: linha.celas, tinta: linha.tinta, tipo: tipo });
    }
    grupos.forEach(function (g, gi) {
      if (g.novaPagina) { if (pag && pag.linhas.length) abre(g.pagTinta); if (g.tipo === "quebra") return; }
      if (!pag) abre(g.pagTinta);
      if (g.tipo === "branco") { if (!ultimaEmBranco()) poe({ celas: [], tinta: "" }, "branco", g.pagTinta); return; }
      var precisaAntes = g.antes && !ultimaEmBranco() ? 1 : 0;
      if (g.junto) {                                              // titulo: so fica se couber com 2 linhas do texto
        var prox = 0;
        for (var j = gi + 1; j < grupos.length && prox < g.junto; j++) {
          if (grupos[j].tipo === "quebra" || grupos[j].novaPagina) break;
          if (grupos[j].tipo !== "branco") prox += grupos[j].linhas.length;
        }
        var precisa = precisaAntes + g.linhas.length + 1 + Math.min(g.junto, prox);
        if (pag.linhas.length && pag.linhas.length + precisa > util && precisa <= util) { abre(g.pagTinta); precisaAntes = 0; }
      }
      if (precisaAntes && !cheia()) poe({ celas: [], tinta: "" }, "branco", g.pagTinta);
      g.linhas.forEach(function (l) { poe(l, g.tipo, g.pagTinta); });
      if (g.depois && !cheia()) poe({ celas: [], tinta: "" }, "branco", g.pagTinta);
    });
    if (!paginas.length) abre(null);

    // 3) tira brancos do fim e escreve a linha de paginacao
    var tot = { paginas: paginas.length, linhas: 0, celas: 0, pontos: 0 };
    paginas.forEach(function (p) {
      while (p.linhas.length && !p.linhas[p.linhas.length - 1].celas.length) p.linhas.pop();
      if (c.numerarPaginas) {
        var cab = [], nb = numero(p.numero), k;
        for (k = 0; k < W; k++) cab.push(0);
        for (k = 0; k < nb.length; k++) cab[W - nb.length + k] = nb[k];
        var txt = "página " + p.numero;
        if (c.paginaTinta && p.tinta != null) {
          var nt = numero(p.tinta);
          if (2 + nt.length + 2 <= W - nb.length) { for (k = 0; k < nt.length; k++) cab[2 + k] = nt[k]; txt += " (original: " + p.tinta + ")"; }
        }
        p.linhas.unshift({ celas: cab, tinta: txt, tipo: "pag" });
      }
      p.linhas.forEach(function (l) {
        while (l.celas.length && l.celas[l.celas.length - 1] === 0) l.celas.pop();
        if (l.celas.length > W) avisos.push("linha com mais de " + W + " celas");
        tot.linhas++; tot.celas += l.celas.length;
        l.celas.forEach(function (x) { for (var b2 = 0; b2 < 6; b2++) if (x & (1 << b2)) tot.pontos++; });
      });
    });
    var unicos = [];
    avisos.forEach(function (a) { if (unicos.indexOf(a) < 0) unicos.push(a); });
    return { paginas: paginas, avisos: unicos, totais: tot, config: c };
  }

  // ------------------------------------------------------------------ exportacao
  // Braille ASCII (formato .brf, lido por impressoras braille comerciais e programas como o Braille Facil)
  var ASCII = " A1B'K2L@CIF/MSP\"E3H9O6R^DJG>NTQ,*5<-U8V.%[$+X!&;:4\\0Z7(_?W]#Y)=";

  function paraBRF(paginas) {
    return paginas.map(function (p) {
      return p.linhas.map(function (l) { return l.celas.map(function (x) { return ASCII.charAt(x); }).join(""); }).join("\r\n");
    }).join("\r\n\f");
  }
  function paraUnicode(paginas) {
    return paginas.map(function (p) {
      return p.linhas.map(function (l) { return B.paraUnicode(l.celas); }).join("\n");
    }).join("\n\f\n");
  }
  /** texto .brf -> paginas (para imprimir um arquivo braille ja pronto) */
  function deBRF(txt, extra) {
    var c = config(extra);
    var pags = String(txt).replace(/\r/g, "").split("\f").map(function (bloco, i) {
      var ls = bloco.replace(/^\n+|\n+$/g, "").split("\n");
      return { numero: i + 1, tinta: null, linhas: ls.map(function (l) {
        return { tipo: "brf", tinta: "", celas: Array.from(l.toUpperCase()).map(function (ch) { var k = ASCII.indexOf(ch); return k < 0 ? 0 : k; }) };
      }) };
    }).filter(function (p) { return p.linhas.some(function (l) { return l.celas.length; }); });
    pags.forEach(function (p, i) { p.numero = i + 1; });
    return { paginas: pags, avisos: [], totais: { paginas: pags.length }, config: c };
  }

  return { PADRAO: PADRAO, config: config, analisa: analisa, trechos: trechos, formata: formata,
           paraBRF: paraBRF, paraUnicode: paraUnicode, deBRF: deBRF, ASCII: ASCII };
});
