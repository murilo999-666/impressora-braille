# Plano de tarefas

Legenda: **[x]** feito e conferido no computador (a coluna da direita diz como). **[ ]** falta, depende de vocês e da máquina.

## Parte A: projeto (feito)

| | Tarefa | Como foi conferido |
|---|---|---|
| [x] | Estudar o projeto BrailleRAP | lista de materiais da BrailleRAP conferida com as peças compradas: mesmos eixos (4 × 330, 1 × 365, 1 × 100), mesmas polias |
| [x] | Conferir o solenoide | etiqueta do solenoide (24 V, 350 mA) contra o especificado pela BrailleRAP (12 V, 2 A): em 12 V seriam 2,1 W contra 24 W |
| [x] | Pesquisa sobre braille | `01-pesquisa-braille.md`; tabela conferida com a Grafia de 2018 e com o liblouis |
| [x] | Arquitetura com punção de cima para baixo | `03-projeto-mecanico.md` |
| [x] | Medidas num arquivo só | `cad/parametros.py` |
| [x] | Modelar as peças do estoque | motores, eixos, buchas, rolamentos, polias, acoplamento, solenoide, Mega e RAMPS |
| [x] | Modelar 24 peças impressas | cada uma vira sólido válido e malha fechada (coluna "ok" do resumo de `cad/saida/resumo_geracao.txt`) |
| [x] | Modelar 7 chapas de MDF com encaixes | linguetas e rasgos gerados dos mesmos números; furos gerados pelos suportes |
| [x] | Procurar interferências | 276 peças, cerca de 460 pares por posição, carros em x = 62, 150 e 258 mm, punção embaixo, e varredura do curso de 7 em 7 mm: 0 problemas (`cad/relatorio_verificacao.txt`) |
| [x] | Orientar as peças para imprimir sem suporte | área de ponte medida por peça; a que mais tem (carro do punção) soma 119 mm², em vãos de até 18 mm |
| [x] | Exportar STL e STEP | `cad/saida/stl/`, `cad/saida/step/` |
| [x] | Exportar DXF e SVG das chapas e montar pranchas | conferido em imagem: contornos fechados, furos e nomes no lugar |
| [x] | Gabarito de teste do laser | `cad/saida/corte_laser/gabarito_teste.*` |
| [x] | Arquivo do FreeCAD com cores | `cad/impressora_braille.FCStd` |
| [x] | Esquema elétrico | `eletrica/esquema_ligacao.png` e `esquema_solenoide.png`; pinos iguais aos de `config.h` |
| [x] | Contas de corrente, potência e aquecimento | `04-esquema-eletrico.md` |
| [x] | Tradutor texto para braille | 52 testes automáticos |
| [x] | Cálculo da página e da ordem dos pontos | mesmos testes; página cheia cabe no curso e no alcance do rolete |
| [x] | Firmware | compila para o Mega 2560 sem avisos; 18,4 kB de 254 kB |
| [x] | Pesquisa sobre a formatação do braille | Normas Técnicas (MEC) e Grafia Braille lidas no original; regras e fontes em `11-programa-relevo.md` |
| [x] | Programa Relevo: importa .docx, .pdf, .txt, .odt, .html, .md e .brf | 48 testes automáticos, entre eles um .docx montado na hora; um PDF real de 73 páginas virou 134 folhas sem erro |
| [x] | Formatador: título, parágrafo, itens, versos, destaque, paginação | mesmos testes; cada regra tem um teste com a norma citada |
| [x] | Tela do programa | abre no Edge; pré-visualização conferida em imagem |
| [x] | Mesas de impressão de 250 × 250 mm | 38 peças em 2 mesas; o script confere que nenhuma sai da mesa nem encosta em outra |
| [x] | Página do projeto e repositório público | `index.html`, `README.md` |
| [x] | Simulador 3D | abre no Edge; carro, êmbolo, papel e pontos animados a partir do modelo do CAD |
| [x] | Lista de compras | parafusos contados pelo modelo |
| [x] | Guia de montagem, calibração e testes | documentos 06 e 08 |

## Parte B: fabricação (falta)

Faça na ordem. Cada linha é uma tarefa pequena.

| | Tarefa | Pronto quando |
|---|---|---|
| [ ] | B1. Confirmar no site oficial o prazo da FEBRACE | data e hora anotadas |
| [ ] | B2. Medir o solenoide, contar dentes das polias e da correia fechada, medir o MDF | tabela "Medir antes de fabricar" preenchida |
| [ ] | B3. Se alguma medida mudou: acertar `parametros.py`, `./rodar.sh verificar` e `./rodar.sh gerar` | 0 problemas |
| [ ] | B4. Confirmar o tipo de driver (DRV8825 ou A4988) | serigrafia lida |
| [ ] | B5. Fazer os orçamentos e comprar | itens do documento 05 em mãos |
| [ ] | B6. Cortar e testar o gabarito do laser | eixo entra justo; lingueta entra com a mão |
| [ ] | B7. Cortar as 7 chapas | todas com o nome gravado ou escrito a lápis |
| [ ] | B8. Imprimir as 38 peças | conferidas contra `tabelas-geradas.md` |
| [ ] | B9. Fazer o estilete | pino de 1,2 mm, ponta lisa |

## Parte C: eletrônica na bancada (falta)

| | Tarefa | Pronto quando |
|---|---|---|
| [ ] | C1. Regular o step-up em 24,0 V | teste 2 |
| [ ] | C2. Soldar a placa do solenoide | diodo e capacitor no sentido certo |
| [ ] | C3. Gravar o firmware | mensagem de pronta no Monitor Serial |
| [ ] | C4. Jumpers e Vref dos drivers | teste 5 |
| [ ] | C5. Testar solenoide, motores e chaves soltos | testes 3, 4, 6 e 7 |

## Parte D: montagem (falta)

| | Tarefa | Pronto quando |
|---|---|---|
| [ ] | D1. Conjuntos de bancada (carros, torre, pressores, esticadores) | conferências da etapa 1 |
| [ ] | D2. Fixar suportes na base, lateral esquerda e parede traseira | etapa 2 |
| [ ] | D3. Fechar a caixa | não balança; fenda de 10 mm por igual |
| [ ] | D4. Eixos e carros | os dois carros correm com um dedo |
| [ ] | D5. Eixo vertical e eixo do papel | giram livres |
| [ ] | D6. Correias | tensionadas por igual |
| [ ] | D7. Alinhar punção e matriz | a ponta entra no sextavado na esquerda, no meio e na direita |
| [ ] | D8. Fiação | conferência da seção 6 do documento 04 |

## Parte E: calibração e dados (falta)

| | Tarefa | Pronto quando |
|---|---|---|
| [ ] | E1. Movimento | testes 8 a 14 |
| [ ] | E2. Ponto | testes 15 a 20 |
| [ ] | E3. Folha inteira | testes 21 a 27 |
| [ ] | E4. Experimentos | tabelas e gráficos da seção 6 do documento 08 |
| [ ] | E5. Leitura por quem lê braille | só com o formulário da FEBRACE aprovado antes |
| [ ] | E6. Fotos e vídeo de cada etapa | diário de bordo em dia |

## O que pode dar errado e o que fazer

| Risco | Chance | Se acontecer |
|---|---|---|
| Solenoide de 24 V fraco mesmo em 32 V | média | plano B: JF-0826B de 12 V 2 A; o berço é o mesmo |
| Ponta do êmbolo sem rosca M3 | baixa | me avise com uma foto: desenho um adaptador de aperto |
| Medidas do solenoide diferentes do catálogo | média | mudar `SOL_L`, `SOL_W`, `SOL_H` e imprimir só o carro de cima |
| Papel escorregando nos roletes | média | mola mais forte nos pressores; limpar os O-rings com álcool |
| MDF empenado abrindo a fenda | baixa | os parafusos em T puxam; se preciso, uma travessa colada embaixo da mesa |
| Furos dos eixos folgados no laser | média | é para isso o gabarito: escolher entre 7,9, 8,0 e 8,1 mm |
