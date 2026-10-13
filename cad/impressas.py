# -*- coding: utf-8 -*-
"""Pecas impressas em 3D. Cada funcao devolve o solido ja na posicao da maquina.
As pecas foram pensadas para imprimir SEM suporte (veja ORIENTACAO em maquina.py)."""
import math
import parametros as P
from fc_util import *

ZP = P.Z_P
MEIO_BLOCO = 10.5         # meia-secao do bloco que abraca a bucha LM8UU
FURO_BUCHA = 15.15        # furo para a LM8UU (15,00) entrar justa
FURO_M3 = 3.4             # furo passante
FURO_M3_ROSCA = 2.7       # furo para o parafuso M3 abrir rosca no plastico
NUT_S, NUT_M = 5.7, 2.7   # rasgo para porca M3 (chave, espessura)


# ====================================================================== carros
def _bloco_bucha(x0, x1, y, z):
    """Bloco com furo passante para as buchas e um ressalto de 1,2 mm na ponta x0
    (lado que fica na mesa da impressora) para a bucha nao escapar."""
    b = box(x0, x1, y - MEIO_BLOCO, y + MEIO_BLOCO, z - MEIO_BLOCO, z + MEIO_BLOCO)
    furo = uni(cylx(FURO_BUCHA, y, z, x0 + 1.2, x1 + 1), cylx(11.0, y, z, x0 - 1, x0 + 2))
    return b, furo


def _furo_trava_bucha(x1, y, z, lado):
    """Furo M3 na face x1 para o parafuso + arruela que prende as buchas."""
    return cylx(FURO_M3_ROSCA, y + lado * 0.0, z + 9.2, x1 - 9, x1 + 1)


def carro_puncao(xc):
    """Carro de cima: leva o solenoide (puncao de cima para baixo)."""
    x0, x1 = xc - P.CARRO_L / 2, xc + P.CARRO_L / 2
    ye, zr = P.Y_EIXO_SUP, P.Z_EIXO_SUP
    yi = ye - MEIO_BLOCO                     # face interna dos blocos (14,5)
    solidos, furos = [], []
    for s in (1, -1):
        b, f = _bloco_bucha(x0, x1, s * ye, zr)
        solidos.append(b)
        furos.append(f)
        furos.append(cylx(FURO_M3_ROSCA, s * (ye + 6.5), zr + 6.5, x1 - 9, x1 + 1))   # trava das buchas
    # piso (com o patim que segura o papel) e deck (apoio do solenoide)
    solidos.append(box(x0, x1, -yi, yi, ZP + 3.5, ZP + 6.5))
    solidos.append(box(x0, x1, -(ye + MEIO_BLOCO), ye + MEIO_BLOCO, ZP + 24.5, ZP + 28.5))
    patim = prisma([(-7.5, ZP + 3.5), (7.5, ZP + 3.5), (6.0, ZP + 0.8), (-6.0, ZP + 0.8)], "x", x0, x1)
    solidos.append(patim)
    # chanfros de entrada do patim (para subir na borda do papel sem enroscar)
    for xe, s in ((x0, 1), (x1, -1)):
        furos.append(prisma([(xe - s * 0.1, ZP + 0.7), (xe + s * 5.0, ZP + 0.7), (xe - s * 0.1, ZP + 3.4)],
                            "y", -8.5, 8.5))
    # berco do solenoide: duas paredes + teto com o parafuso de batente
    yw = P.SOL_W / 2 + 0.4
    tw = 3.5
    xb = xc + 13.0
    z_teto = ZP + 84.0
    for s in (1, -1):
        solidos.append(box(x0, xb, s * yw, s * (yw + tw), ZP + 24.5, z_teto + 7.0))
        # recorte para o braco do mancal de cima do eixo vertical (carro no fim de curso)
        ya, yb = sorted((s * (yw - 1), s * (yw + tw + 5.5)))
        furos.append(box(x0 - 1, x0 + 6.0, ya, yb, ZP + 33.0, ZP + 46.5))
    solidos.append(box(x0, xb, -(yw + tw), yw + tw, z_teto, z_teto + 7.0))
    # nervura com os 2 parafusos que apertam o solenoide contra a parede oposta
    solidos.append(box(x0, xb, yw + tw, yw + tw + 4.5, ZP + 41.0, ZP + 51.0))
    for dx in (-6.0, 6.0):
        furos.append(cyly(FURO_M3_ROSCA, xc + dx, ZP + 46.0, yw - 1, yw + tw + 6))
    # batente do embolo (M3 no teto, com porca presa)
    furos.append(cylz(FURO_M3, xc, 0, z_teto - 1, z_teto + 8))
    furos.append(box(xc - NUT_S / 2, xb + 1, -NUT_S / 2, NUT_S / 2, z_teto + 2.15, z_teto + 2.15 + NUT_M))
    # passagens do puncao
    furos.append(cylz(7.0, xc, 0, ZP, ZP + 7))          # piso + patim: o puncao montado entra por baixo
    furos.append(cylz(9.0, xc, 0, ZP + 24, ZP + 29))    # deck (passa o espacador sextavado)
    furos.append(box(xc, x1 + 1, -1.8, 1.8, ZP + 24, ZP + 29))   # rasgo: a haste do embolo entra de lado
    corpo = dif(uni(solidos), furos)
    # pinos de ancoragem da correia (a correia abraca o pino e e presa com abracadeira)
    pinos = [cylz(4.5, xc + dx, -4.0, ZP + 6.0, ZP + 25.0) for dx in (-20.0, 20.0)]
    # olhal para a abracadeira do cabo
    olhal = dif(box(x0, x0 + 8, yw + tw, yw + tw + 6, z_teto + 1, z_teto + 7),
                box(x0 - 1, x0 + 9, yw + tw + 1.5, yw + tw + 4.0, z_teto + 2.5, z_teto + 5.5))
    return uni(corpo, pinos, olhal)


def carro_matriz(xc):
    """Carro de baixo: leva o parafuso-matriz (o furo sextavado de um M3 sem cabeca)."""
    x0, x1 = xc - P.CARRO_L / 2, xc + P.CARRO_L / 2
    ye, zr = P.Y_EIXO_INF, P.Z_EIXO_INF
    yi = ye - MEIO_BLOCO                     # 9,5
    solidos, furos = [], []
    for s in (1, -1):
        b, f = _bloco_bucha(x0, x1, s * ye, zr)
        solidos.append(b)
        furos.append(f)
        furos.append(cylx(FURO_M3_ROSCA, s * (ye + 6.5), zr - 6.5, x1 - 9, x1 + 1))
    solidos.append(box(x0, x1, -yi, yi, zr - MEIO_BLOCO, zr - MEIO_BLOCO + 3.0))      # piso
    z_deck0, z_deck1 = ZP - 15.0, ZP - 9.5
    solidos.append(box(x0, x1, -yi, yi, z_deck0, z_deck1))                             # deck
    # torre da matriz: sobe pela fenda entre as mesas, com rampas de 45 graus
    zt = ZP - 2.0
    h = zt - z_deck1
    solidos.append(prisma([(xc - 10 - h, z_deck1), (xc + 10 + h, z_deck1), (xc + 10, zt), (xc - 10, zt)],
                          "y", -3.5, 3.5))
    furos.append(cylz(2.9, xc, 0, z_deck0 - 1, zt + 1))                                # rosca do M3 sem cabeca
    furos.append(box(xc - NUT_S / 2, x1 + 1, -NUT_S / 2, NUT_S / 2, ZP - 13.6, ZP - 13.6 + NUT_M))
    corpo = dif(uni(solidos), furos)
    pinos = [cylz(4.5, xc + dx, -4.0, zr - MEIO_BLOCO + 2.5, z_deck0 + 0.5) for dx in (-20.0, 20.0)]
    return uni(corpo, pinos)


def espacador_bucha(xa, xb, y, z):
    """Anel que ocupa o espaco entre/ao lado das buchas dentro do bloco."""
    return dif(cylx(14.6, y, z, xa, xb), cylx(10.0, y, z, xa - 1, xb + 1))


def calco_solenoide(xc, z0, esp):
    """Calco em U que define a altura do solenoide sobre o deck."""
    w = P.SOL_W / 2
    return dif(box(xc - 11, xc + 11, -w, w, z0, z0 + esp),
               box(xc - 4.6, xc + 12, -4.6, 4.6, z0 - 1, z0 + esp + 1))
