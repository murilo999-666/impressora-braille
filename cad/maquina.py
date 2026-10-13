# -*- coding: utf-8 -*-
"""Monta a impressora braille inteira: chapas de MDF, pecas impressas, pecas do estoque
e ferragens. construir() devolve um objeto Montagem."""
from collections import defaultdict
import Part
import parametros as P
from fc_util import *
from montagem_base import Montagem, COR
import comprados as C
import impressas as I
import impressas_fixas as F

T = P.T
W = P.W_IN
ZP = P.Z_P
FM3 = 3.4

# orientacao de impressao de cada peca: lista de giros (eixo, graus) que deitam a peca na mesa
ORIENTACAO = {
    "carro_puncao": [("y", -90)], "carro_matriz": [("y", -90)],
    "torre_motor_x": [("y", -90)], "mancal_superior": [("y", -90)],
    "esticador": [("x", 90)], "trava_eixos": [("y", 90)], "mancal_eixo_papel": [("y", 90)],
    "rolete": [("y", -90)], "manipulo": [("y", 90)], "suporte_motor_y": [("y", -90)],
    "pressor_base": [("x", -90)], "pressor_braco": [("x", 180)], "bucha_608": [("y", -90)],
    "guia_papel_esq": [], "guia_papel_dir": [], "suporte_fim_de_curso": [("y", -90)],
    "suporte_sensor_papel": [("x", -90)], "bandeja_mega": [], "suporte_modulo": [],
    "placa_conectores": [("x", 90)], "calco_solenoide": [], "espacador_bucha_curto": [("y", -90)],
    "espacador_bucha_longo": [("y", -90)], "anel_encosto": [("y", -90)],
}


def construir(xc=None, ferragens=True, batida=False):
    """xc = posicao dos carros; batida=True desenha o embolo embaixo (ponto sendo marcado)."""
    xc = P.X_CARRO_REF if xc is None else xc
    m = Montagem()
    m.com_ferragens = ferragens
    furos = defaultdict(list)          # recortes pedidos pelas pecas em cada chapa

    # ================================================================ carros
    x0, x1 = xc - P.CARRO_L / 2, xc + P.CARRO_L / 2
    m.add("carro_puncao", I.carro_puncao(xc), "impresso", "impresso", "carro_sup")
    m.add("carro_matriz", I.carro_matriz(xc), "impresso", "impresso", "carro_inf")
    # buchas: 2 no eixo de tras, 1 no da frente (em cada carro)
    for grupo, ye, zr, sz in (("carro_sup", P.Y_EIXO_SUP, P.Z_EIXO_SUP, 1), ("carro_inf", P.Y_EIXO_INF, P.Z_EIXO_INF, -1)):
        n = grupo[-3:]
        m.add("bucha_lm8uu_%s_1" % n, C.lm8uu(x0 + 1.2 + 12.0, ye, zr), "comprado", "aco", grupo, "Bucha linear LM8UU")
        m.add("bucha_lm8uu_%s_2" % n, C.lm8uu(x1 - 12.0, ye, zr), "comprado", "aco", grupo, "Bucha linear LM8UU")
        m.add("bucha_lm8uu_%s_3" % n, C.lm8uu(x0 + 1.2 + 15.4 + 12.0, -ye, zr), "comprado", "aco", grupo, "Bucha linear LM8UU")
        m.add("espacador_bucha_curto_%s" % n, I.espacador_bucha(x0 + 25.2, x1 - 24.0, ye, zr), "impresso",
              "branco", grupo, "espacador_bucha_curto")
        m.add("espacador_bucha_longo_%s_1" % n, I.espacador_bucha(x0 + 1.2, x0 + 16.6, -ye, zr), "impresso",
              "branco", grupo, "espacador_bucha_longo")
        m.add("espacador_bucha_longo_%s_2" % n, I.espacador_bucha(x0 + 40.6, x1, -ye, zr), "impresso",
              "branco", grupo, "espacador_bucha_longo")
        for s in (1, -1):                      # parafuso + arruela que prendem as buchas
            m.arruela(3, "x", s * (ye + 6.5), zr + sz * 6.5, x1, 1, grupo)
            m.parafuso(3, 8, "x", s * (ye + 6.5), zr + sz * 6.5, x1 + 0.5, -1, grupo, onde="trava das buchas")

    # ---- solenoide e puncao (desenhados em repouso: embolo em cima)
    zs = P.SOL_Z_BASE
    quadro = dif(box(xc - P.SOL_H / 2, xc + P.SOL_H / 2, -P.SOL_W / 2, P.SOL_W / 2, zs, zs + P.SOL_L),
                 box(xc - P.SOL_H / 2 + 2, xc + P.SOL_H / 2 + 1, -P.SOL_W / 2 - 1, P.SOL_W / 2 + 1, zs + 2, zs + P.SOL_L - 2),
                 cylz(9.0, xc, 0, zs - 1, zs + P.SOL_L + 1))
    bobina = dif(cylz(17.5, xc, 0, zs + 2.2, zs + P.SOL_L - 2.2), cylz(9.0, xc, 0, zs, zs + P.SOL_L))
    m.add("solenoide_quadro", quadro, "comprado", "aluminio", "carro_sup", "Solenoide JF-0826B 24 V")
    m.add("solenoide_bobina", bobina, "comprado", "cobre", "carro_sup", "Solenoide JF-0826B 24 V", obs="sub")
    m.add("calco_solenoide", I.calco_solenoide(xc, ZP + 28.5, zs - (ZP + 28.5)), "impresso", "branco", "carro_sup")
    d = 0.0 if batida else P.CURSO_USADO    # repouso = batida + curso
    z_ponta = ZP - P.PONTA_PROF + d
    estilete = uni(cylz(2.9, xc, 0, z_ponta + 3.0, z_ponta + 22.0),
                   Part.makeCone(0.6, 1.45, 1.2, V(xc, 0, z_ponta + 1.8)),
                   cylz(1.2, xc, 0, z_ponta + 0.4, z_ponta + 1.8),
                   Part.makeCone(0.3, 0.6, 0.4, V(xc, 0, z_ponta)))
    m.add("puncao_estilete", estilete, "comprado", "aco", "embolo", "Estilete: parafuso M3 sem cabeca, ponta arredondada")
    z_esp = z_ponta + 13.6
    m.add("puncao_espacador", dif(hexagono(5.5, "z", xc, 0, z_esp, z_esp + 15.0), cylz(2.5, xc, 0, z_esp - 1, z_esp + 16)),
          "comprado", "latao", "embolo", "Espacador sextavado M3 femea-femea 15 mm")
    m.porca(3, "z", xc, 0, z_esp, -1, "embolo")
    m.add("solenoide_embolo", uni(cylz(P.SOL_EMBOLO_D, xc, 0, z_esp + 15.0, z_esp + 60.0),
                                  cylz(11.0, xc, 0, z_esp + 58.5, z_esp + 60.0)),
          "comprado", "aco", "embolo", "Solenoide JF-0826B 24 V", obs="sub")
    z_teto = ZP + 84.0
    z_bat = ZP - P.PONTA_PROF + P.CURSO_USADO + 13.6 + 60.0     # topo do embolo em repouso
    m.parafuso(3, 16, "z", xc, 0, z_bat + 16.0, -1, "carro_sup", onde="batente do embolo (regula o curso)")
    m.porca(3, "z", xc, 0, z_teto + 7.0, 1, "carro_sup")
    m.porca(3, "z", xc, 0, z_teto + 2.3, 1, "carro_sup")
    for dx in (-6.0, 6.0):
        m.parafuso(3, 12, "y", xc + dx, ZP + 46.0, P.SOL_W / 2 + 12.0, -1, "carro_sup", onde="aperta o solenoide")
    # ---- matriz (M3 sem cabeca, sextavado interno para cima)
    matriz = dif(cylz(2.95, xc, 0, P.MATRIZ_Z - 16.0, P.MATRIZ_Z),
                 hexagono(1.5, "z", xc, 0, P.MATRIZ_Z - 2.0, P.MATRIZ_Z + 1))
    m.add("matriz_parafuso", matriz, "comprado", "aco", "carro_inf", "Matriz: parafuso allen sem cabeca M3 x 16")
    m.porca(3, "z", xc, 0, ZP - 13.6 + 0.15, 1, "carro_inf")

    # ================================================================ transmissao X
    xs = P.X_EIXO_V
    for s in (1, -1):
        m.add("eixo_x_sup_%s" % ("tras" if s > 0 else "frente"), cylx(8, s * P.Y_EIXO_SUP, P.Z_EIXO_SUP, -T, W + T),
              "comprado", "aco", "fixo", "Eixo retificado 8 mm x 330")
        m.add("eixo_x_inf_%s" % ("tras" if s > 0 else "frente"), cylx(8, s * P.Y_EIXO_INF, P.Z_EIXO_INF, -T, W + T),
              "comprado", "aco", "fixo", "Eixo retificado 8 mm x 330")
    m.add("eixo_vertical", cylz(8, xs, 0, P.Z_EIXO_V_BASE, P.Z_EIXO_V_TOPO), "comprado", "aco", "eixo_vertical",
          "Eixo retificado 8 mm x 103")
    m.add("polia_x_sup", C.polia_gt2("z", xs, 0, P.Z_POLIA_SUP_BASE, 1, 8), "comprado", "aluminio", "eixo_vertical",
          "Polia GT2 20 dentes furo 8")
    m.add("polia_x_inf", C.polia_gt2("z", xs, 0, P.Z_POLIA_INF_TOPO, -1, 8), "comprado", "aluminio", "eixo_vertical",
          "Polia GT2 20 dentes furo 8")
    m.add("rolamento_608_vert_inf", C.rol608("z", xs, 0, P.Z_ROL_INF), "comprado", "aco", "fixo", "Rolamento 608")
    m.add("rolamento_608_vert_sup", C.rol608("z", xs, 0, P.Z_ROL_SUP), "comprado", "aco", "fixo", "Rolamento 608")
    m.add("acoplamento_5x8", C.acoplamento(xs, 0, P.Z_ACOPL_BASE), "comprado", "aluminio", "eixo_vertical",
          "Acoplamento flexivel 5 x 8")
    corpo, eixo_m = C.nema17("z", xs, 0, P.Z_MOTOR_X_FACE, 1)
    m.add("motor_x", corpo, "comprado", "preto", "fixo", "Motor NEMA 17 17HS4401")
    m.add("motor_x_eixo", eixo_m, "comprado", "aco", "eixo_vertical", "Motor NEMA 17 17HS4401", obs="sub")
    m.add("torre_motor_x", F.torre_x(), "impresso", "impresso2")
    for sx in (-1, 1):
        for sy in (-1, 1):
            m.parafuso(3, 8, "z", xs + sx * P.NEMA_FUROS / 2, sy * P.NEMA_FUROS / 2, P.Z_MOTOR_X_FACE + 5.0, -1,
                       onde="motor X na torre")
    for y, z in F.TORRE_FUROS:
        furos["lat_esq"].append(cylx(FM3, y, z, -T - 1, 1))
        m.parafuso(3, 16, "x", y, z, -T, 1, onde="torre do motor X")
        m.porca(3, "x", y, z, 5.0, 1)
    m.add("mancal_superior", F.mancal_sup(), "impresso", "impresso2")
    for y, z in F.MANCAL_SUP_FUROS:
        furos["lat_esq"].append(cylx(FM3, y, z, -T - 1, 1))
        m.parafuso(3, 16, "x", y, z, -T, 1, onde="mancal superior")
        m.porca(3, "x", y, z, 5.0, 1)
    # tensoras, esticadores e travas dos eixos
    for nome, zc in (("sup", P.Z_COR_SUP), ("inf", P.Z_COR_INF)):
        m.add("polia_tensora_%s" % nome, C.polia_lisa(P.X_TENS, 0, zc), "comprado", "aluminio", "fixo",
              "Polia lisa GT2 furo 5 (tensora)")
        m.add("esticador_%s" % nome, F.esticador(zc), "impresso", "impresso2", "fixo", "esticador")
        h = P.TENS_H / 2 + 0.5 + 4.0
        m.parafuso(5, 25, "z", P.X_TENS, 0, zc + h, -1, onde="eixo da polia tensora")
        m.porca(5, "z", P.X_TENS, 0, zc - h, -1, tipo="travante")
        m.add("correia_x_%s" % nome, C.correia_fechada_x(xs, P.X_TENS, 0, zc, P.POLIA_DP / 2 + 0.25), "comprado",
              "correia", "fixo", "Correia GT2 6 mm aberta (650 mm)")
        for lado in (-1, 1):
            m.add("trava_eixos_%s_%s" % (nome, "esq" if lado < 0 else "dir"), F.trava_eixos(lado, zc), "impresso",
                  "impresso3", "fixo", "trava_eixos")
            for sy in (-1, 1):
                y = sy * F.TRAVA_Y
                furos["lat_esq" if lado < 0 else "lat_dir"].append(cylx(FM3, y, zc, -T - 1, W + T + 1))
                if lado < 0:
                    m.parafuso(3, 16, "x", y, zc, -T - 4.0, 1, onde="trava dos eixos")
                    m.porca(3, "x", y, zc, 0.0, 1)
                else:
                    m.parafuso(3, 25, "x", y, zc, W + T + 4.0, -1, onde="esticador da correia")
                    m.porca(3, "x", y, zc, P.X_TENS + 13.15, 1)

    # ================================================================ tracao do papel
    yr, zr = P.Y_ROLO, P.Z_ROLO
    xe0 = -T - P.EIXO_PAPEL_ESQ
    m.add("eixo_papel", cylx(8, yr, zr, xe0, xe0 + P.L_EIXO_PAPEL), "comprado", "aco", "eixo_papel",
          "Eixo retificado 8 mm x 366")
    for lado, c0 in ((-1, -T - P.R608_B), (1, W + T)):
        n = "esq" if lado < 0 else "dir"
        m.add("rolamento_608_papel_%s" % n, C.rol608("x", yr, zr, c0), "comprado", "aco", "fixo", "Rolamento 608")
        m.add("mancal_eixo_papel_%s" % n, F.mancal_papel(lado), "impresso", "impresso2", "fixo", "mancal_eixo_papel")
        for dz in (-F.MANCAL_PAPEL_DY, F.MANCAL_PAPEL_DY):
            furos["lat_esq" if lado < 0 else "lat_dir"].append(cylx(FM3, yr, zr + dz, -T - 1, W + T + 1))
            if lado < 0:
                m.parafuso(3, 20, "x", yr, zr + dz, -T - 9.5, 1, onde="mancal do eixo do papel")
                m.porca(3, "x", yr, zr + dz, 0.0, 1)
            else:
                m.parafuso(3, 20, "x", yr, zr + dz, W + T + 9.5, -1, onde="mancal do eixo do papel")
                m.porca(3, "x", yr, zr + dz, W, -1)
    m.add("polia_y_eixo", C.polia_gt2("x", yr, zr, P.X_POLIA_Y, 1, 8), "comprado", "aluminio", "eixo_papel",
          "Polia GT2 20 dentes furo 8")
    m.add("anel_encosto", dif(cylx(14.0, yr, zr, 0.3, P.X_POLIA_Y - 0.3), cylx(8.3, yr, zr, 0, 10)), "impresso",
          "branco", "eixo_papel")
    for i, xr in enumerate(P.X_ROLOS):
        m.add("rolete_%d" % (i + 1), F.rolete(xr), "impresso", "impresso3", "eixo_papel", "rolete")
        m.add("oring_%d" % (i + 1), F.oring(xr), "comprado", "borracha", "eixo_papel", "O-ring 20 x 3 mm")
        m.parafuso(3, 8, "z", xr - 5.7 + P.ROLO_L - 5.0, yr, zr + 12.0, -1, "eixo_papel", cabeca="sem cabeca",
                   onde="trava do rolete")
        m.porca(3, "z", xr - 5.7 + P.ROLO_L - 5.0, yr, zr + 5.45, 1, "eixo_papel")
        # pressor
        m.add("pressor_base_%d" % (i + 1), F.pressor_base(xr), "impresso", "impresso2", "fixo", "pressor_base")
        m.add("pressor_braco_%d" % (i + 1), F.pressor_braco(xr), "impresso", "impresso", "fixo", "pressor_braco")
        m.add("rolamento_608_pressor_%d" % (i + 1), C.rol608("x", yr, F.PR_Z_ROL, xr - 3.5), "comprado", "aco",
              "fixo", "Rolamento 608")
        m.add("bucha_608_%d" % (i + 1), F.bucha_608("x", yr, F.PR_Z_ROL, xr - 3.8), "impresso", "branco", "fixo",
              "bucha_608")
        m.add("mola_pressor_%d" % (i + 1), dif(cylz(4.6, xr, F.PR_MOLA_Y, ZP + 25.0, F.PR_TETO - 0.0),
                                               cylz(3.8, xr, F.PR_MOLA_Y, ZP + 25, F.PR_TETO + 1)),
              "comprado", "aco", "fixo", "Mola de compressao (de caneta) 4,5 x 20 mm")
        m.parafuso(3, 20, "x", yr, F.PR_Z_ROL, xr - 8.6, 1, onde="eixo do 608 do pressor")
        m.porca(3, "x", yr, F.PR_Z_ROL, xr + 8.6, 1, tipo="travante")
        m.parafuso(3, 35, "x", F.PR_PIVO[0], F.PR_PIVO[1], xr - 13.2, 1, onde="pino do braco do pressor")
        m.porca(3, "x", F.PR_PIVO[0], F.PR_PIVO[1], xr + 13.2, 1, tipo="travante")
        for x, z in F.pressor_furos(xr):
            furos["tras"].append(cyly(FM3, x, z, P.YB - 1, P.YB + T + 1))
            m.parafuso(3, 16, "y", x, z, P.YB + T, -1, onde="base do pressor")
            m.porca(3, "y", x, z, P.YB - 4.0, -1)
    m.add("manipulo", F.manipulo(), "impresso", "impresso3", "eixo_papel")
    m.parafuso(3, 6, "z", W + T + 10.5 + 3.2, yr, zr + 10.0, -1, "eixo_papel", cabeca="sem cabeca", onde="trava do manipulo")
    m.porca(3, "z", W + T + 10.5 + 3.2, yr, zr + 5.05, 1, "eixo_papel")
    # motor Y
    ym, zm, xf = P.Y_MOTOR_Y, P.Z_MOTOR_Y, P.X_MOTOR_Y_FACE
    corpo, eixo_m = C.nema17("x", ym, zm, xf, -1)
    m.add("motor_y", corpo, "comprado", "preto", "fixo", "Motor NEMA 17 17HS4401")
    m.add("motor_y_eixo", eixo_m, "comprado", "aco", "fixo", "Motor NEMA 17 17HS4401", obs="sub")
    m.add("polia_y_motor", C.polia_gt2("x", ym, zm, P.X_POLIA_Y, 1, 5), "comprado", "aluminio", "fixo",
          "Polia GT2 20 dentes furo 5")
    m.add("correia_y", C.correia_fechada_yz(P.X_POLIA_Y + P.POLIA_CORREIA_C, ym, zm, yr, zr, P.POLIA_DP / 2 + 0.25),
          "comprado", "correia", "fixo", "Correia GT2 fechada 200 mm")
    m.add("suporte_motor_y", F.suporte_motor_y(), "impresso", "impresso2")
    for sy in (-1, 1):
        for sz in (-1, 1):
            m.arruela(3, "x", ym + sy * P.NEMA_FUROS / 2, zm + sz * P.NEMA_FUROS / 2, xf - 4.0, -1)
            m.parafuso(3, 8, "x", ym + sy * P.NEMA_FUROS / 2, zm + sz * P.NEMA_FUROS / 2, xf - 4.5, 1, onde="motor Y")
    for x, y in F.MOTOR_Y_FUROS:
        furos["base"].append(cylz(FM3, x, y, -T - 1, 1))
        m.parafuso(3, 12, "z", x, y, -T, 1, onde="suporte do motor Y na base")
        m.porca(3, "z", x, y, 4.0, 1)

    # ================================================================ guias, sensores
    for lado, nome in ((-1, "esq"), (1, "dir")):
        m.add("guia_papel_%s" % nome, F.guia_papel(lado), "impresso", "impresso3")
        xf2 = P.X_PAPEL0 if lado < 0 else P.X_PAPEL0 + P.PAPEL_W
        for y in F.GUIA_Y:
            if lado < 0:   # rasgo curto: ajuste fino de +-5 mm
                furos["mesa_t"].append(oblongo(FM3, FM3 + 10.0, "z", xf2 - F.GUIA_DX, y, ZP - T - 1, ZP + 1))
            else:          # rasgo longo: da largura A5 (148) ate carta (216)
                xa, xb = P.X_PAPEL0 + 148.0 + F.GUIA_DX, P.X_PAPEL0 + 216.0 + F.GUIA_DX
                furos["mesa_t"].append(oblongo(FM3, xb - xa + FM3, "z", (xa + xb) / 2, y, ZP - T - 1, ZP + 1))
            m.parafuso(3, 16, "z", xf2 + lado * F.GUIA_DX, y, ZP - T, 1, onde="guia do papel")
            m.arruela(3, "z", xf2 + lado * F.GUIA_DX, y, ZP + 3.0, 1)
            m.porca(3, "z", xf2 + lado * F.GUIA_DX, y, ZP + 3.5, 1, tipo="borboleta")
    m.add("suporte_fim_de_curso", F.suporte_fim_de_curso(), "impresso", "impresso2")
    m.add("microchave_fim_de_curso", box(*F.fdc_posicao()), "comprado", "preto", "fixo", "Microchave KW11-3Z (fim de curso)")
    for y, z in F.FDC_FUROS:
        furos["lat_esq"].append(cylx(FM3, y, z, -T - 1, 1))
        m.parafuso(3, 16, "x", y, z, -T, 1, onde="suporte do fim de curso")
        m.porca(3, "x", y, z, 4.0, 1)
    m.conta("Parafuso M2 x 12 (philips)", 4)
    m.add("suporte_sensor_papel", F.suporte_sensor_papel(), "impresso", "impresso2")
    m.add("microchave_sensor_papel", box(*F.sensor_posicao()), "comprado", "preto", "fixo", "Microchave KW11-3Z (fim de curso)")
    sp = F.sensor_posicao()
    m.add("haste_sensor_papel", prisma([(sp[3] - 1, sp[4]), (sp[3] - 1, sp[4] - 0.5), (sp[2] - 6, ZP - 2.5), (sp[2] - 6, ZP - 2.0)],
                                       "x", F.SENSOR_X - 2.0, F.SENSOR_X + 2.0), "comprado", "aco", "fixo",
          "Microchave KW11-3Z (fim de curso)", obs="sub")
    furos["mesa_t"].append(box(F.SENSOR_X - 2.5, F.SENSOR_X + 2.5, sp[2] - 9, sp[2] + 9, ZP - T - 1, ZP + 1))
    for x, z in F.sensor_furos():
        furos["tras"].append(cyly(FM3, x, z, P.YB - 1, P.YB + T + 1))
        m.parafuso(3, 16, "y", x, z, P.YB + T, -1, onde="suporte do sensor de papel")
        m.porca(3, "y", x, z, P.YB - 4.0, -1)

    # ================================================================ eletronica
    m.add("bandeja_mega", F.bandeja_mega(), "impresso", "impresso2")
    for x, y in F.BANDEJA_FUROS:
        furos["base"].append(cylz(FM3, x, y, -T - 1, 1))
        m.parafuso(3, 12, "z", x, y, -T, 1, onde="bandeja do Mega na base")
        m.porca(3, "z", x, y, 2.5, 1)
    for u, v in P.MEGA_FUROS:
        m.parafuso(3, 8, "z", P.X_MEGA + v, P.Y_MEGA_USB - u, P.Z_PCB_MEGA + 1.6, -1, onde="Mega na bandeja", cabeca="philips")
    nomes = {"mega_pcb": "Arduino Mega 2560", "mega_usb": "Arduino Mega 2560", "mega_jack": "Arduino Mega 2560",
             "barras_pinos": "RAMPS 1.4", "ramps_pcb": "RAMPS 1.4", "ramps_borne_fonte": "RAMPS 1.4",
             "ramps_borne_saidas": "RAMPS 1.4", "driver_x": "Driver DRV8825", "driver_y": "Driver DRV8825"}
    for nome, forma, cor in C.mega_ramps(P.X_MEGA, P.Y_MEGA_USB, P.Z_PCB_MEGA):
        principal = nome in ("mega_pcb", "ramps_pcb", "driver_x", "driver_y")
        m.add(nome, forma, "comprado", cor, "fixo", nomes[nome], obs="" if principal else "sub")
    for nome, x, y in F.MODULOS:
        m.add(nome, F.suporte_modulo(x, y), "impresso", "impresso2", "fixo", "suporte_modulo")
        furos["base"].append(cylz(FM3, x, y, -T - 1, 1))
        m.parafuso(3, 10, "z", x, y, -T, 1, onde="suporte de modulo na base")
        m.porca(3, "z", x, y, 1.55, 1)
    (_, sx, sy), (_, px, py) = F.MODULOS
    e = F.MOD_E
    m.add("modulo_stepup_xl6009", uni(box(sx - 21.5, sx + 21.5, sy - 10.5, sy + 10.5, e, e + 1.6),
                                      box(sx - 12, sx + 2, sy - 7, sy + 7, e + 1.6, e + 9.0),
                                      cylz(8.0, sx + 14, sy, e + 1.6, e + 12.0)), "comprado", "pcb_azul", "fixo",
          "Modulo step-up XL6009")
    m.add("placa_solenoide", uni(box(px - 20, px + 20, py - 12.5, py + 12.5, e, e + 1.6),
                                 cylz(12.5, px - 9, py, e + 1.6, e + 23.0), box(px + 6, px + 18, py - 4, py + 4, e + 1.6, e + 11.0)),
          "comprado", "verde", "fixo", "Placa do solenoide (perfurada 4 x 2,5 cm)")
    # placa de conectores (por fora da parede traseira)
    c = F.PLACA_CON
    m.add("placa_conectores", F.placa_conectores(), "impresso", "impresso2")
    furos["tras"].append(ret_arred("y", c["x"] - 23, c["x"] + 23, c["z"] - 13, c["z"] + 13, P.YB - 1, P.YB + T + 1, 3.0))
    for x, z in F.placa_con_furos():
        furos["tras"].append(cyly(FM3, x, z, P.YB - 1, P.YB + T + 1))
        m.parafuso(3, 16, "y", x, z, P.YB + T + 3.0, -1, onde="placa de conectores")
        m.porca(3, "y", x, z, P.YB, -1)
    yo = P.YB + T + 3.0
    m.add("jack_p4", uni(cyly(11.0, c["x"] - 16, c["z"], yo - 26, yo - 3.0), cyly(8.0, c["x"] - 16, c["z"], yo - 3.0, yo),
                         cyly(13.0, c["x"] - 16, c["z"], yo, yo + 2.5)),
          "comprado", "preto", "fixo", "Jack P4 femea de painel 5,5 x 2,1 mm")
    m.add("chave_liga", uni(box(c["x"] - 6.5, c["x"] + 6.5, yo - 16, yo - 3, c["z"] - 4, c["z"] + 4),
                           cyly(6.0, c["x"], c["z"], yo - 3, yo + 9), cyly(3.0, c["x"], c["z"] + 2, yo + 9, yo + 19)),
          "comprado", "aluminio", "fixo", "Chave alavanca 2 posicoes (liga/desliga)")
    m.add("porta_fusivel", uni(cyly(12.0, c["x"] + 16, c["z"], yo - 28, yo), cyly(15.0, c["x"] + 16, c["z"], yo, yo + 9)),
          "comprado", "preto", "fixo", "Porta-fusivel de painel 5 x 20 mm + fusivel 3 A")

    # ================================================================ papel (ilustrativo)
    m.add("papel_a4", box(P.X_PAPEL0, P.X_PAPEL0 + P.PAPEL_W, -45.0, -45.0 + P.PAPEL_L, ZP, ZP + 0.2), "comprado",
          "papel", "papel", "Papel braille 120-180 g/m2")

    # ================================================================ chapas
    _chapas(m, furos)
    return m


def _chapas(m, furos):
    fe, ft = P.FOLGA_ENC, P.FOLGA_TAB
    YF, YB = P.YF, P.YB
    zb = -(T + P.SAIA)
    H = P.H_IN
    prof = P.PARAF_T_L - T + 1.0          # canal do parafuso nas juntas em T

    # ---------------------------------------------------------- laterais
    for lado, nome in ((-1, "lat_esq"), (1, "lat_dir")):
        xa, xb = (-T, 0.0) if lado < 0 else (W, W + T)
        s = ret_arred("x", -(YF + T + P.ABA), YB + T + P.ABA, zb, H, xa, xb, 6.0)
        c = []
        for a, b in P.TAB_BASE_LAT:
            c.append(box(xa - 1, xb + 1, a - ft / 2, b + ft / 2, -T - fe / 2, fe / 2))
        for a, b in P.TAB_FT_LAT:
            c.append(box(xa - 1, xb + 1, -YF - T - fe / 2, -YF + fe / 2, a - ft / 2, b + ft / 2))
            c.append(box(xa - 1, xb + 1, YB - fe / 2, YB + T + fe / 2, a - ft / 2, b + ft / 2))
        for a, b in P.TAB_MESA_T:
            c.append(box(xa - 1, xb + 1, a - ft / 2, b + ft / 2, ZP - T - fe / 2, ZP + fe / 2))
        for a, b in P.TAB_MESA_F:
            c.append(box(xa - 1, xb + 1, a - ft / 2, b + ft / 2, ZP - P.DEGRAU - T - fe / 2, ZP - P.DEGRAU + fe / 2))
        for y in P.T_BASE_LAT:
            c.append(cylx(FM3, y, -T / 2, xa - 1, xb + 1))
        for z in P.T_FT_LAT:
            c.append(cylx(FM3, -YF - T / 2, z, xa - 1, xb + 1))
            c.append(cylx(FM3, YB + T / 2, z, xa - 1, xb + 1))
        for sy in (1, -1):
            c.append(cylx(P.FURO_EIXO_MDF, sy * P.Y_EIXO_SUP, P.Z_EIXO_SUP, xa - 1, xb + 1))
            c.append(cylx(P.FURO_EIXO_MDF, sy * P.Y_EIXO_INF, P.Z_EIXO_INF, xa - 1, xb + 1))
        c.append(cylx(12.5, P.Y_ROLO, P.Z_ROLO, xa - 1, xb + 1))
        c.extend(furos[nome])
        m.add("lateral_%s" % ("esquerda" if lado < 0 else "direita"), dif(s, c), "mdf", "mdf")
        # parafusos das juntas em T que atravessam as laterais
        for y in P.T_BASE_LAT:
            m.parafuso(3, 16, "x", y, -T / 2, xa if lado < 0 else xb, -lado, onde="junta em T lateral-base")
            m.porca(3, "x", y, -T / 2, (4.5 if lado < 0 else W - 4.5), -lado)
        for z in P.T_FT_LAT:
            for y in (-YF - T / 2, YB + T / 2):
                m.parafuso(3, 16, "x", y, z, xa if lado < 0 else xb, -lado, onde="junta em T lateral-frente/tras")
                m.porca(3, "x", y, z, (4.5 if lado < 0 else W - 4.5), -lado)

    def t_borda_x(a0, a1, b0, b1, z_ou_y, eixo):
        """Recortes em T nas duas bordas x = 0 e x = W de uma chapa.
        eixo = 'z': chapa vertical (frente/tras), posicao ao longo de z; (a0, a1) = faixa em y.
        eixo = 'y': chapa horizontal (base), posicao ao longo de y; (b0, b1) = faixa em z."""
        r = []
        p = z_ou_y
        for x_can, x_por in (((-0.01, prof), (4.5, 4.5 + 2.7)), ((W - prof, W + 0.01), (W - 4.5 - 2.7, W - 4.5))):
            if eixo == "z":
                r.append(box(x_can[0], x_can[1], a0, a1, p - 1.7, p + 1.7))
                r.append(box(x_por[0], x_por[1], a0, a1, p - 2.85, p + 2.85))
            else:
                r.append(box(x_can[0], x_can[1], p - 1.7, p + 1.7, b0, b1))
                r.append(box(x_por[0], x_por[1], p - 2.85, p + 2.85, b0, b1))
        return r

    # ---------------------------------------------------------- frente e tras
    for nome, ya, yb, sinal in (("frente", -YF - T, -YF, -1), ("tras", YB, YB + T, 1)):
        s = [box(0, W, ya, yb, zb, H)]
        for a, b in P.TAB_FT_LAT:
            s.append(box(-T, 0, ya, yb, a, b))
            s.append(box(W, W + T, ya, yb, a, b))
        c = []
        for a, b in P.TAB_BASE_FT:
            c.append(box(a - ft / 2, b + ft / 2, ya - 1, yb + 1, -T - fe / 2, fe / 2))
        for x in P.T_BASE_FT:
            c.append(cyly(FM3, x, -T / 2, ya - 1, yb + 1))
            m.parafuso(3, 16, "y", x, -T / 2, ya if sinal < 0 else yb, -sinal, onde="junta em T frente/tras-base")
            m.porca(3, "y", x, -T / 2, (-YF + 4.5 if sinal < 0 else YB - 4.5), -sinal)
        for z in P.T_FT_LAT:
            c.extend(t_borda_x(ya - 1, yb + 1, 0, 0, z, "z"))
        z_mesa = ZP - T - 0.3 if nome == "tras" else ZP - P.DEGRAU - T - 0.3
        c.append(ret_arred("y", P.X_ABERT0 - 0.3, P.X_ABERT0 + P.ABERT_W + 0.3, z_mesa, ZP + 8.0, ya - 1, yb + 1, 1.0))
        if nome == "frente":
            c.append(ret_arred("y", 60.0, W - 60.0, 20.0, 92.0, ya - 1, yb + 1, 8.0))      # janela de inspecao
        else:
            c.append(ret_arred("y", P.X_MEGA + 28.0, P.X_MEGA + 48.2, 5.0, 25.0, ya - 1, yb + 1, 2.0))   # cabo USB
            for x in (125.0, 193.0, 262.0, 300.0):                                   # abracadeiras dos cabos
                for dz in (-3.5, 3.5):
                    c.append(box(x - 2.0, x + 2.0, ya - 1, yb + 1, ZP + 62.0 + dz - 1.0, ZP + 62.0 + dz + 1.0))
        c.extend(furos[nome])
        m.add("parede_%s" % ("frontal" if nome == "frente" else "traseira"), dif(uni(s), c), "mdf", "mdf2")

    # ---------------------------------------------------------- base
    s = [box(0, W, -YF, YB, -T, 0)]
    for a, b in P.TAB_BASE_LAT:
        s.append(box(-T, 0, a, b, -T, 0))
        s.append(box(W, W + T, a, b, -T, 0))
    for a, b in P.TAB_BASE_FT:
        s.append(box(a, b, -YF - T, -YF, -T, 0))
        s.append(box(a, b, YB, YB + T, -T, 0))
    c = []
    for y in P.T_BASE_LAT:
        c.extend(t_borda_x(0, 0, -T - 1, 1, y, "y"))
    for x in P.T_BASE_FT:
        c.append(box(x - 1.7, x + 1.7, -YF - 0.01, -YF + prof, -T - 1, 1))
        c.append(box(x - 2.85, x + 2.85, -YF + 4.5, -YF + 4.5 + 2.7, -T - 1, 1))
        c.append(box(x - 1.7, x + 1.7, YB - prof, YB + 0.01, -T - 1, 1))
        c.append(box(x - 2.85, x + 2.85, YB - 4.5 - 2.7, YB - 4.5, -T - 1, 1))
    # passagens para abracadeiras dos cabos
    for x, y in ((75.0, -30.0), (120.0, 40.0), (185.0, -30.0), (185.0, 40.0), (285.0, 0.0), (285.0, 55.0)):
        c.append(box(x - 2.0, x + 2.0, y - 5.0, y - 3.0, -T - 1, 1))
        c.append(box(x - 2.0, x + 2.0, y + 3.0, y + 5.0, -T - 1, 1))
    c.extend(furos["base"])
    m.add("base", dif(uni(s), c), "mdf", "mdf2")

    # ---------------------------------------------------------- mesas do papel
    xa0, xa1 = P.X_ABERT0, P.X_ABERT0 + P.ABERT_W
    s = [box(0, W, P.FENDA / 2, YB, ZP - T, ZP),
         ret_arred("z", xa0, xa1, YB - 10, YB + T + P.LINGUETA_TRAS, ZP - T, ZP, 8.0)]
    for a, b in P.TAB_MESA_T:
        s.append(box(-T, 0, a, b, ZP - T, ZP))
        s.append(box(W, W + T, a, b, ZP - T, ZP))
    c = []
    for xr in P.X_ROLOS:                                     # janelas dos roletes
        c.append(ret_arred("z", xr - 5.7 - 2.5, xr - 5.7 + P.ROLO_L + 2.5, P.Y_ROLO - 14.5, P.Y_ROLO + 14.5,
                           ZP - T - 1, ZP + 1, 2.0))
    c.append(box(-1, 26.0, P.Y_ROLO - 11.0, P.Y_ROLO + 11.0, ZP - T - 1, ZP + 1))   # polia do eixo do papel
    c.append(cylz(12.0, W - 16.0, 70.0, ZP - T - 1, ZP + 1))                        # descida dos cabos
    c.extend(furos["mesa_t"])
    m.add("mesa_traseira", dif(uni(s), c), "mdf", "mdf")

    zf = ZP - P.DEGRAU
    s = [box(0, W, -YF, -P.FENDA / 2, zf - T, zf),
         ret_arred("z", xa0, xa1, -YF - T - P.LINGUETA_FRENTE, -YF + 10, zf - T, zf, 8.0)]
    for a, b in P.TAB_MESA_F:
        s.append(box(-T, 0, a, b, zf - T, zf))
        s.append(box(W, W + T, a, b, zf - T, zf))
    c = list(furos["mesa_f"])
    c.append(cylz(10.0, 12.0, -35.0, zf - T - 1, zf + 1))                           # cabo do fim de curso
    m.add("mesa_frontal", dif(uni(s), c) if c else uni(s), "mdf", "mdf")
