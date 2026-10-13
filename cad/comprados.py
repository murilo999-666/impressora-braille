# -*- coding: utf-8 -*-
"""Pecas compradas / do estoque, modeladas de forma simplificada, ja na posicao da maquina."""
import math
import parametros as P
from fc_util import *


def eixo_liso(d, eixo, a, b, c0, c1):
    return cyl(d, eixo, a, b, c0, c1)


def lm8uu(xc, y, z):
    """Bucha linear ao longo de X, centrada em xc."""
    return dif(cylx(P.LM8_D, y, z, xc - P.LM8_L / 2, xc + P.LM8_L / 2),
               cylx(P.D_EIXO + 0.2, y, z, xc - 20, xc + 20))


def rol608(eixo, a, b, c0):
    """Rolamento 608 com a face de baixo em c0."""
    ext = dif(cyl(P.R608_D, eixo, a, b, c0, c0 + P.R608_B), cyl(17.0, eixo, a, b, c0 - 1, c0 + 9))
    inte = dif(cyl(12.0, eixo, a, b, c0, c0 + P.R608_B), cyl(P.R608_d, eixo, a, b, c0 - 1, c0 + 9))
    meio = dif(cyl(17.0, eixo, a, b, c0 + 0.8, c0 + P.R608_B - 0.8),
               cyl(12.0, eixo, a, b, c0 - 1, c0 + 9))
    return uni(ext, inte, meio)


def polia_gt2(eixo, a, b, c_flange, sentido, furo):
    """Polia dentada GT2 20 dentes. c_flange = cota da ponta COM flange (sem cubo);
    o cubo fica para o lado 'sentido' (+1 ou -1)."""
    s = sentido
    c0 = c_flange
    f1 = cyl(P.POLIA_FLANGE_D, eixo, a, b, c0, c0 + s * 1.0)
    dentes = cyl(12.2, eixo, a, b, c0 + s * 1.0, c0 + s * 8.0)
    f2 = cyl(P.POLIA_FLANGE_D, eixo, a, b, c0 + s * 8.0, c0 + s * 9.0)
    cubo = cyl(P.POLIA_FLANGE_D, eixo, a, b, c0 + s * 9.0, c0 + s * P.POLIA_H)
    corpo = uni(f1, dentes, f2, cubo)
    return dif(corpo, cyl(furo, eixo, a, b, c0 - 30, c0 + 30))


def polia_lisa(x, y, zc):
    """Polia tensora lisa (furo 5), eixo vertical, centrada em zc."""
    h = P.TENS_H
    corpo = uni(cylz(P.TENS_FLANGE_D, x, y, zc - h / 2, zc - h / 2 + 1.0),
                cylz(P.TENS_D, x, y, zc - h / 2 + 1.0, zc + h / 2 - 1.0),
                cylz(P.TENS_FLANGE_D, x, y, zc + h / 2 - 1.0, zc + h / 2))
    return dif(corpo, cylz(5.0, x, y, zc - 10, zc + 10))


def acoplamento(x, y, z0):
    corpo = cylz(P.ACOPL_D, x, y, z0, z0 + P.ACOPL_L)
    return dif(corpo, cylz(5.0, x, y, z0 - 1, z0 + P.ACOPL_L / 2),
               cylz(8.0, x, y, z0 + P.ACOPL_L / 2, z0 + P.ACOPL_L + 1))


def nema17(eixo, a, b, c_face, sentido):
    """NEMA 17. (a, b) = centro; c_face = cota da face de montagem; o eixo sai para 'sentido'."""
    s = sentido
    L = P.NEMA_L / 2
    corpo = box_plano(eixo, a - L, a + L, b - L, b + L, c_face, c_face - s * P.NEMA_H)
    # cantos chanfrados do corpo
    ch = 4.5
    cortes = []
    for sa in (-1, 1):
        for sb in (-1, 1):
            pts = [(a + sa * L, b + sb * (L - ch)), (a + sa * L, b + sb * L), (a + sa * (L - ch), b + sb * L)]
            cortes.append(prisma(pts, eixo, c_face - s * P.NEMA_H - 1, c_face + 1))
    corpo = dif(corpo, cortes)
    ress = cyl(P.NEMA_RESSALTO_D, eixo, a, b, c_face, c_face + s * P.NEMA_RESSALTO_H)
    eixo_m = cyl(P.NEMA_EIXO_D, eixo, a, b, c_face, c_face + s * P.NEMA_EIXO_L)
    return corpo, uni(ress, eixo_m)


def correia_fechada_x(xa, xb, y, z, r, larg=6.0, esp=1.4):
    """Laco de correia em plano horizontal (polias de eixo vertical) entre xa e xb."""
    ro, ri = r + esp / 2, r - esp / 2
    z0, z1 = z - larg / 2, z + larg / 2
    retas = [box(xa, xb, y + ri, y + ro, z0, z1), box(xa, xb, y - ro, y - ri, z0, z1)]
    anel_a = dif(cylz(2 * ro, xa, y, z0, z1), cylz(2 * ri, xa, y, z0 - 1, z1 + 1),
                 box(xa, xa + ro + 1, y - ro - 1, y + ro + 1, z0 - 1, z1 + 1))
    anel_b = dif(cylz(2 * ro, xb, y, z0, z1), cylz(2 * ri, xb, y, z0 - 1, z1 + 1),
                 box(xb - ro - 1, xb, y - ro - 1, y + ro + 1, z0 - 1, z1 + 1))
    return uni(retas, anel_a, anel_b)


def correia_fechada_yz(x, y1, z1, y2, z2, r, larg=6.0, esp=1.4):
    """Laco de correia em plano vertical YZ (polias de eixo X) entre os centros 1 e 2."""
    d = math.hypot(y2 - y1, z2 - z1)
    ang = math.degrees(math.atan2(z2 - z1, y2 - y1))
    # constroi ao longo de +y a partir da origem e depois gira em torno de X
    ro, ri = r + esp / 2, r - esp / 2
    x0, x1 = x - larg / 2, x + larg / 2
    retas = [box(x0, x1, 0, d, ri, ro), box(x0, x1, 0, d, -ro, -ri)]
    a1 = dif(cylx(2 * ro, 0, 0, x0, x1), cylx(2 * ri, 0, 0, x0 - 1, x1 + 1),
             box(x0 - 1, x1 + 1, 0, ro + 1, -ro - 1, ro + 1))
    a2 = dif(cylx(2 * ro, d, 0, x0, x1), cylx(2 * ri, d, 0, x0 - 1, x1 + 1),
             box(x0 - 1, x1 + 1, d - ro - 1, d, -ro - 1, ro + 1))
    laco = uni(retas, a1, a2)
    laco = gira(laco, "x", ang)
    return move(laco, 0, y1, z1)


def microchave(eixo_atuador, x0, x1, y0, y1, z0, z1):
    """Bloco da microchave pelos limites; devolve so o corpo."""
    return box(x0, x1, y0, y1, z0, z1)


def mega_ramps(x0, y_usb, z_pcb):
    """Arduino Mega + RAMPS 1.4 + 2 drivers. A placa fica com o USB voltado para +y.
    x0 = canto do lado do conector de alimentacao; devolve lista (nome, forma, cor)."""
    L, W = P.MEGA_L, P.MEGA_W
    y1 = y_usb
    y0 = y_usb - L
    pecas = []
    pecas.append(("mega_pcb", box(x0, x0 + W, y0, y1, z_pcb, z_pcb + 1.6), "pcb_azul"))
    # USB-B e jack
    pecas.append(("mega_usb", box(x0 + 32.0, x0 + 44.2, y1 - 10.0, y1 + 6.3, z_pcb + 1.6, z_pcb + 12.6), "aluminio"))
    pecas.append(("mega_jack", box(x0 + 3.3, x0 + 12.3, y1 - 12.0, y1 + 1.8, z_pcb + 1.6, z_pcb + 12.6), "preto"))
    # barras de pinos (bloco unico entre as placas)
    zc = z_pcb + 1.6
    pecas.append(("barras_pinos", uni(box(x0 + 0.5, x0 + 3.2, y0 + 5, y1 - 14, zc, zc + 11.0),
                                       box(x0 + W - 3.2, x0 + W - 0.5, y0 + 5, y1 - 18, zc, zc + 11.0),
                                       box(x0 + 3, x0 + W - 3, y0 + 1.0, y0 + 6.2, zc, zc + 11.0)), "preto"))
    zr = zc + 11.0
    pecas.append(("ramps_pcb", box(x0 - 3.5, x0 + W + 3.7, y0, y1 - 1.0, zr, zr + 1.6), "pcb_vermelha"))
    zt = zr + 1.6
    # bornes de potencia (verde) e saidas D8-D10 (azul) na ponta do USB
    pecas.append(("ramps_borne_fonte", box(x0 - 2.0, x0 + 18.0, y1 - 13.0, y1 + 9.0, zt, zt + 14.0), "verde"))
    pecas.append(("ramps_borne_saidas", box(x0 + 20.0, x0 + 50.0, y1 - 9.0, y1 - 1.0, zt, zt + 10.0), "pcb_azul"))
    # drivers X e Y com dissipador
    for i, nome in enumerate(("driver_x", "driver_y")):
        dx0 = x0 + 34.0
        dy0 = y1 - 38.0 - i * 24.0
        pecas.append((nome, uni(box(dx0, dx0 + 15.3, dy0 - 20.3, dy0, zt + 8.5, zt + 10.1),
                               box(dx0 + 3.0, dx0 + 12.0, dy0 - 14.0, dy0 - 5.0, zt + 10.1, zt + 18.0)),
                      "pcb_roxa"))
    return pecas
