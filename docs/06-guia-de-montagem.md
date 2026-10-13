# Guia de montagem

A ordem importa: algumas peças só entram antes de a caixa fechar. Cada etapa termina com uma conferência; não
passe para a próxima sem ela. Para ver onde cada peça fica, abra `cad/impressora_braille.FCStd` no FreeCAD ou o
simulador (`simulador/index.html`, com o controle "Explodir").

## Etapa 0: preparar as peças

1. **Meça** as peças da tabela "Medir antes de fabricar" (`03-projeto-mecanico.md`). Se algo for diferente, acerte
   `cad/parametros.py` e gere os arquivos de novo antes de imprimir ou cortar.
2. **Corte o gabarito de teste** de MDF e acerte as folgas (mesma seção do documento 03). Depois corte as 7 chapas.
3. **Imprima** as 38 peças. Em `cad/saida/mesas_250x250/` elas já estão arrumadas em duas mesas de 250 × 250 mm:
   abra `mesa_1.3mf` e `mesa_2.3mf` no fatiador (ou os `.stl`, se o seu não abrir 3MF). A mesa 1 tem as peças
   que trabalham sob carga; a mesa 2, os suportes. Para imprimir peça por peça, use `cad/saida/stl/`.
4. Passe uma broca de 3 mm nos furos passantes que ficaram apertados. Não passe broca nos furos de 2,7 mm: é neles que o parafuso abre rosca.
5. Teste: uma bucha LM8UU entra no furo dos carros com a mão, justa. Um eixo passa pelos furos das laterais.

### Fazer o estilete (punção)

1. Corte a cabeça de um parafuso M3 × 30. Deixe 22 mm de rosca.
2. Prenda o parafuso no mandril de uma furadeira, pelo lado cortado.
3. Com a furadeira girando, encoste a lima na ponta e faça um pino de **1,2 mm de diâmetro por 1,5 mm de comprimento**.
   Meça com o paquímetro.
4. Arredonde a ponta do pino com a lixa 400, ainda girando, até virar meia esfera lisa. Ponta com canto vivo fura o papel.

A matriz não precisa de preparo: é o parafuso allen sem cabeça M3 × 16 como vem.

## Etapa 1: conjuntos de bancada

**Carro do punção (laranja, o mais alto)**

1. Pelo lado de cima (o lado dos dois furinhos de 2,7 mm), ponha no furo do eixo de trás: bucha, espaçador curto, bucha.
   No furo da frente: espaçador longo, bucha, espaçador longo. O ressalto do fundo segura a primeira peça.
2. Feche cada furo com um parafuso M3 × 8 e arruela: a arruela cobre a borda da bucha.
3. Ponha o calço em U no deck, com a abertura virada para o lado do rasgo. Deslize o solenoide de lado para dentro
   do berço, com a haste roscada para baixo passando pelo rasgo do deck até o furo do meio. Aperte de leve os dois
   M3 × 12 da lateral.
4. Monte fora: a porca no estilete e o estilete no espaçador sextavado, com 13,5 mm para fora. Suba esse
   conjunto por baixo, pelo furo de 7 mm do patim, e rosqueie o espaçador na haste do êmbolo, uns 5 mm, segurando
   o êmbolo por cima. A porca trava depois da regulagem.
5. No teto: porca M3 no canal, parafuso M3 × 16 por cima, outra porca por cima do teto para travar.

Confira: o êmbolo sobe e desce livre com o dedo e volta sozinho pela mola. O estilete fica no meio do furo do patim.

**Carro da matriz (laranja, o mais baixo)**

1. Buchas e espaçadores como no outro carro, e os dois M3 × 8 com arruela.
2. Empurre uma porca M3 pelo canal lateral até o centro da torre.
3. Por cima, rosqueie o parafuso sem cabeça M3 × 16 com o sextavado para cima, até a ponta ficar 1 mm acima da torre.

**Torre do motor X (azul)**

1. Ponha um rolamento 608 na bolsa de cima.
2. Deixe o acoplamento solto dentro da gaiola, com o furo de 5 mm para baixo.
3. Suba o motor por baixo, com o eixo entrando no acoplamento, e prenda com quatro M3 × 8. Os dois de trás se
   alcançam pelos furos de acesso do assento do rolamento.
4. Aperte o parafuso do acoplamento no eixo do motor. O de cima fica para depois.

**Motor Y**: prenda o motor no suporte em L com quatro M3 × 8 e arruelas, no meio dos rasgos. Ponha a polia de furo
5 mm no eixo, com a flange para a ponta, sem apertar.

**Pressores (2)**: bucha impressa dentro de um 608; o 608 no garfo do braço, com M3 × 20 e porca travante; o braço
entre as orelhas da base, com M3 × 35 e porca travante, sem apertar a ponto de prender (ele tem de balançar); a mola
entre o braço e o teto da base, no pino-guia.

**Esticadores (2)**: polia lisa no garfo com M5 × 25 e porca travante M5; duas porcas M3 nos rasgos de cima do bloco.

**Eletrônica**: Mega na bandeja com quatro M3 × 8 (abrem rosca nos pilares); RAMPS encaixada no Mega; em cada soquete
X e Y, só o jumper MS3; drivers no sentido certo (documento 04, seção 5). Solde a placa do solenoide e a placa de
conectores conforme os esquemas.

## Etapa 2: fixar na base, na lateral esquerda e na parede traseira

Tudo aqui é mais fácil com as chapas ainda soltas, deitadas na mesa. Parafuso por fora, porca por dentro.

1. **Base**: bandeja do Mega (quatro M3 × 12), dois suportes de módulo (M3 × 10 por baixo, porca embutida em cima),
   suporte do motor Y (três M3 × 12). Prenda o step-up e a placa do solenoide nos suportes com abraçadeiras.
2. **Lateral esquerda** (o nome gravado fica do lado de dentro): torre do motor X (quatro M3 × 16), mancal superior
   (dois M3 × 16), suporte do fim de curso com a microchave (dois M3 × 16; a chave vai com dois M2 × 12).
3. **Parede traseira**: as duas bases dos pressores e o suporte do sensor de papel por dentro (M3 × 16), a placa de
   conectores por fora (quatro M3 × 16).

Confira: nenhuma cabeça de parafuso da base passa da saia das laterais (8 mm).

## Etapa 3: fechar a caixa

As laterais entram por último, porque as mesas atravessam a frente e a traseira.

1. Enfie a lingueta comprida da mesa traseira pela abertura da parede traseira, de dentro para fora. O recorte
   da mesa (passagem da polia) fica do lado esquerdo.
2. Encaixe a parede traseira nas linguetas de trás da base. Ponha os dois parafusos em T dessa junta, sem
   apertar: porca no recorte, M3 × 16 por fora.
3. Enfie a lingueta da mesa frontal pela abertura da parede frontal e encaixe a parede frontal na base, com os
   dois parafusos em T.
4. Ponha a correia fechada em volta da polia do motor Y e deixe pendurada.
5. Encaixe a lateral esquerda de lado: entram ao mesmo tempo as linguetas da base, da frente, da traseira e das
   duas mesas. Comece por baixo e vá subindo.
6. Faça o mesmo com a lateral direita.
7. Ponha os 12 parafusos em T das laterais e aperte os 16 aos poucos, em cruz. Aperto de mão: o MDF amassa.

Confira: a caixa não balança numa mesa plana; as duas mesas estão retas; a fenda entre elas tem 10 mm de ponta a ponta.

## Etapa 4: eixos e carros

1. Ponha o carro da matriz pela janela da frente e segure embaixo das mesas, com a torre na fenda. Enfie os dois eixos de baixo
   pela lateral direita, por dentro das buchas, até a lateral esquerda.
2. **Altura da matriz, agora que o carro de cima ainda não está no caminho:** apoie uma régua de aço na mesa da
   frente, atravessando a fenda. Suba a matriz com a chave allen de 1,5 mm até encostar na régua e depois desça
   quase meia volta (0,2 mm).
3. Faça o mesmo com o carro do punção e os dois eixos de cima.
4. Na lateral esquerda, feche as pontas dos eixos com duas travas (M3 × 16 e porca por dentro). Na direita, as
   travas ficam só encostadas por enquanto.

Confira: cada carro corre de ponta a ponta com um dedo, sem prender. Se prender, os furos das laterais estão
desalinhados ou há rebarba numa bucha.

## Etapa 5: eixo vertical

1. Ponha o segundo rolamento 608 na bolsa do mancal superior.
2. Desça o eixo de 103 mm por cima, passando nesta ordem: rolamento de cima, polia de cima (**cubo para cima**),
   fenda das mesas, polia de baixo (**cubo para baixo**), rolamento de baixo, e 11 mm para dentro do acoplamento.
3. Aperte o parafuso de cima do acoplamento.
4. Deixe as polias na altura dos eixos dos carros e aperte só a de baixo.

## Etapa 6: eixo do papel

1. Enfie o eixo de 366 mm pela lateral direita. Por dentro, ele passa nesta ordem: rolete da direita, rolete da
   esquerda, polia de furo 8 mm (dentro da correia fechada, com o cubo para a direita), anel de encosto.
2. Deixe 12 mm de eixo para fora na esquerda.
3. Por fora, em cada lado: rolamento 608 no eixo, mancal por cima, dois M3 × 20 com porca por dentro.
4. Centre cada rolete na sua janela da mesa e aperte o parafuso sem cabeça M3 × 8 (com a porca no rasgo). Vista os O-rings.
5. Alinhe as duas polias da correia fechada e aperte. Estique a correia descendo o motor Y nos rasgos.
6. Manípulo na ponta direita, com o M3 × 6 sem cabeça.

Confira: girando o manípulo, os dois roletes giram juntos e o motor acompanha. Os O-rings aparecem 0,5 a 1 mm acima
da mesa. Uma folha posta embaixo dos pressores é puxada reta.

## Etapa 7: correias dos carros

Para cada carro:

1. Passe a ponta da correia por dentro do carro, dê a volta no pino da esquerda com os dentes para dentro e prenda
   a ponta nela mesma com uma abraçadeira bem justa.
2. Leve a correia até a polia do eixo vertical, dê a volta, passe **por dentro do carro sem prender**, vá até a
   polia lisa do esticador, dê a volta e volte ao pino da direita. Corte a sobra e prenda com abraçadeira.
3. Ponha os dois M3 × 25 do esticador por fora da lateral direita, passando pela trava dos eixos, até as porcas do garfo.
4. Aperte os dois por igual até a correia soar grave ao ser beliscada, sem ficar esticada como corda de violão.

## Etapa 8: alinhar punção e matriz

Esta é a regulagem que decide a qualidade do ponto.

1. **Altura da matriz**: já foi regulada na etapa 4. Para retocar depois, solte os parafusos da polia de cima,
   afaste o carro de cima uns 6 cm, regule a matriz e refaça o passo 2.
2. **Alinhamento em X**: com a polia de cima solta no eixo, leve os carros para o meio. Aperte o êmbolo com o dedo e
   mexa o carro de cima até a ponta do estilete entrar no sextavado da matriz. Segurando assim, aperte a polia de cima.
3. Repita o teste do dedo perto da esquerda e perto da direita. Tem de entrar nos três lugares. Se não entrar numa
   ponta, uma das correias está mais frouxa que a outra.
4. **Alinhamento em Y**: se a ponta cai à frente ou atrás do furo, afrouxe os dois M3 × 12 do berço, desloque o
   solenoide e aperte. O berço tem 1,5 mm de folga para isso.
5. **Profundidade do punção**: sem papel, com o êmbolo todo embaixo, a ponta deve entrar de 0,6 a 0,8 mm no furo
   da matriz. O ajuste grosso é o estilete (13,5 mm para fora do espaçador, travado com a porca; dá para alcançar
   com dois alicates de bico pelas bocas do túnel da correia). O ajuste fino é o calço do solenoide: calço mais
   fino, ponto mais fundo. Imprima o calço com 3,5, 4,0 e 4,5 mm mudando a escala em Z no fatiador.
6. **Curso**: regule o parafuso do teto para a ponta do estilete ficar 3 mm acima da mesa em repouso.

## Etapa 9: fiação

Siga o documento 04. Passe os fios dos motores e do fim de curso pelo furo da mesa frontal, à esquerda. O cabo do
solenoide e os fios do sensor descem pelo furo da mesa traseira, à direita. O cabo do solenoide faz um arco de uns
18 cm por cima, preso no olhal do carro e numa abraçadeira nos furinhos do alto da parede traseira. Mova o carro de
ponta a ponta com a mão e veja se o cabo não estica nem enrosca nos pressores.

Depois disso, vá para `08-calibracao-e-testes.md`.
