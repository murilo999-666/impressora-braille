# Calibração e testes

Faça na ordem. Cada teste tem um critério para passar. Anote os resultados numa tabela: eles são os dados do relatório.

## 1. Bancada, antes de montar tudo

| # | Teste | Como | Passa se |
|---|---|---|---|
| 1 | Fonte | multímetro na saída | 11,8 a 12,5 V |
| 2 | Step-up | regular sem carga | 24,0 V ± 0,2 |
| 3 | Solenoide solto na mão | `$P 5` | cinco batidas firmes; o LED1 pisca cinco vezes |
| 4 | Aquecimento | `$P 200` (cerca de 13 s) | corpo do solenoide morno, não quente a ponto de não segurar |
| 5 | Vref dos drivers | multímetro no trimpot | 0,50 V nos dois |
| 6 | Motores soltos | `$M 1`, depois `$X 50` e `$Y 20` | giram suave, sem pular nem zumbir parado |
| 7 | Chaves | apertar com o dedo e mandar `$I` | o estado muda de "livre" para "apertado" e de "sem papel" para "com papel" |

## 2. Movimento

| # | Teste | Como | Passa se |
|---|---|---|---|
| 8 | Sentido do X | `$H` | o carro vai para a **esquerda** e para na chave. Se for para a direita: `$S invx=1` |
| 9 | Repetição do home | `$X 100`, marcar a posição do carro com lápis na mesa; `$H`, `$X 100` de novo, 5 vezes | sempre na mesma marca (± 0,1 mm) |
| 10 | Escala do X | `$X 0`, marcar; `$X 180`, marcar; medir com régua | 180,0 ± 0,3 mm. Se medir M: `$S ppx=` 80 × 180 ÷ M |
| 11 | Sentido do papel | folha nos roletes, `$Y 20` | a folha vai para a **frente**. Se voltar: `$S invy=1` |
| 12 | Escala do papel | riscar a folha rente à borda da mesa; `$Y 200`; riscar de novo; medir | 200,0 ± 1 mm. Se medir M: `$S ppy=` 38,44 × 200 ÷ M |
| 13 | Papel reto | `$Y 200` com a folha encostada na guia esquerda | a borda continua paralela à guia (desvio menor que 1 mm) |
| 14 | Fim do curso | `$X 196` | o carro chega sem bater no esticador |

Depois de acertar, `$W` para gravar.

## 3. O ponto

Use papel de 120 g/m². O ponto se mede pelo relevo: empilhe 10 folhas sem ponto, meça com o paquímetro, e meça de
novo em cima de uma fileira de pontos. A diferença é a altura. Ou compare no tato com um texto braille de verdade.

| # | Teste | Como | Passa se |
|---|---|---|---|
| 15 | Batida parada | carro no meio, folha no lugar, `$P 1`, avançar `$Y 5`, repetir | ponto redondo, sem furo, de 0,4 a 0,6 mm |
| 16 | Escada de pulso | `$T 4` | 9 grupos de 4 pontos, feitos com 10, 15, 20 ... 50 ms. Escolha o menor tempo em que o ponto fica bom e some 5 ms: `$S ton=` |
| 17 | Celas cheias | `$T 1` | 30 celas iguais; 6,0 mm entre celas e 2,5 mm entre pontos (meça 10 celas: 60 mm) |
| 18 | Ida e volta | `$T 3` | as colunas das celas ímpares e pares ficam alinhadas na vertical. Se houver degrau maior que 0,2 mm: `$S vaievem=0` |
| 19 | Matriz não amassa | `$T 1` três vezes seguidas | os pontos da primeira linha continuam inteiros depois da terceira |
| 20 | Alfabeto | `$T 2` | 26 letras legíveis |

### Se o ponto ficar fraco

Mexa em uma coisa de cada vez, nesta ordem, e repita o teste 16:

1. Aumente `ton` até 40 ms.
2. Gire o estilete meia volta para fora (0,25 mm mais comprido).
3. Suba a tensão do step-up de 2 em 2 V, até 32 V.
4. Aumente o curso (solte o parafuso do teto uma volta): mais curso dá mais embalo.
5. Troque o papel: mais fino marca mais fácil, mas o ponto dura menos.
6. Plano B: solenoide de 12 V 2 A (documento 04).

### Se o ponto furar o papel

Ponta do estilete com canto vivo (lixe mais), estilete comprido demais (gire para dentro), ou tensão alta.

## 4. A folha inteira

| # | Teste | Como | Passa se |
|---|---|---|---|
| 21 | Carga automática | `$L` e encostar a folha nos roletes | a folha é puxada e para; a primeira linha sai a 12 mm da borda |
| 22 | Margem | imprimir "abc"; medir da borda esquerda até o primeiro ponto, do lado da leitura | 20 mm ± 1. Se medir M: `$S home=` 8 + M − 20 |
| 23 | Folha cheia | 23 linhas de `$T 1` (ou um texto longo pelo programa) | todas as linhas paralelas; a última começa a 232 mm do topo; a folha é ejetada |
| 24 | Tradutor | botão "Conferir tradutor" do programa (aba Impressora) | 17 frases iguais |
| 25 | Cancelar | no meio de uma linha, botão Cancelar | para em menos de 1 s, solenoide desligado |
| 26 | Sem papel | `$L` sem pôr folha | bipa a cada 3 s e desiste em 60 s com `erro: sem papel` |
| 27 | Resistência | 5 folhas cheias seguidas | nenhum ponto faltando; motores e solenoide mornos |

## 5. Leitura

O teste que vale é uma pessoa que lê braille ler a folha. Anote quantas palavras ela leu certo num texto de 50
palavras e o que achou do relevo. **Atenção:** na FEBRACE, pesquisa com participação de pessoas (mesmo só pedir
opinião) exige formulário próprio aprovado **antes** de começar. Confira o regulamento.

Sem leitor, compare no tato e na lupa com um impresso braille comercial, como uma caixa de remédio: mesma altura?
mesmo espaçamento?

## 6. Experimentos para o relatório

Cada um tem uma variável que vocês mudam, uma que medem, e o resto fica igual.

| Pergunta | Muda | Mede | Como |
|---|---|---|---|
| Qual o menor pulso que marca bem? | `ton` de 10 a 50 ms | altura do ponto | `$T 4`, um gráfico de altura por tempo |
| Quanto a tensão ajuda? | step-up em 12, 18, 24, 28 e 32 V | altura do ponto | `$T 1` em cada tensão; compare com a previsão de que a força cresce com V² |
| Qual papel segura melhor? | 90, 120, 150 e 180 g/m² | altura logo depois e depois de passar o dedo 20 vezes | mesma tensão e pulso |
| O vai e vem piora o alinhamento? | `vaievem` 0 e 1 | degrau entre fileiras (lupa e régua) e tempo da linha | `$T 3` |
| A velocidade afeta a posição? | `vx` de 60 a 200 | erro do passo em 10 celas | `$T 1` |

A primeira linha da tabela de tensão (12 V) reproduz a tensão da BrailleRAP original: mostra quanto o
nosso solenoide de 24 V perde se for ligado em 12 V.

## 7. Defeitos comuns

| Sintoma | Causa provável | O que fazer |
|---|---|---|
| Motor vibra e não gira | par de fios de bobina trocado | refazer o teste dos pares (documento 04) |
| Carro perde posição no meio da linha | correia frouxa, polia solta no eixo ou Vref baixo | apertar; conferir os parafusos allen das polias |
| Ponto só de um lado da folha | carros desalinhados numa ponta | etapa 8 do guia de montagem; igualar a tensão das correias |
| Ponto bom parado, fraco imprimindo | `toff` curto: o carro sai antes de o punção subir | aumentar `toff` para 40 |
| Papel torto | um pressor mais apertado que o outro | igualar as molas; conferir as guias |
| Papel não entra | O-ring abaixo da mesa ou pressor sem mola | o O-ring tem de aparecer 0,5 a 1 mm |
| Mega reinicia ao bater | queda de tensão ou falta do diodo D1 | conferir o diodo e o capacitor C1 |
| Solenoide zumbe e não solta | MOSFET em curto | desligar; testar a continuidade entre D8 − e GND com a placa desligada |
