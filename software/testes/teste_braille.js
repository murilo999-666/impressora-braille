// Testes do tradutor e do leiaute. Rodar:  node software/testes/teste_braille.js
"use strict";
const B = require("../braille-pt.js");
const L = require("../leiaute.js");

let ok = 0, falhas = 0;
function igual(nome, obtido, esperado) {
  const a = JSON.stringify(obtido), b = JSON.stringify(esperado);
  if (a === b) ok++;
  else { falhas++; console.log("FALHOU: " + nome + "\n   obtido:   " + a + "\n   esperado: " + b); }
}
const t = (s) => B.paraUnicode(B.traduz(s).celas);

// ---- letras, acentos, maiusculas (Grafia Braille 2018)
igual("abc", t("abc"), "⠁⠃⠉");
igual("alfabeto", t("abcdefghijklmnopqrstuvwxyz"), "⠁⠃⠉⠙⠑⠋⠛⠓⠊⠚⠅⠇⠍⠝⠕⠏⠟⠗⠎⠞⠥⠧⠺⠭⠽⠵");
igual("acentos", t("áàâãéêíóôõúüç"), "⠷⠫⠡⠜⠿⠣⠌⠬⠹⠪⠾⠳⠯");
igual("Brasil", t("Brasil"), "⠨⠃⠗⠁⠎⠊⠇");
igual("BRASIL", t("BRASIL"), "⠨⠨⠃⠗⠁⠎⠊⠇");
igual("ação", t("ação"), "⠁⠯⠜⠕");
igual("pão", t("pão"), "⠏⠜⠕");
igual("àquela", t("àquela"), "⠫⠟⠥⠑⠇⠁");
igual("É", t("É"), "⠨⠿");
igual("McDonald", t("McDonald"), "⠨⠍⠉⠨⠙⠕⠝⠁⠇⠙");
igual("Olá, mundo!", t("Olá, mundo!"), "⠨⠕⠇⠷⠂⠀⠍⠥⠝⠙⠕⠖");
// ---- numeros
igual("2026", t("2026"), "⠼⠃⠚⠃⠋");
igual("3,14", t("3,14"), "⠼⠉⠂⠁⠙");
igual("1.000", t("1.000"), "⠼⠁⠄⠚⠚⠚");
igual("5a (sinal de letra)", t("5a"), "⠼⠑⠐⠁");
igual("5k", t("5k"), "⠼⠑⠅");
igual("10%", t("10%"), "⠼⠁⠚⠸⠴");
igual("data", t("12/10/2026"), "⠼⠁⠃⠠⠂⠼⠁⠚⠠⠂⠼⠃⠚⠃⠋");
igual("numero e ponto final", t("em 2026."), "⠑⠍⠀⠼⠃⠚⠃⠋⠄");
igual("dois numeros", t("7 8"), "⠼⠛⠀⠼⠓");
// ---- pontuacao
igual("(a)", t("(a)"), "⠣⠄⠁⠠⠜");
igual("pergunta", t("tudo bem?"), "⠞⠥⠙⠕⠀⠃⠑⠍⠢");
igual("aspas", t('"oi"'), "⠦⠕⠊⠦");
igual("hifen", t("guarda-chuva"), "⠛⠥⠁⠗⠙⠁⠤⠉⠓⠥⠧⠁");
igual("reticencias", t("e…"), "⠑⠄⠄⠄");
igual("arroba", t("a@b"), "⠁⠱⠃");
// ---- caixa alta em sequencia
igual("3 palavras em caixa alta", t("FEIRA DE CIENCIAS"), "⠨⠨⠋⠑⠊⠗⠁⠀⠨⠨⠙⠑⠀⠨⠨⠉⠊⠑⠝⠉⠊⠁⠎");
igual("mais de 3 palavras em caixa alta", t("FEIRA BRASILEIRA DE CIENCIAS"),
      "⠒⠨⠨⠋⠑⠊⠗⠁⠀⠃⠗⠁⠎⠊⠇⠑⠊⠗⠁⠀⠙⠑⠀⠨⠨⠉⠊⠑⠝⠉⠊⠁⠎");
// ---- caracteres sem cela
igual("aviso", B.traduz("a~b").avisos, ["~"]);
igual("quebra de paragrafo", B.traduz("a\nb").celas, [1, -1, 3]);
igual("origem", B.traduz("Ab").origem, [0, 0, 1]);

// ---- quebra de linha
const q = (s, larg, rec) => B.quebra(B.traduz(s).celas, larg, rec).map(B.paraUnicode);
igual("quebra simples", q("aaa bbb ccc ddd", 10), ["⠁⠁⠁⠀⠃⠃⠃", "⠉⠉⠉⠀⠙⠙⠙"]);
igual("quebra com recuo", q("aaa bbb ccc", 10, 2), ["⠀⠀⠁⠁⠁⠀⠃⠃⠃", "⠉⠉⠉"]);
igual("palavra maior que a linha", q("abcdefghij", 6), ["⠁⠃⠉⠙⠑⠤", "⠋⠛⠓⠊⠚"]);
igual("dois paragrafos", q("a\nb", 10), ["⠁", "⠃"]);
igual("linha em branco", q("a\n\nb", 10), ["⠁", "", "⠃"]);
igual("nunca passa da largura", q("Uma impressora braille de baixo custo para a escola.", 12)
      .every((l) => Array.from(l).length <= 12), true);
igual("hex", B.paraHex([1, 0, 63]), "01003f");

// ---- leiaute
const c = L.config();
igual("linhas que cabem", L.linhasQueCabem(c), 23);
igual("celas que cabem", L.celasQueCabem(c) >= 30, true);
const pg = L.pagina([[B.P(123456)]], c);       // uma cela cheia
igual("6 pontos", pg.pontos.length, 6);
igual("3 fileiras", pg.fileiras.length, 3);
igual("posicao do ponto 1", [pg.pontos[0].u, pg.pontos[0].v], [20, 12]);
igual("ponto 4 fica 2,5 mm a direita", pg.pontos.find((p) => p.ponto === 4).u, 22.5);
igual("ponto 3 fica 5 mm abaixo", pg.pontos.find((p) => p.ponto === 3).v, 17);
igual("vai e vem: 2a fileira invertida", pg.fileiras[1].us, [22.5, 20]);
const pg2 = L.pagina([[B.P(1), 0, B.P(1)], [B.P(4)]], c);
igual("2a cela a 6 mm", pg2.pontos[1].u, 32);
igual("2a linha a 10 mm", pg2.pontos[2].v, 22);
// tudo dentro do curso da maquina?
const cheia = [];
for (let i = 0; i < c.linhasPorPagina; i++) cheia.push(new Array(c.celasPorLinha).fill(63));
const pc = L.pagina(cheia, c);
const us = pc.pontos.map((p) => p.u + c.xPapel0), vs = pc.pontos.map((p) => p.v);
igual("pagina cheia: X dentro do curso", Math.min(...us) >= c.xMin && Math.max(...us) <= c.xMax, true);
igual("pagina cheia: V dentro do alcance do rolete", Math.max(...vs) <= c.papelAltura - c.distRoletePuncao - c.folgaFim, true);
igual("pagina cheia: pontos", pc.pontos.length, 23 * 30 * 6);
igual("paginas", L.paginas(new Array(50).fill([1]), c).length, 3);

console.log("pagina cheia: %d pontos, margem direita %s mm, ultima fileira a %s mm do topo, tempo ~%s min",
            pc.pontos.length, (c.papelLargura - (Math.max(...us) - c.xPapel0)).toFixed(1), Math.max(...vs),
            (L.tempo(pc, c) / 60).toFixed(1));
const frase = L.pagina(B.quebra(B.traduz("Feira Brasileira de Ciencias e Engenharia 2027").celas, 30, 2), c);
console.log("frase de exemplo: %d pontos, ~%s s", frase.pontos.length, L.tempo(frase, c).toFixed(0));
console.log("%d testes ok, %d falhas", ok, falhas);
process.exit(falhas ? 1 : 0);
