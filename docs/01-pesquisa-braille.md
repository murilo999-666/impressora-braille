# Pesquisa: o braille e as impressoras braille

## 1. O que é

O braille é um sistema de escrita em relevo para leitura com a ponta dos dedos. Foi criado pelo francês Louis
Braille (1809 a 1852), que ficou cego na infância. Ele publicou a primeira versão em 1829 e a forma definitiva em
1837. Quem trouxe o sistema ao Brasil foi José Álvares de Azevedo, um jovem cego que estudou em Paris e voltou em
1850. Em 1854 foi fundado no Rio de Janeiro o Imperial Instituto dos Meninos Cegos, hoje Instituto Benjamin Constant
(IBC). O Dia Mundial do Braille é 4 de janeiro (nascimento de Louis Braille) e o Dia Nacional do Braille é 8 de abril
(nascimento de José Álvares de Azevedo).

## 2. A cela

Tudo é escrito com uma **cela** de seis pontos, em duas colunas de três. Os pontos têm número fixo:

```
1 ● ● 4
2 ● ● 5
3 ● ● 6
```

Cada ponto pode estar em relevo ou não. São 2⁶ = 64 combinações: 63 sinais mais a cela vazia, que é o espaço. Um
caractere é descrito pelos pontos que tem. Exemplos: a = ponto 1; b = pontos 1 e 2; c = pontos 1 e 4.

As 26 letras seguem uma lógica de séries, que ajuda a decorar e também a conferir uma tabela:

| Série | Regra | Sinais |
|---|---|---|
| 1ª | só os pontos de cima (1, 2, 4, 5) | a b c d e f g h i j |
| 2ª | 1ª série + ponto 3 | k l m n o p q r s t |
| 3ª | 1ª série + pontos 3 e 6 | u v x y z ç é á è ú |
| 4ª | 1ª série + ponto 6 | â ê ì ô ù à ï ü õ w |
| 5ª | 1ª série rebaixada (pontos 2, 3, 5, 6) | pontuação: , ; : ? ! e outros |

O w ficou na 4ª série porque não existia no alfabeto francês da época.

## 3. O braille do português

A norma em vigor no Brasil e em Portugal é a **Grafia Braille para a Língua Portuguesa** (Ministério da Educação,
3ª edição, 2018; a 1ª é de 2002, aprovada pela Portaria nº 2.678). O braille do português usado em livros e na escola
é **integral (grau 1)**: cada letra do texto vira uma cela, sem abreviaturas. É esse que a impressora escreve.

### Letras acentuadas

No português, cada letra acentuada tem uma cela própria (não se escreve "acento + letra"):

| Letra | Pontos | Letra | Pontos | Letra | Pontos |
|---|---|---|---|---|---|
| á | 1 2 3 5 6 | é | 1 2 3 4 5 6 | í | 3 4 |
| à | 1 2 4 6 | ê | 1 2 6 | ó | 3 4 6 |
| â | 1 6 | ç | 1 2 3 4 6 | ô | 1 4 5 6 |
| ã | 3 4 5 | ú | 2 3 4 5 6 | õ | 2 4 6 |
| ü | 1 2 5 6 | | | | |

### Maiúsculas

- Uma letra maiúscula: o sinal de maiúscula (pontos 4 6) antes dela. "Brasil" = (46) b r a s i l.
- Palavra toda em maiúsculas: o sinal duas vezes antes da palavra. "FEBRACE" = (46)(46) f e b r a c e.
- Mais de três palavras seguidas em maiúsculas: (25)(46)(46) antes da primeira e (46)(46) antes da última.

### Números

Os algarismos usam as mesmas celas das letras a até j, precedidas do **sinal de número** (pontos 3 4 5 6):
1 = a, 2 = b, ... 9 = i, 0 = j. O sinal vale para o número inteiro: "2026" = (3456) b j b f.

- Vírgula decimal: ponto 2. Ponto de milhar: ponto 3. Os dois continuam o número sem repetir o sinal.
- Se logo depois do número vier uma letra de a até j, põe-se o ponto 5 antes dela, para não ser lida como algarismo.

### Pontuação mais usada

| Sinal | Pontos | Sinal | Pontos |
|---|---|---|---|
| vírgula | 2 | ponto final | 3 |
| ponto e vírgula | 2 3 | dois-pontos | 2 5 |
| interrogação | 2 6 | exclamação | 2 3 5 |
| hífen | 3 6 | travessão | (36)(36) |
| aspas | 2 3 6 | reticências | (3)(3)(3) |
| abre parêntese | (126)(3) | fecha parêntese | (6)(345) |
| asterisco | 3 5 | barra | (6)(2) |
| arroba | 1 5 6 | por cento | (456)(356) |

A tabela completa que a impressora usa está em `software/braille-pt.js`. Ela foi conferida de três jeitos: pela
regra das séries, pelo texto da Grafia e pela tabela `pt-pt-g1.utb` do liblouis, o tradutor livre usado pelos
leitores de tela.

### O que a impressora não faz

Matemática (Código Matemático Unificado), música, química, braille abreviado (grau 2) e os números ordinais na forma
oficial (7º vira "7o"). Para isso existem programas como o Braille Fácil (feito no NCE/UFRJ e distribuído pelo IBC).
Um programa desses pode mandar as celas prontas para a impressora pelo comando `$C`.

## 4. Medidas do braille

O que importa para ler com o dedo é o espaçamento. As medidas variam pouco de um padrão para outro:

| Medida | Papel (padrão europeu) | Faixa usual em papel | Sinalização (NBR 9050) |
|---|---|---|---|
| Entre pontos da mesma cela | 2,5 mm | 2,3 a 2,5 mm | 2,7 mm |
| Entre celas | 6,0 mm | 6,0 a 6,2 mm | 6,6 mm |
| Entre linhas | 10,0 mm | 10,0 mm | 10,8 mm |
| Diâmetro da base do ponto | 1,5 ± 0,25 mm | | 2,0 mm |
| Altura do ponto | 0,5 ± 0,1 mm | 0,25 a 0,53 mm | 0,65 mm |

Fontes: norma britânica da UKAAF para o papel; faixa usual citada pela ViewPlus, fabricante de impressoras braille;
os valores de sinalização são os de um memorial descritivo que segue a NBR 9050 (não consegui acesso ao texto da
norma para conferir: se for citar no relatório, confira na norma).

A impressora usa 2,5, 6,0 e 10,0 mm. Os três valores são parâmetros do firmware (`ponto`, `cela`, `linha`).

**Meta de qualidade do projeto:** ponto com 0,4 a 0,6 mm de altura, base de 1,3 a 1,7 mm, sem furar o papel.

## 5. Como se produz braille

| Jeito | Como funciona | Limitação |
|---|---|---|
| Reglete e punção | A pessoa fura ponto por ponto, de trás para frente e espelhado, com o papel numa régua com celas | lento; exige escrever espelhado |
| Máquina Perkins | Seis teclas, uma por ponto; cada apertada faz uma cela inteira | manual; cara |
| Impressora braille | Martelos movidos por solenoides batem o papel contra uma matriz | a partir de alguns milhares de dólares |
| Linha braille | Pinos que sobem e descem formam uma linha de texto que muda | não deixa registro em papel |

### Como uma impressora braille marca o ponto

O ponto é uma deformação permanente do papel entre duas ferramentas: um **punção** (macho, de ponta arredondada) e
uma **matriz** (fêmea, uma cavidade). O punção empurra o papel para dentro da cavidade além do limite elástico das
fibras, e o relevo fica.

- As impressoras comerciais têm uma fileira de martelos e marcam vários pontos de uma vez.
- As de baixo custo, como a BrailleRAP e esta, têm **um punção só**, que anda de ponto em ponto. São lentas, mas têm
  poucas peças. A BrailleRAP custa perto de 250 dólares em peças, segundo os autores.
- Quem movimenta o punção é um solenoide: uma bobina que, energizada, puxa um núcleo de ferro. A força cresce com o
  quadrado da corrente e é maior no fim do curso.

Nesta máquina a matriz é o furo sextavado de 1,5 mm de um parafuso allen sem cabeça M3, ideia da BrailleRAP. O
punção tem a ponta de 1,2 mm: 1,2 + 2 × 0,16 (espessura do papel de 120 g) = 1,5 mm, que é o que cabe no furo.

### Papel

O braille precisa de papel mais grosso que o sulfite comum de 75 g/m², que não segura o relevo. O usual é de
120 a 180 g/m². Para os testes, sulfite de 120 g/m² e papel de 150 ou 180 g/m² resolvem.

## 6. Por que o projeto importa

No Censo de 2010 do IBGE, cerca de 6,5 milhões de brasileiros declararam deficiência visual severa, dos quais perto
de 500 mil não enxergam nada. Uma impressora braille comercial custa mais do que a maioria das escolas pode pagar,
então professores e alunos cegos dependem de centros de produção e de prazo. Uma impressora que uma escola consegue
montar com cortadora a laser e impressora 3D, por uma fração do preço, reduz essa dependência para textos curtos:
etiquetas, avisos, provas, listas de exercícios.

(Confira os números do Censo na fonte antes de pôr no relatório. O Censo de 2022 mudou a forma da pergunta.)

## 7. Fontes

- Grafia Braille para a Língua Portuguesa, 3ª ed., MEC, 2018: <https://www.gov.br/ibc/pt-br/pesquisa-e-tecnologia/materiais-especializados-1/livros-em-braille-1/o-sistema-braille-arquivos/grafia-braille-para-a-lingua-portuguesa-pdf.pdf>
- Normas Técnicas para a Produção de Textos em Braille, 3ª ed., MEC, 2018 (mesma página do IBC).
- Tabela `pt-pt-g1.utb` do liblouis: <https://github.com/liblouis/liblouis/blob/master/tables/pt-pt-g1.utb>
- UKAAF, Braille Standard Dimensions: <https://www.ukaaf.org/wp-content/uploads/2020/03/Braille-Standard-Dimensions.pdf>
- ViewPlus, sobre faixas de medidas: <https://viewplus.com/braille-innovations-and-over-specified-standards/>
- BrailleRAP, documentação e lista de materiais: <https://braillerap-en.readthedocs.io/en/latest/>
- Dados do solenoide JF-0826B (revendedor): <https://makerselectronics.com/product/push-type-linear-solenoid-jf-0826b-24v-350ma-10mm-20n/>
