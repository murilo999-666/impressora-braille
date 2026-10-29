# Lista de compras

As quantidades de parafusos, peças impressas e chapas saem direto do modelo 3D e estão em
[`tabelas-geradas.md`](tabelas-geradas.md). Aqui está o resumo do que vocês já têm e do que falta.

Não coloquei preço: muda toda semana e eu não tenho como conferir daqui. A coluna fica para vocês preencherem com
três orçamentos. O total entra no relatório da feira como custo do protótipo.

## 1. O que já está no estoque e onde entra

| Peça do estoque | Qtd | Uso neste projeto |
|---|---:|---|
| Arduino Mega 2560 | 1 | controle |
| RAMPS 1.4 | 1 | drivers, MOSFET do solenoide, bornes |
| Driver de motor (DRV8825, confirmar) | 2 | motor X e motor Y |
| Motor NEMA 17 17HS4401 | 2 | X (carros) e Y (papel) |
| Solenoide JF-0826B 24 V 350 mA | 1 | punção |
| Eixo retificado 8 mm × 330 mm | 4 | dois para o carro de cima, dois para o de baixo |
| Eixo retificado 8 mm × 366 mm | 1 | eixo dos roletes do papel |
| Eixo retificado 8 mm × 103 mm | 1 | eixo vertical que sincroniza os carros |
| Bucha linear LM8UU (15 mm por fora) | 6 | três em cada carro |
| Rolamento 608 (8 × 22 × 7) | 4 | dois no eixo vertical, dois no eixo do papel |
| Polia GT2 20 dentes, furo 8 mm | 3 | duas no eixo vertical, uma no eixo do papel |
| Polia GT2 20 dentes, furo 5 mm | 1 | motor Y |
| Polia lisa GT2, furo 5 mm | 2 | tensoras das duas correias |
| Acoplamento flexível 5 × 8 mm | 1 | motor X no eixo vertical |
| Fim de curso (microchave) | 1 | referência do carro |
| Correia GT2 fechada | 1 | motor Y (confirmar que tem 100 dentes = 200 mm) |
| Correia GT2 aberta | ? | servem se houver dois pedaços de 650 mm |
| Roletes impressos com anel de vedação | 2 | **não entram**: são pequenos para este projeto |

Tudo o que vocês listaram é aproveitado, menos os dois roletes impressos.

## 2. Obrigatório comprar

| Qtd | Item | Por quê | Preço |
|---:|---|---|---|
| 1 | Fonte 12 V 5 A com plugue P4 5,5 × 2,1 mm | pico de 2,3 A com folga de 2 vezes | |
| 1 | Módulo step-up XL6009 | o solenoide é de 24 V; em 12 V tem 1/4 da potência nominal | |
| 1 | Kit da placa do solenoide: capacitor 1000 µF 50 V, diodo 1N4007, resistores 10 kΩ e 2,2 kΩ, LED 5 mm, placa perfurada | sem o diodo o MOSFET da RAMPS queima | |
| 1 | Jack P4 de painel, chave alavanca, porta-fusível 5 × 20 e 3 fusíveis de 3 A | entrada de energia segura na parede traseira | |
| 2 | Rolamento 608ZZ | roletes de pressão do papel | |
| 2 | O-ring 20 × 3 mm (compre 4) | borracha dos roletes de tração | |
| 2 | Mola de compressão de caneta esferográfica (cerca de 4,5 × 20 mm) | pressão dos roletes | |
| 1,5 m | Correia GT2 de 6 mm, aberta | dois pedaços de 650 mm, se as que vocês têm forem curtas | |
| 1 | Espaçador sextavado de latão M3 fêmea-fêmea, 15 mm | liga o êmbolo ao estilete | |
| 2 | Parafuso allen sem cabeça M3 × 16 | matriz (um de reserva) | |
| 2 | Parafuso M3 × 30 | para fazer o estilete: corta-se a cabeça e afina-se a ponta (um de reserva) | |
| | Parafusos, porcas e arruelas M3, M5 e M2 | quantidades em `tabelas-geradas.md` | |
| 3 | Chapa de MDF cru de 6 mm, 600 × 400 mm (ou 2 de 900 × 600) | estrutura | |
| 1 | Rolo de filamento PLA de 1 kg | usa 240 g, em duas mesas de 250 × 250 mm | |
| 1 m | Cabo flexível 2 × 0,5 mm² e 1 m de cabo 2 × 1,0 mm² | solenoide e 12 V | |
| 20 | Abraçadeira de nylon de 2,5 mm | pontas das correias e cabos | |
| 1 | Pacote de papel A4 de 120 g/m² e algumas folhas de 150 ou 180 g/m² | o de 75 g não segura o ponto | |

## 3. Recomendado

| Qtd | Item | Por quê |
|---:|---|---|
| 1 | Microchave KW11-3Z com haste e 4 parafusos M2 × 12 | sensor de papel: carrega a folha sozinho e avisa quando falta. Sem ele o firmware funciona com `$S sensor=0`, mas a pessoa tem de avisar pelo botão |
| 1 | Buzzer passivo 5 V e resistor de 100 Ω | avisos sonoros de pronto, fim e erro: essencial para um operador cego |
| 3 | Botão tátil de 12 mm | carregar, testar e cancelar sem computador |
| 4 | Pé de borracha adesivo | a batida do solenoide faz a caixa andar na mesa |
| 1 | Cabo USB A para B | se não vier com o Mega |

## 4. Opcional

| Item | Quando vale |
|---|---|
| 2 LEDs (verde e vermelho) e 2 resistores de 330 Ω | estado visível de longe |
| Solenoide JF-0826B de 12 V 2 A | plano B, se o ponto ficar baixo mesmo com 32 V |
| Placa de acrílico de 3 mm, 330 × 178 mm | tampa transparente: protege os dedos do público na feira e deixa ver o mecanismo |
| Filamento PETG | para os dois carros e os braços do pressor, que trabalham sob carga |
| Graxa branca ou óleo fino | eixos e buchas |

## 5. Ferramentas

Multímetro (sem ele não dá para regular o step-up nem os drivers), chaves allen de 1,5, 2 e 2,5 mm, chave philips
pequena, alicate de corte, ferro de solda, lima fina e lixa 400, furadeira (para girar o parafuso enquanto afina a
ponta do estilete), paquímetro, arco de serra ou mini retífica para cortar a cabeça do parafuso.
