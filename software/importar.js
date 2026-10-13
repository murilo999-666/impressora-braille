/*
 * importar.js - le arquivos (.txt .md .docx .odt .html .pdf) e devolve o texto com as marcas
 * que o formatador entende (# titulo, - item, **destaque**, [[pagina N]] ...).
 *
 * Braille nao tem tamanho de letra. Por isso o que no original e "letra grande" ou estilo de
 * titulo vira TITULO (centralizado, entre linhas em branco), e negrito/italico viram destaque.
 *
 * Sem bibliotecas para .docx/.odt (o proprio navegador descompacta o zip). Para .pdf usa o pdf.js
 * (software/lib). Funciona no navegador (window.Importar) e no Node 18+ (require).
 */
(function (raiz, fabrica) {
  if (typeof module === "object" && module.exports) module.exports = fabrica();
  else raiz.Importar = fabrica();
})(typeof self !== "undefined" ? self : this, function () {
  "use strict";

  // ------------------------------------------------------------------ utilidades
  /** protege caracteres que seriam lidos como marca */
  function escapa(s) { return String(s).replace(/([*_\\])/g, "\\$1"); }
  function escapaInicio(s) { return s.replace(/^(\s*)(#{1,6}\s|[-+>]\s|={3,}$|-{3,}$)/, "$1\\$2"); }
  function limpa(s) { return String(s).replace(/[  -​ 　]/g, " ").replace(/­/g, "").replace(/[ \t]+/g, " ").trim(); }
  function entidades(s) {
    var mapa = { amp: "&", lt: "<", gt: ">", quot: '"', apos: "'", nbsp: " ", ndash: "–", mdash: "—", hellip: "…",
                 laquo: "«", raquo: "»", ordm: "º", ordf: "ª", deg: "°", ccedil: "ç", Ccedil: "Ç",
                 atilde: "ã", otilde: "õ", Atilde: "Ã", Otilde: "Õ", aacute: "á", eacute: "é", iacute: "í", oacute: "ó", uacute: "ú",
                 Aacute: "Á", Eacute: "É", Iacute: "Í", Oacute: "Ó", Uacute: "Ú", acirc: "â", ecirc: "ê", ocirc: "ô", Acirc: "Â",
                 Ecirc: "Ê", Ocirc: "Ô", agrave: "à", Agrave: "À", uuml: "ü", ldquo: "“", rdquo: "”", lsquo: "‘", rsquo: "’" };
    return s.replace(/&(#x?[0-9a-fA-F]+|\w+);/g, function (t, e) {
      if (e.charAt(0) === "#") { var n = e.charAt(1).toLowerCase() === "x" ? parseInt(e.slice(2), 16) : parseInt(e.slice(1), 10); return n ? String.fromCodePoint(n) : ""; }
      return Object.prototype.hasOwnProperty.call(mapa, e) ? mapa[e] : t;
    });
  }
  /** divide XML/HTML em { abre|fecha|texto } sem depender de DOMParser */
  function tokens(xml) {
    var re = /<!--[\s\S]*?-->|<!\[CDATA\[([\s\S]*?)\]\]>|<(\/?)([A-Za-z_][\w:.-]*)((?:"[^"]*"|'[^']*'|[^>"'])*?)(\/?)>|([^<]+)/g, m, out = [];
    while ((m = re.exec(xml))) {
      if (m[1] !== undefined) out.push({ texto: m[1] });
      else if (m[3]) {
        var attrs = {}, ra = /([\w:.-]+)\s*=\s*(?:"([^"]*)"|'([^']*)')/g, a;
        while ((a = ra.exec(m[4]))) attrs[a[1]] = entidades(a[2] !== undefined ? a[2] : a[3]);
        if (m[2]) out.push({ fecha: m[3] });
        else { out.push({ abre: m[3], attrs: attrs }); if (m[5]) out.push({ fecha: m[3] }); }
      } else if (m[6] !== undefined) out.push({ texto: entidades(m[6]) });
    }
    return out;
  }
  /** junta trechos vizinhos com o mesmo destaque e devolve texto marcado */
  function marca(runs) {
    var junt = [];
    runs.forEach(function (r) {
      if (!r.txt) return;
      var u = junt[junt.length - 1];
      if (u && u.dest === !!r.dest) u.txt += r.txt; else junt.push({ txt: r.txt, dest: !!r.dest });
    });
    return junt.map(function (r) {
      var t = escapa(r.txt);
      if (!r.dest || !t.trim()) return t;
      var a = /^\s*/.exec(t)[0], b = /\s*$/.exec(t)[0];
      return a + "**" + t.trim() + "**" + b;
    }).join("");
  }

  // ------------------------------------------------------------------ zip (docx, odt)
  async function descompacta(buffer) {
    var u8 = new Uint8Array(buffer), dv = new DataView(u8.buffer, u8.byteOffset, u8.byteLength);
    var fim = -1;
    for (var i = u8.length - 22; i >= Math.max(0, u8.length - 66000); i--) if (dv.getUint32(i, true) === 0x06054b50) { fim = i; break; }
    if (fim < 0) throw new Error("o arquivo não é um .docx/.odt válido (zip sem índice)");
    var n = dv.getUint16(fim + 10, true), pos = dv.getUint32(fim + 16, true), arqs = {}, td = new TextDecoder("utf-8");
    for (var k = 0; k < n; k++) {
      if (dv.getUint32(pos, true) !== 0x02014b50) break;
      var metodo = dv.getUint16(pos + 10, true), tamC = dv.getUint32(pos + 20, true);
      var ln = dv.getUint16(pos + 28, true), le = dv.getUint16(pos + 30, true), lc = dv.getUint16(pos + 32, true);
      var local = dv.getUint32(pos + 42, true), nome = td.decode(u8.subarray(pos + 46, pos + 46 + ln));
      var ini = local + 30 + dv.getUint16(local + 26, true) + dv.getUint16(local + 28, true);
      arqs[nome] = { metodo: metodo, dados: u8.subarray(ini, ini + tamC) };
      pos += 46 + ln + le + lc;
    }
    return {
      nomes: Object.keys(arqs),
      texto: async function (nome) {
        var a = arqs[nome];
        if (!a) return null;
        if (a.metodo === 0) return td.decode(a.dados);
        if (a.metodo !== 8) throw new Error("compressão não suportada no zip");
        var fluxo = new Blob([a.dados]).stream().pipeThrough(new DecompressionStream("deflate-raw"));
        return await new Response(fluxo).text();
      }
    };
  }

  // ------------------------------------------------------------------ .txt e .md
  function deTexto(txt) {
    txt = String(txt).replace(/^﻿/, "").replace(/\r\n?/g, "\n");
    var linhas = txt.split("\n"), naoVazias = linhas.filter(function (l) { return l.trim(); });
    if (!naoVazias.length) return "";
    var temBranco = /\n[ \t]*\n/.test(txt.trim());
    var longas = naoVazias.filter(function (l) { return l.length > 100; }).length;
    var umaPorParagrafo = !temBranco || longas > naoVazias.length * 0.3;      // texto colado do Word: cada linha e um paragrafo
    var out = [], primeira = true;
    linhas.forEach(function (l, i) {
      var t = limpa(l);
      if (!t) { out.push(""); return; }
      var prox = i + 1 < linhas.length ? linhas[i + 1].trim() : "";
      if (/^[-*•]\s+/.test(t) || /^(\d{1,3}[.)]|[a-zA-Z]\))\s+/.test(t)) { out.push(t.replace(/^[*•]/, "-")); primeira = false; return; }
      if (primeira && naoVazias.length > 1 && t.length <= 70 && !/[.;:,]$/.test(t) && (!prox || umaPorParagrafo)) { out.push("# " + escapa(t)); if (prox) out.push(""); primeira = false; return; }
      primeira = false;
      out.push(escapaInicio(escapa(t)));
      if (umaPorParagrafo) out.push("");
    });
    return out.join("\n").replace(/\n{4,}/g, "\n\n\n").trim() + "\n";
  }
  function deMarkdown(txt) {
    return String(txt).replace(/^﻿/, "").replace(/\r\n?/g, "\n")
      .replace(/```[\s\S]*?```/g, "").replace(/`([^`]*)`/g, "$1")
      .replace(/!\[([^\]]*)\]\([^)]*\)/g, "$1").replace(/\[([^\]]+)\]\([^)]*\)/g, "$1")
      .replace(/^\s*>\s?/gm, "").replace(/<[^>]+>/g, "");
  }

  // ------------------------------------------------------------------ .docx
  var ROMANOS = ["", "i", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix", "x", "xi", "xii", "xiii", "xiv", "xv", "xvi", "xvii", "xviii", "xix", "xx"];
  function marcador(fmt, n) {
    if (fmt === "decimal" || fmt === "decimalZero") return n + ".";
    if (fmt === "lowerLetter") return String.fromCharCode(96 + ((n - 1) % 26) + 1) + ")";
    if (fmt === "upperLetter") return String.fromCharCode(64 + ((n - 1) % 26) + 1) + ")";
    if (fmt === "lowerRoman" || fmt === "upperRoman") return n + ".";
    return "-";
  }
  function nivelDoEstilo(nome) {
    var m = /^(?:heading|t[ií]tulo|titre|cabe[cç]alho)\s*(\d)/i.exec(nome || "");
    if (m) return +m[1];
    if (/^(title|t[ií]tulo)$/i.test(nome || "")) return 1;
    if (/^(subtitle|subt[ií]tulo)$/i.test(nome || "")) return 2;
    return 0;
  }
  async function deDocx(buffer) {
    var zip = await descompacta(buffer);
    var doc = await zip.texto("word/document.xml");
    if (!doc) throw new Error("não achei o texto dentro do .docx");
    var estilos = {}, nums = {}, abst = {};
    var sx = await zip.texto("word/styles.xml");
    if (sx) {
      var at = null;
      tokens(sx).forEach(function (t) {
        if (t.abre === "w:style") at = estilos[t.attrs["w:styleId"]] = { nivel: 0, neg: false };
        else if (at && t.abre === "w:name") at.nivel = at.nivel || nivelDoEstilo(t.attrs["w:val"]);
        else if (at && t.abre === "w:outlineLvl") at.nivel = at.nivel || (+t.attrs["w:val"] < 9 ? +t.attrs["w:val"] + 1 : 0);
        else if (t.fecha === "w:style") at = null;
      });
    }
    var nx = await zip.texto("word/numbering.xml");
    if (nx) {
      var an = null, lv = null, nu = null;
      tokens(nx).forEach(function (t) {
        if (t.abre === "w:abstractNum") an = abst[t.attrs["w:abstractNumId"]] = {};
        else if (an && t.abre === "w:lvl") lv = an[t.attrs["w:ilvl"]] = { fmt: "bullet" };
        else if (lv && t.abre === "w:numFmt") lv.fmt = t.attrs["w:val"];
        else if (t.fecha === "w:abstractNum") { an = null; lv = null; }
        else if (t.abre === "w:num") nu = t.attrs["w:numId"];
        else if (nu && t.abre === "w:abstractNumId") nums[nu] = abst[t.attrs["w:val"]] || {};
        else if (t.fecha === "w:num") nu = null;
      });
    }
    var out = [], cont = {}, p = null, run = null, emPPr = false, emRPr = false, noTexto = false;
    var tabela = 0, celulas = null, celAtual = null, pagAntes = false;
    function ligado(t) { var v = t.attrs["w:val"]; return v === undefined || (v !== "0" && v !== "false" && v !== "none"); }
    function fechaPar() {
      var txt = limpa(p.runs.map(function (r) { return r.txt; }).join(""));
      if (tabela) { if (txt && celAtual) celAtual.push(txt); p = null; return; }
      if (p.quebraAntes || pagAntes) { out.push("==="); pagAntes = false; }
      if (!txt) { if (p.quebraDepois) pagAntes = true; else out.push(""); p = null; return; }
      var est = estilos[p.estilo] || {}, nivel = p.nivel || est.nivel || 0;
      var todoNeg = p.runs.filter(function (r) { return r.txt.trim(); }).every(function (r) { return r.dest; });
      if (!nivel && !p.numId && todoNeg && txt.length <= 80 && !/[.;,]$/.test(txt)) nivel = p.centro ? 1 : 2;
      if (nivel) out.push((nivel === 1 ? "# " : "## ") + escapa(txt), "");
      else if (p.numId && p.numId !== "0") {
        var def = (nums[p.numId] || {})[p.ilvl] || { fmt: "bullet" }, cs = cont[p.numId] = cont[p.numId] || {};
        cs[p.ilvl] = (cs[p.ilvl] || 0) + 1;
        Object.keys(cs).forEach(function (k) { if (+k > +p.ilvl) cs[k] = 0; });
        out.push(new Array(+p.ilvl * 2 + 1).join(" ") + marcador(def.fmt, cs[p.ilvl]) + " " + marca(p.runs).trim());
      } else out.push(escapaInicio(marca(p.runs).replace(/\s+/g, " ").trim()), "");
      if (p.quebraDepois) pagAntes = true;
      p = null;
    }
    tokens(doc).forEach(function (t) {
      if (t.abre === "w:tbl") tabela++;
      else if (t.fecha === "w:tbl") { tabela--; out.push(""); }
      else if (t.abre === "w:tr") celulas = [];
      else if (t.abre === "w:tc") celAtual = [];
      else if (t.fecha === "w:tc") { if (celulas && celAtual) celulas.push(celAtual.join(" ")); celAtual = null; }
      else if (t.fecha === "w:tr") { if (celulas && celulas.length) out.push(escapaInicio(escapa(celulas.join("; "))), ""); celulas = null; }
      else if (t.abre === "w:p") p = { runs: [], estilo: null, numId: null, ilvl: 0, centro: false, nivel: 0 };
      else if (t.fecha === "w:p") { if (p) fechaPar(); }
      else if (!p) return;
      else if (t.abre === "w:pPr") emPPr = true;
      else if (t.fecha === "w:pPr") emPPr = false;
      else if (emPPr) {
        if (t.abre === "w:pStyle") p.estilo = t.attrs["w:val"];
        else if (t.abre === "w:numId") p.numId = t.attrs["w:val"];
        else if (t.abre === "w:ilvl") p.ilvl = t.attrs["w:val"];
        else if (t.abre === "w:jc") p.centro = t.attrs["w:val"] === "center";
        else if (t.abre === "w:outlineLvl") p.nivel = +t.attrs["w:val"] < 9 ? +t.attrs["w:val"] + 1 : 0;
        else if (t.abre === "w:pageBreakBefore" && ligado(t)) p.quebraAntes = true;
      }
      else if (t.abre === "w:r") { run = { txt: "", dest: false }; p.runs.push(run); }
      else if (t.fecha === "w:r") run = null;
      else if (!run) return;
      else if (t.abre === "w:rPr") emRPr = true;
      else if (t.fecha === "w:rPr") emRPr = false;
      else if (emRPr) { if ((t.abre === "w:b" || t.abre === "w:i" || t.abre === "w:u") && ligado(t)) run.dest = true; }
      else if (t.abre === "w:t") noTexto = true;
      else if (t.fecha === "w:t") noTexto = false;
      else if (t.texto !== undefined && noTexto) run.txt += t.texto;
      else if (t.abre === "w:tab") run.txt += " ";
      else if (t.abre === "w:br" || t.abre === "w:cr") { if (t.attrs && t.attrs["w:type"] === "page") p.quebraDepois = true; else run.txt += " "; }
      else if (t.abre === "w:lastRenderedPageBreak") { /* quebra automatica do Word: ignorada */ }
    });
    return out.join("\n").replace(/\n{4,}/g, "\n\n\n").trim() + "\n";
  }

  // ------------------------------------------------------------------ .odt
  async function deOdt(buffer) {
    var zip = await descompacta(buffer);
    var xml = await zip.texto("content.xml");
    if (!xml) throw new Error("não achei o texto dentro do .odt");
    var est = {}, nomeEst = null, out = [], pilha = [], bloco = null, lista = 0, item = false;
    tokens(xml).forEach(function (t) {
      if (t.abre === "style:style") nomeEst = t.attrs["style:name"];
      else if (t.fecha === "style:style") nomeEst = null;
      else if (nomeEst && t.abre === "style:text-properties") {
        if (t.attrs["fo:font-weight"] === "bold" || t.attrs["fo:font-style"] === "italic" ||
            (t.attrs["style:text-underline-style"] && t.attrs["style:text-underline-style"] !== "none")) est[nomeEst] = true;
      }
      else if (t.abre === "text:list") lista++;
      else if (t.fecha === "text:list") lista--;
      else if (t.abre === "text:list-item") item = true;
      else if (t.abre === "text:h" || t.abre === "text:p") bloco = { titulo: t.abre === "text:h" ? +(t.attrs["text:outline-level"] || 1) : 0, runs: [], item: item && lista > 0, nivel: Math.max(0, lista - 1) };
      else if ((t.fecha === "text:h" || t.fecha === "text:p") && bloco) {
        var txt = limpa(bloco.runs.map(function (r) { return r.txt; }).join(""));
        if (!txt) out.push("");
        else if (bloco.titulo) out.push((bloco.titulo === 1 ? "# " : "## ") + escapa(txt), "");
        else if (bloco.item) out.push(new Array(bloco.nivel * 2 + 1).join(" ") + "- " + marca(bloco.runs).trim());
        else out.push(escapaInicio(marca(bloco.runs).replace(/\s+/g, " ").trim()), "");
        bloco = null; item = false; pilha = [];
      }
      else if (!bloco) return;
      else if (t.abre === "text:span") pilha.push(!!est[t.attrs["text:style-name"]]);
      else if (t.fecha === "text:span") pilha.pop();
      else if (t.abre === "text:s" || t.abre === "text:tab" || t.abre === "text:line-break") bloco.runs.push({ txt: " ", dest: false });
      else if (t.texto !== undefined) bloco.runs.push({ txt: t.texto, dest: pilha.some(Boolean) });
    });
    return out.join("\n").replace(/\n{4,}/g, "\n\n\n").trim() + "\n";
  }

  // ------------------------------------------------------------------ .html
  function deHtml(html) {
    html = String(html).replace(/<(script|style|head|svg|noscript)[\s\S]*?<\/\1>/gi, " ");
    var out = [], runs = [], dest = 0, tipo = "p", listas = [], ignora = 0;
    function fecha() {
      var txt = limpa(runs.map(function (r) { return r.txt; }).join(""));
      if (txt) {
        var m = marca(runs).replace(/\s+/g, " ").trim();
        if (tipo === "h1") out.push("# " + escapa(txt), "");
        else if (/^h[2-6]$/.test(tipo)) out.push("## " + escapa(txt), "");
        else if (tipo === "li") {
          var l = listas[listas.length - 1] || { ord: false, n: 0 };
          l.n++;
          out.push(new Array(Math.max(0, listas.length - 1) * 2 + 1).join(" ") + (l.ord ? l.n + "." : "-") + " " + m);
        } else out.push(escapaInicio(m), "");
      }
      runs = [];
    }
    tokens(html).forEach(function (t) {
      var tag = (t.abre || t.fecha || "").toLowerCase();
      if (t.texto !== undefined) { if (!ignora) runs.push({ txt: t.texto.replace(/\s+/g, " "), dest: dest > 0 }); return; }
      if (/^(b|strong|i|em|u|mark)$/.test(tag)) { dest += t.abre ? 1 : -1; if (dest < 0) dest = 0; return; }
      if (tag === "br") { if (t.abre) runs.push({ txt: " ", dest: false }); return; }
      if (tag === "ul" || tag === "ol") { fecha(); if (t.abre) listas.push({ ord: tag === "ol", n: 0 }); else { listas.pop(); out.push(""); } tipo = "p"; return; }
      if (/^(p|div|h[1-6]|li|tr|blockquote|section|article|header|footer|table|td|th|hr|title)$/.test(tag)) {
        if (tag === "td" || tag === "th") { if (t.fecha) runs.push({ txt: "; ", dest: false }); return; }
        fecha();
        if (t.abre) tipo = /^(h[1-6]|li)$/.test(tag) ? tag : "p"; else tipo = "p";
        if (tag === "hr" && t.abre) out.push("---", "");
      }
    });
    fecha();
    return out.join("\n").replace(/;\s*\n/g, "\n").replace(/\n{4,}/g, "\n\n\n").trim() + "\n";
  }

  // ------------------------------------------------------------------ .pdf (precisa do pdf.js)
  /** linhas = [{ pag, x, y, tam, txt, larg }] -> texto marcado. Separada para poder ser testada. */
  function linhasDoPdfParaTexto(linhas) {
    if (!linhas.length) return "";
    var pesos = {}, corpo = 0, maior = 0;
    linhas.forEach(function (l) { var k = Math.round(l.tam * 2) / 2; pesos[k] = (pesos[k] || 0) + l.txt.length; });
    Object.keys(pesos).forEach(function (k) { if (pesos[k] > maior) { maior = pesos[k]; corpo = +k; } });
    var doCorpo = linhas.filter(function (l) { return Math.abs(l.tam - corpo) < 0.6; });
    var esq = Math.min.apply(null, doCorpo.map(function (l) { return l.x; }));
    var dir = Math.max.apply(null, doCorpo.map(function (l) { return l.x + l.larg; }));
    var passos = [];
    for (var i = 1; i < doCorpo.length; i++) if (doCorpo[i].pag === doCorpo[i - 1].pag) { var d = doCorpo[i - 1].y - doCorpo[i].y; if (d > 0 && d < corpo * 3) passos.push(d); }
    passos.sort(function (a, b) { return a - b; });
    var passo = passos.length ? passos[Math.floor(passos.length / 2)] : corpo * 1.2;
    var out = [], par = "", ant = null, pagAtual = 0;
    function fecha() { if (par) { out.push(escapaInicio(escapa(par)), ""); par = ""; } }
    linhas.forEach(function (l) {
      var t = limpa(l.txt);
      if (!t) return;
      if (l.pag !== pagAtual) {
        if (/^\d{1,4}$/.test(t)) return;                                   // numero de pagina solto
        pagAtual = l.pag;
        if (par && /[.!?:]["”’)]?$/.test(par)) fecha();                 // a frase acabou junto com a pagina
        if (out.length && !par) out.push("[[página " + l.pag + "]]");
      }
      if (/^\d{1,4}$/.test(t) && (!ant || ant.pag !== l.pag || Math.abs(ant.y - l.y) > passo * 2.5)) return;   // numero de pagina
      var titulo = l.tam >= corpo * 1.15 && t.length <= 120;
      if (titulo) { fecha(); out.push((l.tam >= corpo * 1.5 ? "# " : "## ") + escapa(t), ""); ant = l; return; }
      var m = /^([•◦▪■●\-–]|\d{1,3}[.)]|[a-zA-Z]\))\s+(.+)$/.exec(t);
      if (m && !par) { out.push((/\d|[a-zA-Z]\)/.test(m[1]) ? m[1] : "-") + " " + escapa(m[2])); ant = l; return; }
      if (m) { fecha(); out.push((/\d|[a-zA-Z]\)/.test(m[1]) ? m[1] : "-") + " " + escapa(m[2])); ant = l; return; }
      var novo = false;
      if (ant && ant.pag === l.pag) {
        var salto = ant.y - l.y;
        if (salto > passo * 1.45) novo = true;                              // espaco maior entre linhas
        if (l.x > esq + corpo * 0.8 && ant.x <= esq + corpo * 0.4) novo = true;   // recuo de paragrafo
        if (ant.x + ant.larg < dir - (dir - esq) * 0.18 && /[.!?:]["”’)]?$/.test(limpa(ant.txt))) novo = true;   // linha anterior curta
      }
      if (novo) fecha();
      if (par && /[A-Za-zÀ-ÿ]-$/.test(par) && /^[a-zà-ÿ]/.test(t)) par = par.slice(0, -1) + t;    // palavra partida no fim da linha
      else par += (par && !/ $/.test(par) ? " " : "") + t;
      ant = l;
    });
    fecha();
    return out.join("\n").replace(/\n{4,}/g, "\n\n\n").trim() + "\n";
  }
  async function dePdf(buffer, pdfjs) {
    if (!pdfjs) throw new Error("a biblioteca de PDF não foi carregada");
    var doc = await pdfjs.getDocument({ data: new Uint8Array(buffer) }).promise, linhas = [];
    for (var p = 1; p <= doc.numPages; p++) {
      var pg = await doc.getPage(p), tc = await pg.getTextContent(), at = null;
      tc.items.forEach(function (it) {
        if (!it.str) return;
        var tam = Math.hypot(it.transform[2], it.transform[3]) || it.height || 10, x = it.transform[4], y = it.transform[5];
        if (at && Math.abs(at.y - y) <= Math.max(2, tam * 0.35)) {
          var vao = x - (at.x + at.larg);
          if (vao > tam * 0.18 && !/\s$/.test(at.txt) && !/^\s/.test(it.str)) at.txt += " ";
          at.txt += it.str; at.larg = Math.max(at.larg, x + (it.width || 0) - at.x); at.tam = Math.max(at.tam, tam);
        } else { at = { pag: p, x: x, y: y, tam: tam, txt: it.str, larg: it.width || 0 }; linhas.push(at); }
      });
    }
    if (!linhas.some(function (l) { return l.txt.trim(); })) throw new Error("este PDF não tem texto (deve ser imagem escaneada)");
    return linhasDoPdfParaTexto(linhas);
  }

  // ------------------------------------------------------------------ escolhe pelo nome
  /** arquivo: { nome, buffer (ArrayBuffer) } -> Promise<{ texto, tipo, pronto? }>; pdfjs so e usado para .pdf */
  async function importa(nome, buffer, pdfjs) {
    var ext = (/\.([a-z0-9]+)$/i.exec(nome || "") || [, ""])[1].toLowerCase();
    var comoTexto = function () {
      var u8 = new Uint8Array(buffer), t = new TextDecoder("utf-8", { fatal: false }).decode(u8);
      if (t.indexOf("�") >= 0) t = new TextDecoder("windows-1252").decode(u8);      // arquivo antigo em ANSI
      return t;
    };
    if (ext === "docx") return { tipo: "Word", texto: await deDocx(buffer) };
    if (ext === "odt") return { tipo: "LibreOffice", texto: await deOdt(buffer) };
    if (ext === "pdf") return { tipo: "PDF", texto: await dePdf(buffer, pdfjs) };
    if (ext === "html" || ext === "htm") return { tipo: "página web", texto: deHtml(comoTexto()) };
    if (ext === "md" || ext === "markdown") return { tipo: "Markdown", texto: deMarkdown(comoTexto()) };
    if (ext === "brf" || ext === "brl") return { tipo: "braille pronto", texto: comoTexto(), pronto: true };
    if (ext === "doc") throw new Error("arquivo .doc antigo: abra no Word e salve como .docx");
    return { tipo: "texto", texto: deTexto(comoTexto()) };
  }

  return { importa: importa, deTexto: deTexto, deMarkdown: deMarkdown, deDocx: deDocx, deOdt: deOdt, deHtml: deHtml,
           dePdf: dePdf, linhasDoPdfParaTexto: linhasDoPdfParaTexto, descompacta: descompacta, tokens: tokens, escapa: escapa };
});
