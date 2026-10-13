# O programa Relevo e a formatação do braille

O Relevo é o programa que fica entre o seu arquivo e a impressora. Ele abre o arquivo, monta as folhas em braille
já formatadas e manda imprimir. Fica em `software/index.html` e roda no navegador, sem instalar.

![Tela do Relevo](imagens/relevo.png)

## 1. Usar

1. **Abrir o arquivo.** Solte o arquivo na área tracejada, ou clique nela para escolher.
2. **Conferir.** À esquerda fica o texto que o programa leu, com marcas simples (`#` para título, `-` para item).
   À direita ficam as folhas como vão sair. O texto em tinta aparece acima de cada linha de braille, para quem
   enxerga conferir sem saber braille.
3. **Corrigir, se preciso.** Se um título não foi reconhecido, ponha o cursor na linha e clique em Título. O que
   você muda à esquerda aparece na hora à direita.
4. **Imprimir.** Clique em Conectar, escolha a porta do Arduino e clique em Imprimir. O programa espera a folha,
   imprime, ejeta e pede a próxima.

Botões da direita: **Salvar .brf** grava o braille pronto no formato que impressoras braille comerciais e o Braille
Fácil leem. **Ver em 3D** abre o simulador marcando a folha que está à vista.

### Arquivos aceitos

| Arquivo | O que o programa aproveita |
|---|---|
| Word (.docx) | estilos de título, listas numeradas e com marcador, negrito, itálico, sublinhado, quebra de página, tabelas (cada linha vira um parágrafo, com as células separadas por ponto e vírgula) |
| PDF | texto; **letra maior que a do corpo vira título**; parágrafos pelo espaço entre linhas; palavras partidas no fim da linha são emendadas; o número de cada página do original é guardado |
| Texto (.txt) | parágrafos; a primeira linha curta vira título; linhas que começam com `-` ou `1.` viram itens |
| LibreOffice (.odt) | títulos, listas, negrito e itálico |
| Página (.html) | h1 a h6, parágrafos, listas, negrito e itálico |
| Markdown (.md) | as marcas são as mesmas do programa |
| Braille pronto (.brf) | imprime como está, sem traduzir de novo |

Não abre: `.doc` antigo (salve como .docx), PDF escaneado (é imagem, não tem texto) e fórmulas.

### A aba Impressora

Tem os comandos manuais (referenciar o carro, carregar e ejetar a folha), os quatro testes de calibração, as margens,
o tempo do pulso do solenoide e o registro de tudo o que a impressora respondeu. O botão **Conferir tradutor** manda
17 frases para o firmware traduzir e compara com a tradução do programa.

## 2. Como o braille é formatado

**Braille não tem tamanho de letra, negrito, cor nem tipo de fonte.** Toda cela tem o mesmo tamanho: 2,5 mm entre
pontos e 6 mm entre celas. Um título em letra 24 e um rodapé em letra 8 ocupam o mesmo espaço. Por isso a
formatação em braille não copia a aparência do original: ela mostra a **estrutura** do texto pela posição das linhas
e por alguns sinais. A Grafia Braille diz isso assim: segue-se a disposição do texto em tinta "tendo sempre em
conta, no entanto, as especificidades da leitura tátil".

As regras que o programa aplica:

| No original | Em braille | Fonte |
|---|---|---|
| Página | linha de até 40 celas; folha de 27 linhas em face única, com a 1ª reservada para identificação | Normas Técnicas, 5.6.2 |
| Número da página | na 1ª linha: à direita, o número da folha braille; a partir da 3ª cela, o número da página do original | Normas Técnicas, 5.17 |
| Parágrafo | começa "sempre na terceira cela"; as outras linhas começam na 1ª. Não se pula linha entre parágrafos | Normas Técnicas, 5.19 |
| Título | centralizado; ou na margem, continuando na 3ª cela. Sempre "separados por linhas em branco" | Normas Técnicas, 5.25 |
| Título no fim da folha | não pode ficar sozinho: se não couber com pelo menos duas linhas do texto, vai para a folha seguinte | Normas Técnicas, 5.25, obs. 2 |
| Item de lista, questão | começa na 1ª cela e continua na 3ª | Normas Técnicas, 5.20 |
| Verso | começa na margem; se passar da linha, continua na 3ª cela | Normas Técnicas, 5.26 |
| Capítulo novo | começa em folha nova (opção do programa) | Normas Técnicas, 5.21 |
| Itálico, negrito, sublinhado | um sinal só, pontos 3-5, colocado "imediatamente" antes e depois do trecho | Grafia Braille, 30 |
| Título em negrito ou caixa alta | sem sinal: as linhas em branco "substituem, com vantagem, o itálico e a caixa alta" | Grafia Braille, 46 |
| Maiúscula | pontos 4-6 antes da letra; duas vezes antes da palavra toda em maiúsculas | Grafia Braille |
| Número | pontos 3-4-5-6 antes; os algarismos são as letras de a até j | Grafia Braille |

As Normas também pedem cuidado com o exagero: sinais de maiúscula e de destaque antes de cada palavra dificultam a
leitura e não produzem o mesmo efeito que cor e tamanho produzem para quem vê. Por isso há uma opção para desligar
os destaques.

### O que muda nesta impressora

A norma fala em 40 celas e 27 linhas porque as folhas de braille comerciais são maiores que o A4. Esta máquina, em
A4, faz **30 celas por linha** (o carro tem 196 mm de curso) e **23 linhas por folha** (os últimos 48 mm ficam atrás
dos roletes). Com a paginação ligada, sobram 22 linhas de texto por folha. Uma página de texto comum (cerca de 3000
caracteres) vira cerca de cinco folhas de braille.

### O que o programa ainda não faz

- Dividir palavras em sílabas no fim da linha. A palavra que não cabe desce inteira.
- Notas de rodapé, sumário com pontilhado e tabelas em colunas.
- Matemática, música e química.
- Ordinais na forma oficial (7º sai como "7o").

## 3. As marcas do texto

O importador escreve essas marcas sozinho; você pode mexer nelas ou digitar o texto direto.

| Você escreve | Sai em braille |
|---|---|
| `# Capítulo 1` | título centralizado |
| `## Introdução` | subtítulo na margem |
| `- arroz` ou `1. arroz` ou `a) arroz` | item de lista (dois espaços antes = subitem) |
| `> Minha terra tem palmeiras` | verso |
| `**importante**` ou `*importante*` | destaque |
| uma linha em branco | novo parágrafo |
| duas linhas em branco | uma linha em branco na folha |
| `---` | separador: fileira de pontos 2-5 no centro |
| `===` | nova folha |
| `[[página 12]]` | daqui em diante o original está na página 12 |
| `\*` | um asterisco de verdade |

## 4. Por dentro

| Arquivo | Papel |
|---|---|
| `braille-pt.js` | texto para celas: letras, acentos, maiúsculas, números, pontuação |
| `formatador.js` | marcas para blocos, blocos para linhas, linhas para folhas; exporta .brf |
| `importar.js` | .docx, .odt, .pdf, .html, .txt e .md para texto com marcas. O .docx e o .odt são descompactados pelo próprio navegador; o PDF usa a biblioteca pdf.js, que está em `lib/` |
| `leiaute.js` | posição de cada ponto em milímetros e tempo de impressão |
| `relevo.js`, `relevo.css`, `index.html` | a tela e a conversa com a impressora |

A conversa com a impressora usa os comandos do firmware (documento 07): `$L` carrega a folha, `$C` manda uma linha
de celas, `$F` pula linhas em branco e `$E` ejeta. As folhas são montadas no computador; o firmware só marca.

Testes: `node software/testes/teste_formatador.js` roda 48 casos, entre eles um .docx montado na hora, a regra do
título no fim da folha, a paginação e a tabela do .brf.
