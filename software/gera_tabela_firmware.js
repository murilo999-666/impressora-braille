// Gera firmware/ImpressoraBraille/tabela_braille.h a partir de braille-pt.js, para o
// firmware e o painel usarem EXATAMENTE a mesma tabela.   node software/gera_tabela_firmware.js
"use strict";
const fs = require("fs");
const path = require("path");
const B = require("./braille-pt.js");

const hex = (n) => "0x" + n.toString(16).toUpperCase().padStart(2, "0");
const letras = Object.keys(B.LETRAS).filter((c) => c.codePointAt(0) < 256)
  .sort((a, b) => a.codePointAt(0) - b.codePointAt(0));
const sinais = Object.keys(B.SINAIS).filter((c) => c.codePointAt(0) < 256)
  .sort((a, b) => a.codePointAt(0) - b.codePointAt(0));

let h = "// GERADO por software/gera_tabela_firmware.js a partir de software/braille-pt.js. NAO EDITAR.\n";
h += "// Cela = 6 bits: bit 0 = ponto 1 ... bit 5 = ponto 6. Codigos de caractere em Latin-1 / Unicode < 256.\n";
h += "#ifndef TABELA_BRAILLE_H\n#define TABELA_BRAILLE_H\n#include <avr/pgmspace.h>\n\n";
h += "#define CELA_NUMERO " + hex(B.SINAL_NUMERO) + "\n#define CELA_MAIUSCULA " + hex(B.SINAL_MAIUSCULA) +
     "\n#define CELA_LETRA " + hex(B.SINAL_LETRA) + "\n#define CELA_HIFEN " + hex(B.P(36)) + "\n\n";
h += "// letras minusculas: {codigo, cela}\nconst uint8_t TAB_LETRAS[][2] PROGMEM = {\n";
h += letras.map((c) => "  {" + hex(c.codePointAt(0)) + ", " + hex(B.LETRAS[c]) + "}").join(",\n") + "\n};\n";
h += "const uint8_t N_LETRAS = " + letras.length + ";\n\n";
h += "// digitos 0..9\nconst uint8_t TAB_DIGITOS[10] PROGMEM = {" +
     "0123456789".split("").map((d) => hex(B.DIGITOS[d])).join(", ") + "};\n\n";
h += "// sinais: {codigo, quantidade de celas, cela 1, cela 2, cela 3}\nconst uint8_t TAB_SINAIS[][5] PROGMEM = {\n";
h += sinais.map((c) => {
  const s = B.SINAIS[c];
  return "  {" + [hex(c.codePointAt(0)), s.length, hex(s[0] || 0), hex(s[1] || 0), hex(s[2] || 0)].join(", ") + "}";
}).join(",\n") + "\n};\n";
h += "const uint8_t N_SINAIS = " + sinais.length + ";\n\n#endif\n";

const destino = path.join(__dirname, "..", "firmware", "ImpressoraBraille", "tabela_braille.h");
fs.mkdirSync(path.dirname(destino), { recursive: true });
fs.writeFileSync(destino, h);
console.log("gerado: " + destino + " (" + letras.length + " letras, " + sinais.length + " sinais)");
