# Firmware e programas

São três programas, que usam a mesma tabela braille:

| Programa | Onde roda | Para quê |
|---|---|---|
| `firmware/ImpressoraBraille/` | Arduino Mega | move os motores, bate o solenoide, cuida da folha |
| `software/index.html` (Relevo) | navegador (Edge ou Chrome) | abre o arquivo, formata em braille, mostra as folhas e manda imprimir pelo USB |
| `simulador/index.html` | navegador | mostra a máquina em 3D imprimindo, sem precisar da máquina |

## 1. Gravar o firmware

1. Abra `firmware/ImpressoraBraille/ImpressoraBraille.ino` na Arduino IDE.
2. Ferramentas, Placa: **Arduino Mega or Mega 2560**. Processador: ATmega2560. Escolha a porta.
3. Carregar. Não precisa de biblioteca nenhuma.
4. Abra o Monitor Serial em **115200** e "Nova linha". Deve aparecer `# Impressora braille v1.0 pronta.`

O sketch tem três arquivos: o `.ino`, `config.h` (pinos e valores de fábrica) e `tabela_braille.h` (gerado, não edite).

## 2. Usar pelo programa Relevo

Abra `software/index.html` com dois cliques (Edge ou Chrome, no computador), ou a página do projeto na internet.
Não instala nada e funciona sem internet. O manual completo está em [`11-programa-relevo.md`](11-programa-relevo.md).

1. Solte o arquivo (Word, PDF, texto) na aba Documento. O programa formata e mostra as folhas.
2. **Conectar** e escolher a porta do Arduino.
3. **Imprimir**. O programa manda uma linha por vez, ejeta a folha no fim de cada página e pede a próxima.

Na aba Impressora ficam os comandos manuais, os quatro testes e as margens. **Conferir tradutor** manda 17 frases
para a impressora traduzir e compara com a tradução do programa: é o teste que prova que as duas tabelas são
iguais na placa de verdade.

## 3. Usar sem o painel

Qualquer programa de terminal serve, inclusive o Monitor Serial da Arduino IDE e aplicativos de celular com cabo OTG.
Digite o texto e mande: a impressora traduz sozinha e imprime. Cada linha enviada é um parágrafo.

## 4. Comandos

Toda linha que começa com `$` é comando. A resposta termina com `ok`, `fim_pagina` ou `erro: ...`. Linhas que
começam com `#` são avisos.

| Comando | O que faz |
|---|---|
| `texto qualquer` | traduz para braille e imprime |
| `$H` | leva o carro até o fim de curso (referência) |
| `$L` | espera a folha, puxa e deixa na primeira linha. Se a folha que está na máquina já foi usada, ejeta antes |
| `$E` | ejeta a folha |
| `$C 010307...` | imprime uma linha de celas prontas, 2 dígitos hexadecimais por cela (bit 0 = ponto 1) |
| `$F n` | pula n linhas |
| `$T 1` a `$T 4` | testes: celas cheias, alfabeto, ida e volta, escada de pulso |
| `$P n` | n batidas sem mover nada, para regular punção e matriz |
| `$X mm`, `$Y mm` | move o carro para a posição; avança o papel |
| `$M 0` ou `$M 1` | solta ou liga os motores |
| `$A texto` | só traduz e devolve as celas, sem imprimir |
| `$S nome=valor` | muda um parâmetro |
| `$I` | mostra todos os parâmetros e o estado dos sensores |
| `$W` | grava os parâmetros na memória da placa |
| `$R` | volta aos valores de fábrica (depois `$W` para gravar) |
| `!` | cancela na hora |

## 5. Parâmetros

| Nome | Fábrica | Significado |
|---|---|---|
| `ppx` | 80,00 | passos por mm do carro |
| `ppy` | 38,44 | passos por mm do papel |
| `vx`, `ax` | 120, 3000 | velocidade (mm/s) e aceleração (mm/s²) do carro |
| `vy`, `ay` | 30, 400 | velocidade e aceleração do papel |
| `ton` | 25 | tempo do solenoide ligado (ms). Limite de segurança: 80 |
| `toff` | 30 | espera para o punção subir antes de mover (ms) |
| `tass` | 5 | parada antes da batida (ms) |
| `ponto`, `cela`, `linha` | 2,5, 6, 10 | medidas da cela (mm) |
| `me`, `mt` | 20, 12 | margem esquerda e de cima (mm) |
| `celas`, `linhas` | 30, 23 | celas por linha e linhas por folha |
| `recuo` | 2 | celas em branco no começo do parágrafo |
| `home` | 8 | quantos mm o fim de curso fica para dentro da borda esquerda da folha |
| `rolete` | 48 | distância do rolete até a linha de punção (mm) |
| `invx`, `invy` | 0 | 1 inverte o sentido do motor |
| `vaievem` | 1 | 1: as fileiras alternam o sentido (mais rápido). 0: sempre da esquerda para a direita |
| `fcnf` | 1 | 1: fim de curso ligado em C e NF |
| `fimx` | 1 | 0: sem fim de curso (assume que o carro já está na esquerda) |
| `sensor` | 1 | 0: sem sensor de papel |

## 6. Como o firmware trabalha

- **Movimento**: cada motor anda com rampa de aceleração e de freada. O intervalo entre passos vem de
  t = √(2k ÷ a), a fórmula do movimento uniformemente acelerado, e nunca fica menor que o da velocidade máxima.
- **Linha de texto**: três fileiras de pontos (pontos 1 e 4, depois 2 e 5, depois 3 e 6). Em cada fileira o carro vai
  só aos pontos que existem e bate. O papel avança 2,5 mm entre fileiras e completa os 10 mm até a próxima linha.
  O papel só anda para a frente, para não perder a posição.
- **Folha**: com o sensor, a impressora espera a folha encostar nos roletes, puxa 48 mm até a linha de punção e mais
  a margem de cima. Na 23ª linha, ejeta e pede outra folha.
- **Proteção do solenoide**: o pulso nunca passa de 80 ms e o solenoide nunca fica ligado mais de 40 % do tempo.
  O pino do solenoide é o primeiro a ser posto em nível baixo quando a placa liga.
- **Cancelar**: o `!` pela serial ou o botão param o movimento em no máximo 128 passos (1,6 mm).

## 7. O tradutor

`software/braille-pt.js` é a fonte da tabela dos sinais. Ele faz letras, acentos, maiúsculas, números e pontuação conforme a
Grafia Braille de 2018. O firmware usa a mesma tabela (`tabela_braille.h` é gerado por
`node software/gera_tabela_firmware.js`). Diferença: a regra das "mais de três palavras em maiúsculas" só existe no
programa; pelo terminal, cada palavra em maiúsculas recebe o seu sinal duplo, o que também é leitura correta.

`software/formatador.js` monta as folhas (título no centro, parágrafo na 3ª cela, paginação) e `software/importar.js`
lê os arquivos. Os dois são explicados no documento 11.

`software/leiaute.js` calcula a posição de cada ponto na folha e o tempo de impressão. É a mesma conta do firmware.

Testes: `node software/testes/teste_braille.js` roda 52 casos (letras, acentos, números, pontuação, quebra de linha,
posição dos pontos, limites da folha) e `node software/testes/teste_formatador.js` roda 48 (formatação e importação).

## 8. O simulador

`simulador/index.html` carrega o próprio modelo do CAD (`modelo.js`, gerado por `cad/gerar.py`). Digite um texto e
clique em Imprimir: o carro anda, o êmbolo bate e os pontos aparecem na folha na mesma ordem da máquina real.
"Raio-x" deixa o MDF transparente, "Corte" fatia a máquina da frente para trás e "Explodir" afasta as peças.

## 9. Refazer o CAD

Depois de mudar `cad/parametros.py`, no Git Bash:

```
cd cad
./rodar.sh verificar        # procura interferências (1 minuto)
./rodar.sh gerar            # STL, STEP, DXF, SVG, listas e o modelo do simulador
./rodar.sh mesas            # arruma as pecas impressas em mesas de 250 x 250 mm (.3mf e .stl)
./rodar.sh render final ../docs/imagens     # .FCStd com cores e as imagens (abre o FreeCAD por alguns segundos)
python ../docs/gerar_tabelas.py
```
