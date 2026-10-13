// Testes do formatador (diagramacao) e dos importadores.  node software/testes/teste_formatador.js
"use strict";
const zlib = require("zlib");
const B = require("../braille-pt.js");
const F = require("../formatador.js");
const I = require("../importar.js");

let ok = 0, falhas = 0;
function igual(nome, obtido, esperado) {
  const a = JSON.stringify(obtido), b = JSON.stringify(esperado);
  if (a === b) ok++;
  else { falhas++; console.log("FALHOU: " + nome + "\n   obtido:   " + a + "\n   esperado: " + b); }
}
const U = (l) => B.paraUnicode(l.celas);
const linhas = (txt, cfg) => F.formata(txt, Object.assign({ numerarPaginas: false }, cfg)).paginas[0].linhas;
const recuo = (l) => { let n = 0; while (n < l.celas.length && l.celas[n] === 0) n++; return n; };

// ---- marcas
igual("trechos", F.trechos("a **b** c *d* _e_ f_g"), [{ txt: "a ", dest: false }, { txt: "b", dest: true }, { txt: " c ", dest: false },
      { txt: "d", dest: true }, { txt: " ", dest: false }, { txt: "e", dest: true }, { txt: " f_g", dest: false }]);
igual("escape", F.trechos("2 \\* 3"), [{ txt: "2 * 3", dest: false }]);
igual("blocos", F.analisa("# T\n\num\ndois\n\n- a\n1. b\n> v\n---\n===\n[[página 7]]\nfim").map((b) => b.t),
      ["titulo", "par", "item", "item", "verso", "sep", "quebra", "pagtinta", "par"]);
igual("linhas de um paragrafo se juntam", F.analisa("um\ndois")[0].runs[0].txt, "um dois");
igual("duas linhas em branco viram uma linha em branco", F.analisa("a\n\n\nb").map((b) => b.t), ["par", "branco", "par"]);

// ---- paragrafo: 3a cela, continuacao na 1a (Normas 5.19)
let ls = linhas("aaa bbb ccc ddd eee fff", { celas: 12 });
igual("paragrafo comeca na 3a cela", recuo(ls[0]), 2);
igual("continuacao na 1a cela", recuo(ls[1]), 0);
igual("nenhuma linha passa da largura", ls.every((l) => l.celas.length <= 12), true);
igual("texto em tinta da linha", ls[0].tinta, "aaa bbb");

// ---- titulo centralizado entre linhas em branco (5.25)
ls = linhas("antes\n\n# oi\n\ndepois", { celas: 20 });
igual("ordem com brancos", ls.map((l) => l.tipo), ["par", "branco", "titulo", "branco", "par"]);
igual("titulo centralizado", recuo(ls[2]), 9);
const semRecuo = (l) => U(l).replace(/^⠀+/, "");
igual("titulo sem sinal de destaque", semRecuo(linhas("# **oi**", { celas: 20 })[0]), "⠕⠊");
ls = linhas("# um titulo bem comprido que nao cabe", { celas: 20 });
igual("titulo longo em varias linhas centralizadas", ls.length > 1 && ls.every((l) => l.celas.length <= 20), true);
ls = linhas("## sub titulo comprido demais", { celas: 16 });
igual("subtitulo na margem, continuacao na 3a cela", [recuo(ls[0]), recuo(ls[1])], [0, 2]);
ls = linhas("# oi", { celas: 20, sublinharTitulo: true });
igual("titulo sublinhado com pontos 25", semRecuo(ls[1]), "⠒⠒");

// ---- itens e versos: 1a cela, continuacao na 3a (5.20 e 5.26)
ls = linhas("- aaa bbb ccc ddd eee", { celas: 12 });
igual("item: hifen na 1a cela", U(ls[0]).slice(0, 2), "⠤⠀");
igual("item: continuacao na 3a cela", recuo(ls[1]), 2);
igual("item numerado", U(linhas("1. um", {})[0]), "⠼⠁⠄⠀⠥⠍");
ls = linhas("> aaa bbb ccc ddd eee", { celas: 12 });
igual("verso", [recuo(ls[0]), recuo(ls[1])], [0, 2]);

// ---- destaque: sinal 35 antes e depois (Grafia, 30)
igual("destaque", U(linhas("a **bc** d", {})[0]), "⠀⠀⠁⠀⠔⠃⠉⠔⠀⠙");
igual("destaque desligado", U(linhas("a **bc** d", { destaques: false })[0]), "⠀⠀⠁⠀⠃⠉⠀⠙");

// ---- paginacao (5.17)
let r = F.formata("um", { celas: 20 });
igual("1a linha e a paginacao", r.paginas[0].linhas[0].tipo, "pag");
igual("numero da pagina a direita", U(r.paginas[0].linhas[0]), "⠀".repeat(18) + "⠼⠁");
r = F.formata("[[página 12]]\num", { celas: 20 });
igual("pagina em tinta a partir da 3a cela", U(r.paginas[0].linhas[0]).slice(0, 5), "⠀⠀⠼⠁⠃");
const muitos = Array.from({ length: 60 }, (_, i) => "p" + i).join("\n\n");
r = F.formata(muitos, { celas: 20, linhasPagina: 10 });
igual("60 paragrafos em paginas de 9 linhas uteis", r.paginas.length, 7);
igual("nenhuma pagina passa do limite", r.paginas.every((p) => p.linhas.length <= 10), true);
igual("paginas numeradas em ordem", r.paginas.map((p) => p.numero), [1, 2, 3, 4, 5, 6, 7]);
igual("quebra de pagina", F.formata("a\n===\nb", {}).paginas.length, 2);
// titulo nunca sozinho no fim da pagina: precisa caber com 2 linhas do texto
const oito = Array.from({ length: 8 }, (_, i) => "p" + i).join("\n\n");
r = F.formata(oito + "\n\n# titulo\n\ntexto um\n\ntexto dois", { celas: 20, linhasPagina: 10 });
igual("titulo vai para a pagina seguinte", r.paginas[1].linhas[1].tipo, "titulo");
igual("pagina nao comeca com linha em branco", r.paginas[1].linhas[1].celas.length > 0, true);
igual("capitulo em pagina nova", F.formata("# a\n\nx\n\n# b\n\ny", { capituloPaginaNova: true }).paginas.length, 2);
igual("totais", F.formata("ab", { numerarPaginas: false }).totais, { paginas: 1, linhas: 1, celas: 4, pontos: 3 });

// ---- exportacao
igual("tabela braille ASCII tem 64 sinais", F.ASCII.length, 64);
igual("brf", F.paraBRF(F.formata("ação 12", { numerarPaginas: false }).paginas), "  A&>O #AB");
igual("brf de volta", F.deBRF("  A&>O #AB").paginas[0].linhas[0].celas, F.formata("ação 12", { numerarPaginas: false }).paginas[0].linhas[0].celas);

// ---- importadores
igual("txt: titulo na 1a linha", I.deTexto("Meu texto\n\nPrimeiro paragrafo\ncontinua.\n\nSegundo."), "# Meu texto\n\nPrimeiro paragrafo\ncontinua.\n\nSegundo.\n");
igual("txt: uma linha so nao vira titulo", I.deTexto("Bom dia"), "Bom dia\n");
igual("txt: asterisco protegido", I.deTexto("a\n\n2 * 3"), "# a\n\n2 \\* 3\n");
igual("html", I.deHtml("<html><head><title>x</title><style>p{}</style></head><body><h1>T&iacute;tulo</h1><p>Um <b>dois</b> tr&ecirc;s.</p><ul><li>a</li><li>b</li></ul><ol><li>c</li></ol></body></html>"),
      "# Título\n\nUm **dois** três.\n\n- a\n- b\n\n1. c\n");
igual("md", I.deMarkdown("# T\n\n[link](http://x) e `cod`"), "# T\n\nlink e cod");

// zip minimo para montar um .docx de teste
function zip(arqs, comprime) {
  const partes = [], central = []; let pos = 0;
  for (const [nome, txt] of Object.entries(arqs)) {
    const bruto = Buffer.from(txt, "utf8"), dados = comprime ? zlib.deflateRawSync(bruto) : bruto, n = Buffer.from(nome);
    const cab = Buffer.alloc(30); cab.writeUInt32LE(0x04034b50, 0); cab.writeUInt16LE(20, 4); cab.writeUInt16LE(comprime ? 8 : 0, 8);
    cab.writeUInt32LE(zlib.crc32(bruto), 14); cab.writeUInt32LE(dados.length, 18); cab.writeUInt32LE(bruto.length, 22); cab.writeUInt16LE(n.length, 26);
    const cen = Buffer.alloc(46); cen.writeUInt32LE(0x02014b50, 0); cen.writeUInt16LE(20, 4); cen.writeUInt16LE(20, 6); cen.writeUInt16LE(comprime ? 8 : 0, 10);
    cen.writeUInt32LE(zlib.crc32(bruto), 16); cen.writeUInt32LE(dados.length, 20); cen.writeUInt32LE(bruto.length, 24); cen.writeUInt16LE(n.length, 28); cen.writeUInt32LE(pos, 42);
    partes.push(cab, n, dados); central.push(cen, n); pos += 30 + n.length + dados.length;
  }
  const tc = central.reduce((s, b) => s + b.length, 0), fim = Buffer.alloc(22);
  fim.writeUInt32LE(0x06054b50, 0); fim.writeUInt16LE(Object.keys(arqs).length, 8); fim.writeUInt16LE(Object.keys(arqs).length, 10);
  fim.writeUInt32LE(tc, 12); fim.writeUInt32LE(pos, 16);
  const b = Buffer.concat([...partes, ...central, fim]);
  return b.buffer.slice(b.byteOffset, b.byteOffset + b.length);
}
const W = (s) => '<?xml version="1.0"?><w:document xmlns:w="x"><w:body>' + s + "</w:body></w:document>";
const docx = {
  "word/styles.xml": '<w:styles><w:style w:type="paragraph" w:styleId="Ttulo1"><w:name w:val="heading 1"/></w:style><w:style w:styleId="Normal"><w:name w:val="Normal"/></w:style></w:styles>',
  "word/numbering.xml": '<w:numbering><w:abstractNum w:abstractNumId="0"><w:lvl w:ilvl="0"><w:numFmt w:val="decimal"/></w:lvl></w:abstractNum><w:abstractNum w:abstractNumId="1"><w:lvl w:ilvl="0"><w:numFmt w:val="bullet"/></w:lvl></w:abstractNum><w:num w:numId="1"><w:abstractNumId w:val="0"/></w:num><w:num w:numId="2"><w:abstractNumId w:val="1"/></w:num></w:numbering>',
  "word/document.xml": W(
    '<w:p><w:pPr><w:pStyle w:val="Ttulo1"/><w:rPr><w:b/></w:rPr></w:pPr><w:r><w:t>Relat&#243;rio</w:t></w:r></w:p>' +
    '<w:p><w:r><w:t xml:space="preserve">Texto </w:t></w:r><w:r><w:rPr><w:b/></w:rPr><w:t>forte</w:t></w:r><w:r><w:rPr><w:b w:val="0"/></w:rPr><w:t xml:space="preserve"> e 2*3.</w:t></w:r></w:p>' +
    '<w:p><w:pPr><w:numPr><w:ilvl w:val="0"/><w:numId w:val="1"/></w:numPr></w:pPr><w:r><w:t>primeiro</w:t></w:r></w:p>' +
    '<w:p><w:pPr><w:numPr><w:ilvl w:val="0"/><w:numId w:val="1"/></w:numPr></w:pPr><w:r><w:t>segundo</w:t></w:r></w:p>' +
    '<w:p><w:pPr><w:numPr><w:ilvl w:val="0"/><w:numId w:val="2"/></w:numPr></w:pPr><w:r><w:t>marcador</w:t></w:r></w:p>' +
    '<w:p><w:pPr><w:jc w:val="center"/></w:pPr><w:r><w:rPr><w:b/></w:rPr><w:t>Parte dois</w:t></w:r></w:p>' +
    '<w:tbl><w:tr><w:tc><w:p><w:r><w:t>a</w:t></w:r></w:p></w:tc><w:tc><w:p><w:r><w:t>b</w:t></w:r></w:p></w:tc></w:tr></w:tbl>' +
    '<w:p><w:r><w:br w:type="page"/></w:r></w:p><w:p><w:r><w:t>fim</w:t></w:r></w:p>')
};
const esperadoDocx = "# Relatório\n\nTexto **forte** e 2\\*3.\n\n1. primeiro\n2. segundo\n- marcador\n# Parte dois\n\na; b\n\n\n===\nfim\n";

(async () => {
  igual("docx sem compressao", await I.deDocx(zip(docx, false)), esperadoDocx);
  igual("docx comprimido", await I.deDocx(zip(docx, true)), esperadoDocx);
  igual("importa pelo nome", (await I.importa("a.DOCX", zip(docx, true))).tipo, "Word");
  igual("importa txt em ANSI", (await I.importa("a.txt", Uint8Array.from([0x61, 0xE7, 0xE3, 0x6F, 10, 10, 0x62]).buffer)).texto, "# ação\n\nb\n");
  const odt = { "content.xml": '<office:document-content><office:automatic-styles><style:style style:name="T1"><style:text-properties fo:font-weight="bold"/></style:style></office:automatic-styles><office:body><office:text>' +
    '<text:h text:outline-level="1">Titulo</text:h><text:p>Um <text:span text:style-name="T1">dois</text:span>.</text:p><text:list><text:list-item><text:p>item</text:p></text:list-item></text:list></office:text></office:body></office:document-content>' };
  igual("odt", await I.deOdt(zip(odt, true)), "# Titulo\n\nUm **dois**.\n\n- item\n");
  // pdf: linhas ja extraidas (corpo 10, titulo 16)
  const L = (pag, y, tam, txt, x) => ({ pag, x: x === undefined ? 50 : x, y, tam, txt, larg: txt.length * tam * 0.5 });
  igual("pdf: titulo pela letra grande, paragrafos, hifen e numero de pagina",
    I.linhasDoPdfParaTexto([L(1, 700, 16, "Titulo"), L(1, 670, 10, "Uma linha comprida de texto que vai ate a mar-"), L(1, 658, 10, "gem direita e termina aqui."),
      L(1, 630, 10, "Outro paragrafo, mais abaixo, tambem bem comprido."), L(1, 40, 10, "1"), L(2, 700, 10, "Texto da segunda pagina do original.")]),
    "# Titulo\n\nUma linha comprida de texto que vai ate a margem direita e termina aqui.\n\nOutro paragrafo, mais abaixo, tambem bem comprido.\n\n[[página 2]]\nTexto da segunda pagina do original.\n");
  // documento inteiro: do .docx as paginas
  const res = F.formata(await I.deDocx(zip(docx, true)), {});
  igual("docx formatado: 2 paginas (quebra manual)", res.paginas.length, 2);
  igual("docx formatado: titulo centralizado na 2a linha", [res.paginas[0].linhas[1].tipo, recuo(res.paginas[0].linhas[1]) > 5], ["titulo", true]);
  console.log("%d testes ok, %d falhas", ok, falhas);
  process.exit(falhas ? 1 : 0);
})();
