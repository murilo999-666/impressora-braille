# Tabelas geradas pelo CAD

Arquivo gerado por `docs/gerar_tabelas.py` a partir de `cad/saida/lista_pecas.json`. Não edite à mão:
mude o CAD, rode `cad/rodar.sh gerar` e depois `python docs/gerar_tabelas.py`.

## Peças impressas em 3D

Medidas já na posição de impressão (largura × profundidade × altura). A massa considera 3 paredes e 30 % de
preenchimento (55 % do volume vira plástico). Todas saem sem suporte.

| Arquivo (`cad/saida/stl/`) | Qtd | Tamanho na mesa (mm) | Massa cada (g) | Pontes (mm²) |
|---|---:|---|---:|---:|
| `carro_puncao.stl` | 1 | 90 × 71 × 56 | 53.2 | 119 |
| `carro_matriz.stl` | 1 | 28 × 61 × 56 | 27.0 | 0 |
| `espacador_bucha_curto.stl` | 2 | 15 × 15 × 7 | 0.4 | 0 |
| `espacador_bucha_longo.stl` | 4 | 15 × 15 × 15 | 0.9 | 0 |
| `calco_solenoide.stl` | 1 | 22 × 25 × 4 | 1.1 | 0 |
| `torre_motor_x.stl` | 1 | 47 × 44 × 45 | 24.9 | 0 |
| `mancal_superior.stl` | 1 | 28 × 40 × 36 | 9.5 | 0 |
| `esticador.stl` | 2 | 26 × 18 × 29 | 5.1 | 65 |
| `trava_eixos.stl` | 4 | 14 × 62 × 4 | 2.1 | 0 |
| `mancal_eixo_papel.stl` | 2 | 50 × 30 × 10 | 4.1 | 0 |
| `anel_encosto.stl` | 1 | 14 × 14 × 5 | 0.4 | 0 |
| `rolete.stl` | 2 | 24 × 24 × 18 | 4.4 | 24 |
| `pressor_base.stl` | 2 | 26 × 32 × 38 | 5.6 | 0 |
| `pressor_braco.stl` | 2 | 17 × 36 × 21 | 4.4 | 23 |
| `bucha_608.stl` | 2 | 8 × 8 × 8 | 0.2 | 0 |
| `manipulo.stl` | 1 | 39 × 39 × 14 | 6.5 | 14 |
| `suporte_motor_y.stl` | 1 | 62 × 52 × 38 | 16.1 | 0 |
| `guia_papel_esq.stl` | 1 | 16 × 90 × 14 | 4.9 | 0 |
| `guia_papel_dir.stl` | 1 | 16 × 90 × 14 | 4.9 | 0 |
| `suporte_fim_de_curso.stl` | 1 | 26 × 17 × 33 | 4.4 | 0 |
| `suporte_sensor_papel.stl` | 1 | 28 × 40 × 28 | 5.0 | 70 |
| `bandeja_mega.stl` | 1 | 61 × 104 × 8 | 8.4 | 0 |
| `suporte_modulo.stl` | 2 | 52 × 30 × 4 | 4.0 | 0 |
| `placa_conectores.stl` | 1 | 64 × 40 × 3 | 4.7 | 0 |

**Total: 38 peças de 24 modelos, cerca de 239 g de filamento** (compre 1 rolo de 1 kg: sobra para repetir peças).

## Chapas de MDF (corte a laser)

| Arquivo (`cad/saida/corte_laser/`) | Tamanho (mm) | Contornos | Área (cm²) |
|---|---|---:|---:|
| `lateral_esquerda.dxf` / `.svg` | 178 × 236 | 39 | 395 |
| `lateral_direita.dxf` / `.svg` | 178 × 236 | 31 | 396 |
| `parede_frontal.dxf` / `.svg` | 330 × 236 | 8 | 572 |
| `parede_traseira.dxf` / `.svg` | 330 × 236 | 27 | 699 |
| `base.dxf` / `.svg` | 330 × 162 | 22 | 493 |
| `mesa_traseira.dxf` / `.svg` | 330 × 193 | 9 | 512 |
| `mesa_frontal.dxf` / `.svg` | 330 × 99 | 2 | 294 |

Área de MDF nas peças: 3361 cm² (0.34 m²). Pranchas prontas: 3 de 600 × 400 mm, 2 de 900 × 600 mm.

## Parafusos, porcas e arruelas (contagem exata do modelo)

| Item | Qtd no modelo | Compre |
|---|---:|---:|
| Arruela lisa M3 | 12 | 15 |
| Parafuso M2 x 12 (philips) | 4 | 6 |
| Parafuso M3 x 10 (allen) | 2 | 4 |
| Parafuso M3 x 12 (allen) | 9 | 11 |
| Parafuso M3 x 16 (allen) | 43 | 52 |
| Parafuso M3 x 20 (allen) | 6 | 8 |
| Parafuso M3 x 25 (allen) | 4 | 6 |
| Parafuso M3 x 35 (allen) | 2 | 4 |
| Parafuso M3 x 6 (sem cabeca) | 1 | 3 |
| Parafuso M3 x 8 (allen) | 12 | 15 |
| Parafuso M3 x 8 (philips) | 4 | 6 |
| Parafuso M3 x 8 (sem cabeca) | 2 | 4 |
| Parafuso M5 x 25 (allen) | 2 | 4 |
| Porca M3 (borboleta) | 4 | 6 |
| Porca M3 (sextavada) | 62 | 75 |
| Porca M3 (travante) | 4 | 6 |
| Porca M5 (travante) | 2 | 4 |

A coluna Compre soma 20 % de folga (no mínimo 2 a mais).

### Onde vai cada parafuso

- **Parafuso M3 x 10**: 2 em suporte de modulo na base.
- **Parafuso M3 x 12**: 2 em aperta o solenoide; 3 em suporte do motor Y na base; 4 em bandeja do Mega na base.
- **Parafuso M3 x 16**: 1 em batente do embolo (regula o curso); 4 em torre do motor X; 2 em mancal superior; 4 em trava dos eixos; 4 em base do pressor; 4 em guia do papel; 2 em suporte do fim de curso; 2 em suporte do sensor de papel; 4 em placa de conectores; 4 em junta em T lateral-base; 8 em junta em T lateral-frente/tras; 4 em junta em T frente/tras-base.
- **Parafuso M3 x 20**: 4 em mancal do eixo do papel; 2 em eixo do 608 do pressor.
- **Parafuso M3 x 25**: 4 em esticador da correia.
- **Parafuso M3 x 35**: 2 em pino do braco do pressor.
- **Parafuso M3 x 6**: 1 em trava do manipulo.
- **Parafuso M3 x 8**: 4 em trava das buchas; 4 em motor X na torre; 2 em trava do rolete; 4 em motor Y; 4 em Mega na bandeja.
- **Parafuso M5 x 25**: 2 em eixo da polia tensora.

## Peças do estoque e compradas que aparecem no modelo

| Peça | Qtd |
|---|---:|
| Bucha linear LM8UU | 6 |
| Solenoide JF-0826B 24 V | 1 |
| Estilete: parafuso M3 sem cabeca, ponta arredondada | 1 |
| Espacador sextavado M3 femea-femea 15 mm | 1 |
| Matriz: parafuso allen sem cabeca M3 x 16 | 1 |
| Eixo retificado 8 mm x 330 | 4 |
| Eixo retificado 8 mm x 103 | 1 |
| Polia GT2 20 dentes furo 8 | 3 |
| Rolamento 608 | 6 |
| Acoplamento flexivel 5 x 8 | 1 |
| Motor NEMA 17 17HS4401 | 2 |
| Polia lisa GT2 furo 5 (tensora) | 2 |
| Correia GT2 6 mm aberta (650 mm) | 2 |
| Eixo retificado 8 mm x 366 | 1 |
| O-ring 20 x 3 mm | 2 |
| Mola de compressao (de caneta) 4,5 x 20 mm | 2 |
| Polia GT2 20 dentes furo 5 | 1 |
| Correia GT2 fechada 200 mm | 1 |
| Microchave KW11-3Z (fim de curso) | 2 |
| Arduino Mega 2560 | 1 |
| RAMPS 1.4 | 1 |
| Driver DRV8825 | 2 |
| Modulo step-up XL6009 | 1 |
| Placa do solenoide (perfurada 4 x 2,5 cm) | 1 |
| Jack P4 femea de painel 5,5 x 2,1 mm | 1 |
| Chave alavanca 2 posicoes (liga/desliga) | 1 |
| Porta-fusivel de painel 5 x 20 mm + fusivel 3 A | 1 |
| Papel braille 120-180 g/m2 | 1 |

## Números da máquina

| Grandeza | Valor |
|---|---|
| Tamanho externo (L × P × A) | 330 × 178 × 236 mm (sem as bandejas) |
| Curso útil do carro (X) | 196 mm |
| Margem mínima à esquerda / direita da folha A4 | 8 mm / 6 mm |
| Celas por linha (máximo mecânico) | 33 |
| Passos por mm no X (1/16 de passo, polia de 20 dentes) | 80.00 |
| Passos por mm no papel (rolete de 26,5 mm) | 38.44 |
| Distância do rolete até a linha de punção | 48 mm |
| Comprimento do laço de cada correia do X | 586 mm (corte 650 mm para sobrar ponta) |
