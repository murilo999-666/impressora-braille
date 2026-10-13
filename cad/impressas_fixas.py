# -*- coding: utf-8 -*-
"""Pecas impressas fixas (suportes, mancais, tracao do papel, eletronica).
Cada funcao devolve o solido ja na posicao da maquina."""
import math
import Part
import parametros as P
from fc_util import *
from impressas import ZP, FURO_M3, FURO_M3_ROSCA, NUT_S, NUT_M

# ====================================================================== transmissao X
TORRE_FUROS = [(sy * 13.0, z) for sy in (-1, 1) for z in (P.Z_MOTOR_X_FACE + 12.0, P.Z_ROL_INF - 6.0)]


def torre_x():
    """Suporte do motor X + gaiola do acoplamento + assento do 608 de baixo.
    Parafusada por dentro na lateral esquerda (x = 0)."""
    xs = P.X_EIXO_V
    zf = P.Z_MOTOR_X_FACE                 # face do motor (motor pendurado embaixo)
    zt = P.Z_ROL_INF + P.R608_B           # topo do assento
    L = 22.0
    s = [box(0, 45, -L, L, zf, zf + 5.0),                         # placa do motor
         box(0, 5, -L, L, zf, zt),                                # flange na lateral
         box(0, 45, 18, L, zf, zt), box(0, 45, -L, -18, zf, zt),  # paredes
         box(0, 37, -L, L, P.Z_ROL_INF - 1.5, zt)]                # assento do rolamento
    f = [cylz(23.0, xs, 0, zf - 1, zf + 6)]
    for sx in (-1, 1):
        for sy in (-1, 1):
            f.append(cylz(FURO_M3, xs + sx * P.NEMA_FUROS / 2, sy * P.NEMA_FUROS / 2, zf - 1, zf + 6))
    for sy in (-1, 1):                                            # acesso da chave aos parafusos de tras
        f.append(cylz(6.5, xs - P.NEMA_FUROS / 2, sy * P.NEMA_FUROS / 2, P.Z_ROL_INF - 3, zt + 1))
    f.append(cylz(P.R608_D + 0.15, xs, 0, P.Z_ROL_INF, zt + 1))   # bolsa do 608
    f.append(cylz(12.5, xs, 0, P.Z_ROL_INF - 3, zt))
    for y, z in TORRE_FUROS:
        f.append(cylx(FURO_M3, y, z, -1, 6))
    return dif(uni(s), f)


MANCAL_SUP_FUROS = [(-11.0, P.Z_ROL_SUP + P.R608_B + 11.0), (11.0, P.Z_ROL_SUP + P.R608_B + 11.0)]


def mancal_sup():
    """Mancal do 608 de cima do eixo vertical (lateral esquerda, acima do papel)."""
    xs = P.X_EIXO_V
    z0 = P.Z_ROL_SUP - 1.5
    z1 = P.Z_ROL_SUP + P.R608_B
    zf = z1 + 19.0
    s = [box(0, 5, -20, 20, z0, zf),
         box(0, xs + 13.5, -17.5, 17.5, z0, z1)]
    for sy in (-1, 1):                                            # nervuras
        ya, yb = sorted((sy * 14.0, sy * 17.5))
        s.append(prisma([(5, zf), (5, z1), (xs + 13.5, z1)], "y", ya, yb))
    f = [cylz(P.R608_D + 0.15, xs, 0, P.Z_ROL_SUP, z1 + 1), cylz(12.5, xs, 0, z0 - 1, z1)]
    for y, z in MANCAL_SUP_FUROS:
        f.append(cylx(FURO_M3, y, z, -1, 6))
    return dif(uni(s), f)


def esticador(zc):
    """Garfo da polia tensora, puxado por 2 parafusos M3 que atravessam a lateral direita."""
    x = P.X_TENS
    hy = 14.5
    h = P.TENS_H / 2 + 0.5
    s = [box(x - 7, x + 18.5, -hy, hy, zc + h, zc + h + 4.0),
         box(x - 7, x + 18.5, -hy, hy, zc - h - 4.0, zc - h),
         box(x + 10.5, x + 18.5, -hy, hy, zc - h - 4.0, zc + h + 4.0)]
    f = [cylz(5.2, x, 0, zc - 20, zc + 20)]
    for sy in (-1, 1):
        f.append(cylx(FURO_M3, sy * 10.0, zc, x + 9, x + 20))
        f.append(box(x + 13.0, x + 13.0 + NUT_M, sy * 10.0 - NUT_S / 2, sy * 10.0 + NUT_S / 2, zc - 3.2, zc + h + 5))
    return dif(uni(s), f)


TRAVA_Y = 10.0      # os 2 parafusos de cada trava (e de cada esticador) ficam em y = +-10


def trava_eixos(lado, zc):
    """Tira que fecha as pontas de dois eixos por fora da lateral. lado = -1 (esq) ou +1 (dir)."""
    xa = -P.T if lado < 0 else P.W_IN + P.T
    xb = xa + lado * 4.0
    lo, hi = min(xa, xb), max(xa, xb)
    s = ret_arred("x", -31, 31, zc - 7, zc + 7, lo, hi, 3.0)
    f = [cylx(FURO_M3, sy * TRAVA_Y, zc, lo - 1, hi + 1) for sy in (-1, 1)]
    r0, r1 = sorted((xa - lado * 0.01, xa + lado * 1.0))
    for sy in (-1, 1):                                            # rebaixo de 1 mm onde encosta o eixo
        ya, yb = sorted((sy * 15.5, sy * 29.5))
        f.append(ret_arred("x", ya, yb, zc - 4.7, zc + 4.7, r0, r1, 4.0))
    return dif(s, f)


# ====================================================================== tracao do papel
MANCAL_PAPEL_DY = 18.0     # furos acima e abaixo do eixo


def mancal_papel(lado):
    """Mancal do 608 do eixo do papel, por FORA da lateral (o rolamento fica preso contra o MDF)."""
    y, z = P.Y_ROLO, P.Z_ROLO
    xa = -P.T if lado < 0 else P.W_IN + P.T
    xb = xa + lado * 9.5
    lo, hi = min(xa, xb), max(xa, xb)
    e0, e1 = sorted((xa, xa + lado * 4.0))
    s = [cylx(30.0, y, z, lo, hi), ret_arred("x", y - 7, y + 7, z - 25, z + 25, lo, hi, 6.9)]
    b0, b1 = sorted((xa - lado * 0.01, xa + lado * 7.2))
    f = [cylx(P.R608_D + 0.15, y, z, b0, b1), cylx(10.0, y, z, lo - 1, hi + 1)]
    for dz in (-MANCAL_PAPEL_DY, MANCAL_PAPEL_DY):
        f.append(cylx(FURO_M3, y, z + dz, lo - 1, hi + 1))
    return dif(uni(s), f)


def rolete(xr):
    """Rolete de tracao: O-ring 20 x 3 no canal, preso ao eixo por parafuso M3 + porca."""
    y, z = P.Y_ROLO, P.Z_ROLO
    xa, xb = xr - 5.7, xr - 5.7 + P.ROLO_L
    # perfil de revolucao: canal de 20,6 mm com flancos a 45 graus (imprime em pe sem suporte)
    R, rg, rf = 12.0, 10.3, 8.15 / 2
    perfil = [(xa, rf), (xa, R), (xr - 3.4, R), (xr - 1.7, rg), (xr + 1.7, rg), (xr + 3.4, R), (xb, R), (xb, rf)]
    pts = [V(px, y, z + pr) for px, pr in perfil]
    pts.append(pts[0])
    s = Part.Face(Part.makePolygon(pts)).revolve(V(0, y, z), V(1, 0, 0), 360)
    xp = xb - 5.0                                                 # posicao do parafuso de trava
    f = [
         cylz(FURO_M3, xp, y, z, z + 13),
         box(xp - NUT_M / 2, xp + NUT_M / 2, y - NUT_S / 2, y + NUT_S / 2, z + 5.3, z + 5.3 + 8)]
    return dif(s, f)


def oring(xr):
    y, z = P.Y_ROLO, P.Z_ROLO
    return dif(cylx(P.ROLO_D, y, z, xr - 1.5, xr + 1.5), cylx(20.6, y, z, xr - 2, xr + 2))


def manipulo():
    """Manipulo para avancar o papel com a mao (ponta direita do eixo do papel)."""
    y, z = P.Y_ROLO, P.Z_ROLO
    xa = P.W_IN + P.T + 10.5
    xb = P.W_IN + P.T + (P.L_EIXO_PAPEL - P.L_EIXO_X - P.EIXO_PAPEL_ESQ)
    cubo = cylx(18.0, y, z, xa, xb)
    disco = cylx(40.0, y, z, xb - 8.0, xb)
    cortes = [cylx(8.15, y, z, xa - 1, xb + 1)]
    for i in range(8):
        a = i * math.pi / 4
        cortes.append(cylx(9.0, y + 21.5 * math.cos(a), z + 21.5 * math.sin(a), xb - 9, xb + 1))
    xp = xa + 3.2
    cortes.append(cylz(FURO_M3, xp, y, z, z + 10))
    cortes.append(box(xp - NUT_M / 2, xp + NUT_M / 2, y - NUT_S / 2, y + NUT_S / 2, z + 4.9, z + 10))
    return dif(uni(cubo, disco), cortes)


MOTOR_Y_FUROS = [(P.X_MOTOR_Y_FACE + 13.0, P.Y_MOTOR_Y - 20.0), (P.X_MOTOR_Y_FACE + 13.0, P.Y_MOTOR_Y + 20.0),
                 (P.X_MOTOR_Y_FACE + 29.0, P.Y_MOTOR_Y)]


def suporte_motor_y():
    """Suporte em L do motor do papel, parafusado na base. Os rasgos verticais
    deixam o motor subir/descer +-4 mm para esticar a correia fechada."""
    ym, zm, xf = P.Y_MOTOR_Y, P.Z_MOTOR_Y, P.X_MOTOR_Y_FACE
    aj = P.AJUSTE_MOTOR_Y
    y0, y1 = ym - 26.0, ym + 26.0
    zt = zm + P.NEMA_L / 2 + aj + 3.0
    s = [box(xf - 4.0, xf, y0, y1, 0, zt),
         box(xf - 4.0, xf + 34.0, y0, y1, 0, 4.0)]
    for ya, yb in ((y0, y0 + 3.5), (y1 - 3.5, y1)):
        s.append(prisma([(xf, zt), (xf, 4.0), (xf + 34.0, 4.0)], "y", ya, yb))
    f = [oblongo(23.0, 23.0 + 2 * aj, "x", ym, zm, xf - 5, xf + 1, ao_longo="b")]
    for sy in (-1, 1):
        for sz in (-1, 1):
            f.append(oblongo(FURO_M3, FURO_M3 + 2 * aj, "x", ym + sy * P.NEMA_FUROS / 2,
                             zm + sz * P.NEMA_FUROS / 2, xf - 5, xf + 1, ao_longo="b"))
    for x, y in MOTOR_Y_FUROS:
        f.append(cylz(FURO_M3, x, y, -1, 5))
    return dif(uni(s), f)


# ---------------------------------------------------------------------- pressor
PR_PIVO = (72.0, ZP + 21.0)         # (y, z) do pino do braco
PR_Z_ROL = ZP + P.ROLO_SALIENCIA + 0.2 + P.R608_D / 2  # centro do 608 que aperta o papel
PR_TETO = ZP + 41.0                 # vao de 16 mm para a mola de caneta (22 a 25 mm livre): 6 a 9 mm de aperto
PR_MOLA_Y = 50.0


def pressor_furos(xr):
    return [(xr - 6.0, ZP + 37.0), (xr + 6.0, ZP + 37.0)]


def pressor_base(xr):
    """Base do pressor, parafusada por dentro na parede traseira."""
    yb = P.YB
    s = [box(xr - 13.2, xr + 13.2, yb - 4.0, yb, ZP + 13.0, PR_TETO + 4.0),          # placa na parede
         box(xr - 13.2, xr + 13.2, 44.0, yb, PR_TETO, PR_TETO + 4.0)]                 # teto (apoio da mola)
    for sx in (-1, 1):                                                               # orelhas do pino
        xa, xb = sorted((xr + sx * 9.2, xr + sx * 13.2))
        s.append(box(xa, xb, 66.0, yb, ZP + 14.0, ZP + 28.0))
        s.append(box(xa, xb, yb - 4.0, yb, ZP + 28.0, PR_TETO))
    s.append(cylz(3.6, xr, PR_MOLA_Y, PR_TETO - 3.0, PR_TETO))                        # pino-guia da mola
    f = [cylx(FURO_M3, PR_PIVO[0], PR_PIVO[1], xr - 15, xr + 15)]
    for x, z in pressor_furos(xr):
        f.append(cyly(FURO_M3, x, z, yb - 5, yb + 1))
    return dif(uni(s), f)


def pressor_braco(xr):
    """Braco articulado: garfo com um 608 que aperta o papel contra o O-ring."""
    yr, zr = P.Y_ROLO, PR_Z_ROL
    perfil = [(76.0, ZP + 26.5), (42.0, ZP + 26.5), (40.5, zr + 6), (40.5, zr - 3),
              (43.0, zr - 6.2), (54.0, zr - 6.2), (61.0, ZP + 16.0), (76.0, ZP + 16.0)]
    s = prisma(perfil, "x", xr - 8.6, xr + 8.6)
    f = [box(xr - 3.9, xr + 3.9, 30.0, 61.5, ZP - 5, ZP + 23.5),        # vao do rolamento (ponte em cima)
         cylx(FURO_M3, yr, zr, xr - 10, xr + 10),
         cylx(FURO_M3 + 0.2, PR_PIVO[0], PR_PIVO[1], xr - 10, xr + 10),
         cylz(5.4, xr, PR_MOLA_Y, ZP + 25.0, ZP + 27.5)]                # assento da mola
    return dif(s, f)


def bucha_608(eixo, a, b, c0):
    """Bucha que adapta o furo de 8 mm do 608 para um parafuso M3."""
    return dif(cyl(7.9, eixo, a, b, c0, c0 + 7.6), cyl(3.3, eixo, a, b, c0 - 1, c0 + 9))


# ---------------------------------------------------------------------- guias e sensores
GUIA_Y = (P.YB + P.T + 22.0, P.YB + P.T + 80.0)
GUIA_DX = 9.0       # distancia do parafuso ate a face que guia o papel


def guia_papel(lado):
    """Guia lateral do papel na bandeja de entrada. lado = -1 (esquerda) ou +1 (direita)."""
    xf = P.X_PAPEL0 if lado < 0 else P.X_PAPEL0 + P.PAPEL_W
    y0, y1 = P.YB + P.T + 6.0, P.YB + P.T + 96.0
    a0, a1 = sorted((xf, xf + lado * 16.0))
    b0, b1 = sorted((xf, xf + lado * 3.0))
    s = [box(a0, a1, y0, y1, ZP, ZP + 3.0), box(b0, b1, y0, y1, ZP, ZP + 14.0)]
    f = [cylz(FURO_M3, xf + lado * GUIA_DX, y, ZP - 1, ZP + 4) for y in GUIA_Y]
    return dif(uni(s), f)


FDC_FUROS = [(-49.0, ZP + 8.0), (-49.0, ZP + 22.0)]


def fdc_posicao():
    """Limites da microchave do fim de curso (x0, x1, y0, y1, z0, z1)."""
    xt = P.X_CARRO_MIN - P.CARRO_L / 2
    zc = ZP + 15.0
    return (xt - P.MS_A, xt, -36.7, -36.7 + P.MS_E, zc - P.MS_L / 2, zc + P.MS_L / 2)


def suporte_fim_de_curso():
    """Suporte da microchave do fim de curso do X (lateral esquerda). A face esquerda
    do bloco da bucha da frente do carro de cima aperta a chave em x = X_CARRO_MIN - 28."""
    xt = P.X_CARRO_MIN - P.CARRO_L / 2            # onde o carro encosta
    zc = ZP + 15.0
    ya, yb = -44.2, -36.7                         # braco ao lado da chave
    s = [box(0, 4, -54.0, yb, zc - 13, zc + 13),
         box(0, xt - 1.0, ya, yb, zc - 11, zc + 11)]
    f = []
    xh = xt - P.MS_A + 2.9                        # furos da chave
    for dz in (-P.MS_FUROS / 2, P.MS_FUROS / 2):
        f.append(cyly(1.8, xh, zc + dz, ya - 1, yb + 1))
    for y, z in FDC_FUROS:
        f.append(cylx(FURO_M3, y, z, -1, 5))
    return dif(uni(s), f)


SENSOR_X = P.W_IN / 2
SENSOR_Y = (56.0, 56.0 + P.MS_L)


def sensor_furos():
    return [(SENSOR_X - 8.0, ZP + 36.0), (SENSOR_X + 8.0, ZP + 36.0)]


def sensor_posicao():
    x = SENSOR_X
    return (x - P.MS_E / 2, x + P.MS_E / 2, SENSOR_Y[0], SENSOR_Y[1], ZP + 6.0, ZP + 6.0 + P.MS_A)


def suporte_sensor_papel():
    """Suporte da microchave que detecta o papel (parede traseira, acima da mesa)."""
    x, yb = SENSOR_X, P.YB
    xa, xb = x + P.MS_E / 2, x + P.MS_E / 2 + 7.0
    s = [box(x - 14, x + 14, yb - 4.0, yb, ZP + 12.0, ZP + 44.0),
         box(xa, xb, SENSOR_Y[0] - 2.0, yb, ZP + 4.0, ZP + 26.0)]
    f = []
    zc = ZP + 6.0 + P.MS_A - 2.9
    yc = (SENSOR_Y[0] + SENSOR_Y[1]) / 2
    for dy in (-P.MS_FUROS / 2, P.MS_FUROS / 2):   # rasgos: a altura da chave e regulavel
        f.append(oblongo(1.9, 1.9 + 5.0, "x", yc + dy, zc + 1.0, xa - 1, xb + 1, ao_longo="b"))
    for xx, z in sensor_furos():
        f.append(cyly(FURO_M3, xx, z, yb - 5, yb + 1))
    return dif(uni(s), f)


# ---------------------------------------------------------------------- eletronica
BANDEJA_FUROS = [(P.X_MEGA + 5.0, P.Y_MEGA_USB - 30.0), (P.X_MEGA + P.MEGA_W - 5.0, P.Y_MEGA_USB - 30.0),
                 (P.X_MEGA + 5.0, P.Y_MEGA_USB - 75.0), (P.X_MEGA + P.MEGA_W - 5.0, P.Y_MEGA_USB - 75.0)]


def bandeja_mega():
    """Bandeja com 4 pilares para o Arduino Mega (parafusos M3 abrem rosca nos pilares)."""
    x0, y1 = P.X_MEGA, P.Y_MEGA_USB
    y0 = y1 - P.MEGA_L
    zt = 2.5
    s = [ret_arred("z", x0 - 4, x0 + P.MEGA_W + 4, y0 - 2, y1, 0, zt, 3.0)]
    f = []
    for u, v in P.MEGA_FUROS:
        s.append(cylz(7.0, x0 + v, y1 - u, zt, P.Z_PCB_MEGA))
        f.append(cylz(FURO_M3_ROSCA, x0 + v, y1 - u, zt - 1.0, P.Z_PCB_MEGA + 1))
    for x, y in BANDEJA_FUROS:
        f.append(cylz(FURO_M3, x, y, -1, zt + 1))
    f.append(ret_arred("z", x0 + 12, x0 + P.MEGA_W - 12, y0 + 22, y1 - 22, -1, zt + 1, 4.0))
    return dif(uni(s), f)


MOD_E = 4.0     # espessura da placa de suporte
MODULOS = (("suporte_stepup", 150.0, 52.0), ("suporte_placa_solenoide", 150.0, 14.0))


def suporte_modulo(xc, yc, lx=52.0, ly=30.0):
    """Placa com rasgos para prender um modulo (step-up, placa do solenoide) com abracadeiras."""
    s = ret_arred("z", xc - lx / 2, xc + lx / 2, yc - ly / 2, yc + ly / 2, 0, MOD_E, 3.0)
    f = [cylz(FURO_M3, xc, yc, -1, 5), hexagono(NUT_S, "z", xc, yc, 1.5, 5)]
    for sx in (-1, 1):
        for sy in (-1, 1):
            a0, a1 = sorted((xc + sx * (lx / 2 - 9), xc + sx * (lx / 2 - 5.5)))
            b0, b1 = sorted((yc + sy * (ly / 2 - 7.5), yc + sy * (ly / 2 - 2.0)))
            f.append(box(a0, a1, b0, b1, -1, 5))
    return dif(s, f)


PLACA_CON = dict(x=272.0, z=48.0, lx=64.0, lz=40.0)   # placa de conectores na parede traseira


def placa_con_furos():
    c = PLACA_CON
    return [(c["x"] + sx * (c["lx"] / 2 - 4.5), c["z"] + sz * (c["lz"] / 2 - 4.5)) for sx in (-1, 1) for sz in (-1, 1)]


def placa_conectores():
    """Placa fina por fora da parede traseira: jack P4 de painel, chave e porta-fusivel."""
    c = PLACA_CON
    y0 = P.YB + P.T
    s = ret_arred("y", c["x"] - c["lx"] / 2, c["x"] + c["lx"] / 2, c["z"] - c["lz"] / 2, c["z"] + c["lz"] / 2,
                  y0, y0 + 3.0, 4.0)
    f = [cyly(8.2, c["x"] - 16.0, c["z"], y0 - 1, y0 + 4),      # jack P4 de painel (rosca M8)
         cyly(6.3, c["x"], c["z"], y0 - 1, y0 + 4),             # chave alavanca (rosca 6 mm)
         cyly(12.3, c["x"] + 16.0, c["z"], y0 - 1, y0 + 4)]     # porta-fusivel 5x20 de painel
    for x, z in placa_con_furos():
        f.append(cyly(FURO_M3, x, z, y0 - 1, y0 + 4))
    return dif(s, f)
