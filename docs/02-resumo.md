# Resumo do projeto em uma página

**O quê.** Uma impressora braille para folha A4, feita com MDF cortado a laser, peças impressas em 3D, um Arduino
Mega com RAMPS 1.4, dois motores de passo e um solenoide.

**Para quê.** Impressoras braille comerciais custam milhares de dólares. Uma escola com cortadora a laser e
impressora 3D consegue fazer esta com peças de impressora 3D comum.

**De onde veio.** Do projeto aberto BrailleRAP: tiramos os arquivos dos repositórios públicos dele e melhoramos o
projeto. A eletrônica, os motores e os eixos foram comprados a preço de sucata na Lixotec, em Foz do Iguaçu.

**O que descobrimos.** O nosso solenoide é a versão de 24 V, e a BrailleRAP usa a de 12 V. A potência cai com o
quadrado da tensão: em 12 V sobrariam 2,1 W dos 24 W que o projeto original usa. O mecanismo serve; faltaria força.

**O que mudou.**

1. O solenoide passou a ter alimentação própria de 24 a 32 V, por um conversor step-up de poucos reais.
2. O punção bate de cima para baixo. O solenoide fica à vista e a folha fica apoiada na mesa na hora da batida.
3. Os quatro eixos dos carros passam pelos mesmos furos das laterais de MDF: o alinhamento sai do corte a laser.
4. Os roletes ficam antes do punção e a mesa da frente é 1 mm mais baixa: nada amassa o ponto pronto.
5. A caixa é parafusada, não colada.
6. Sensor de papel, buzzer e botões, pensando em quem opera sem enxergar.
7. Firmware próprio e um programa no navegador que abre arquivos do Word e PDF, traduz para o braille do português
   e formata as folhas pelas normas brasileiras.

**Como funciona.** A folha entra por trás e é empurrada por dois roletes. Dois carros andam juntos, um em cima e um
embaixo da folha, puxados por correias ligadas ao mesmo eixo. O de cima leva o solenoide com um punção de 1,2 mm; o
de baixo leva a matriz, que é o furo sextavado de um parafuso M3. Para cada linha de texto a máquina faz três
passadas (as três fileiras de pontos da cela) e avança o papel 2,5 mm entre elas.

**Números.** 330 × 178 × 236 mm. 30 celas por linha, 23 linhas por folha. Cela de 2,5 / 6 / 10 mm. Cerca de 8 pontos
por segundo. 7 chapas de MDF de 6 mm, 38 peças impressas (240 g), 12 V e 2,3 A de pico.

**O que está pronto.** Projeto completo e verificado no computador: modelo 3D sem interferências, arquivos de corte
e de impressão, esquema elétrico, firmware que compila, programa com 100 testes automáticos, simulador 3D.

**O que falta.** Fabricar, montar, calibrar e medir a altura do ponto. O plano está em `09-plano-de-tarefas.md`.

**Limites.** É lenta (um ponto por vez). Não imprime os últimos 48 mm da folha. Só faz braille integral de texto:
nada de matemática ou música.
