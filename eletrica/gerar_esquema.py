# -*- coding: utf-8 -*-
"""Desenha os esquemas eletricos da impressora braille (PNG + SVG).
Rodar com o Python que vem no FreeCAD (tem matplotlib):
  "%LOCALAPPDATA%/Programs/FreeCAD 1.1/bin/python.exe" gerar_esquema.py
Saidas: esquema_ligacao.(png|svg), esquema_solenoide.(png|svg)
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, Polygon, Rectangle

AQUI = os.path.dirname(os.path.abspath(__file__))
plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["svg.fonttype"] = "none"

COR = dict(v12="#d32f2f", gnd="#212121", v24="#e65100", sinal="#1565c0", a="#2e7d32", b="#6a1b9a",
           usb="#546e7a", opc="#00838f", borda="#37474f", fundo="#eceff1", ramps="#fde0dc", mega="#dbe7f7",
           mod="#e3f2e1", amarelo="#fff8e1")


def bloco(ax, x, y, w, h, titulo, sub="", cor="#eceff1", tracejado=False, tam=10):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=1.2", fc=cor, ec=COR["borda"],
                                lw=1.3, ls="--" if tracejado else "-", zorder=2))
    ax.text(x + w / 2, y + h - 2.2, titulo, ha="center", va="top", fontsize=tam, fontweight="bold", zorder=5)
    if sub:
        ax.text(x + w / 2, y + h - 6.0, sub, ha="center", va="top", fontsize=7.2, color="#455a64", zorder=5)


def pino(ax, x, y, nome, lado="e", cor="#212121", tam=7.5):
    """Terminal: bolinha + rotulo. lado = onde fica o TEXTO (e, d, c, b)."""
    ax.add_patch(Circle((x, y), 0.8, fc="white", ec=cor, lw=1.4, zorder=6))
    dx, dy, ha, va = {"e": (-1.6, 0, "right", "center"), "d": (1.6, 0, "left", "center"),
                      "c": (0, 1.5, "center", "bottom"), "b": (0, -1.5, "center", "top")}[lado]
    ax.text(x + dx, y + dy, nome, ha=ha, va=va, fontsize=tam, zorder=6)
    return (x, y)


def fio(ax, pts, cor, lw=2.0, ls="-", z=4):
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    ax.plot(xs, ys, color=cor, lw=lw, ls=ls, solid_capstyle="round", solid_joinstyle="round", zorder=z)


def no(ax, p, cor):
    ax.add_patch(Circle(p, 0.75, fc=cor, ec=cor, zorder=7))


def nota(ax, x, y, txt, tam=7.5, cor="#37474f", ha="left", va="center", fundo=None):
    ax.text(x, y, txt, fontsize=tam, color=cor, ha=ha, va=va, zorder=8,
            bbox=dict(fc=fundo, ec="none", pad=1.2) if fundo else None)


# ============================================================================ 1) ligacao geral
def ligacao():
    fig, ax = plt.subplots(figsize=(17, 11.2), dpi=110)
    ax.set_xlim(0, 240)
    ax.set_ylim(0, 158)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.text(3, 154, "Impressora braille: ligação elétrica", fontsize=17, fontweight="bold", va="center")
    ax.text(3, 148.5, "Arduino Mega 2560 + RAMPS 1.4 · fonte 12 V · solenoide de 24 V alimentado por conversor step-up",
            fontsize=9.5, color="#455a64", va="center")

    # ---------------- alimentacao
    bloco(ax, 4, 110, 30, 26, "Fonte 12 V", "5 A (60 W)\nplugue P4", COR["amarelo"])
    f_p = pino(ax, 34, 127, "+12 V", "e", COR["v12"])
    f_n = pino(ax, 34, 116, "GND", "e", COR["gnd"])
    bloco(ax, 46, 121, 20, 12, "Fusível 3 A", "porta-fusível 5×20", "#ffffff", tam=8.5)
    fu_a = pino(ax, 46, 127, "", "e", COR["v12"])
    fu_b = pino(ax, 66, 127, "", "d", COR["v12"])
    bloco(ax, 76, 121, 20, 12, "Chave geral", "liga/desliga", "#ffffff", tam=8.5)
    ch_a = pino(ax, 76, 127, "", "e", COR["v12"])
    ch_b = pino(ax, 96, 127, "", "d", COR["v12"])
    fio(ax, [f_p, fu_a], COR["v12"])
    fio(ax, [fu_b, ch_a], COR["v12"])
    nota(ax, 46, 118.2, "na placa de conectores da parede traseira", 7.2)

    # ---------------- RAMPS + Mega
    rx, ry, rw, rh = 104, 44, 78, 92
    bloco(ax, rx, ry, rw, rh, "", "", COR["ramps"], tam=11)
    ax.text(rx + 3, ry + rh - 3.2, "RAMPS 1.4 sobre o Arduino Mega 2560", fontsize=10.5, fontweight="bold", va="center", zorder=5)
    # bornes de potencia (lado esquerdo)
    e5p = pino(ax, rx, 127, "5A +", "d", COR["v12"])
    e5n = pino(ax, rx, 121, "5A −", "d", COR["gnd"])
    e11p = pino(ax, rx, 113, "11A +", "d", "#9e9e9e")
    e11n = pino(ax, rx, 107, "11A −", "d", "#9e9e9e")
    nota(ax, rx + 13, 110, "(não ligar)", 7, "#9e9e9e")
    d8p = pino(ax, rx, 97, "D8 +", "d", "#9e9e9e")
    d8n = pino(ax, rx, 91, "D8 −", "d", COR["v24"])
    nota(ax, rx + 12, 97, "(não ligar)", 7, "#9e9e9e")
    nota(ax, rx + 12, 91, "MOSFET da saída D8", 7)
    nota(ax, rx + 3, 82, "D9 e D10: livres", 7, "#9e9e9e")
    # soquetes dos drivers
    for i, (nome, yy, cor) in enumerate((("Driver X  (DRV8825)", 118, COR["a"]), ("Driver Y  (DRV8825)", 96, COR["b"]))):
        ax.add_patch(Rectangle((rx + 38, yy - 6), 26, 14, fc="#e8d5f0", ec=COR["borda"], lw=1, zorder=3))
        ax.text(rx + 51, yy + 5.5, nome, ha="center", va="center", fontsize=7.5, fontweight="bold", zorder=5)
        ax.text(rx + 51, yy + 1.0, "1/16 passo: só o jumper MS3\nVref 0,50 a 0,60 V", ha="center", va="center",
                fontsize=6.6, color="#455a64", zorder=5)
    # saidas dos motores (lado direito)
    mx = {}
    for nome, y0 in (("X", 124), ("Y", 102)):
        for k, lab in enumerate(("2B", "2A", "1A", "1B")):
            mx[nome + lab] = pino(ax, rx + rw, y0 - k * 3.6, lab, "e", COR["a"] if nome == "X" else COR["b"], 6.8)
    # fins de curso
    xmin_s = pino(ax, rx + rw, 80, "X− S  (D3)", "e", COR["sinal"], 7)
    xmin_g = pino(ax, rx + rw, 76, "X− GND", "e", COR["gnd"], 7)
    ymin_s = pino(ax, rx + rw, 68, "Y− S  (D14)", "e", COR["sinal"], 7)
    ymin_g = pino(ax, rx + rw, 64, "Y− GND", "e", COR["gnd"], 7)
    nota(ax, rx + rw - 26, 86, "barra ENDSTOPS", 7, "#455a64")
    # auxiliares (embaixo)
    bz_s = pino(ax, rx + 12, ry, "D4", "c", COR["opc"], 7)
    bz_g = pino(ax, rx + 18, ry, "GND", "c", COR["gnd"], 7)
    nota(ax, rx + 8, ry + 9.5, "barra SERVOS", 7, "#455a64")
    bt = [pino(ax, rx + 34 + i * 6, ry, n, "c", COR["opc"], 7) for i, n in enumerate(("A5", "A9", "A10"))]
    bt_g = pino(ax, rx + 52, ry, "GND", "c", COR["gnd"], 7)
    ld = [pino(ax, rx + 62 + i * 6, ry, n, "c", COR["opc"], 7) for i, n in enumerate(("D40", "D42"))]
    nota(ax, rx + 46, ry + 9.5, "conector AUX-2", 7, "#455a64")
    # USB
    usb = pino(ax, rx + 66, ry + rh, "", "b", COR["usb"], 7.5)
    bloco(ax, rx + 50, 142, 32, 9, "Computador", "painel de controle", COR["mega"], tam=8.5)
    fio(ax, [usb, (rx + 66, 142)], COR["usb"], 2.4)
    nota(ax, rx + 68, 139, "cabo USB do Mega", 7.2, COR["usb"])

    # 12 V e GND ate a RAMPS
    fio(ax, [ch_b, (100, 127), e5p], COR["v12"])
    fio(ax, [f_n, (40, 116), (40, 113), (100, 113), (100, 121), e5n], COR["gnd"])

    # ---------------- step-up + placa do solenoide
    bloco(ax, 6, 60, 34, 34, "Step-up XL6009", "ajuste a saída para\n24,0 V (máximo 32 V)", COR["mod"])
    su_ip = pino(ax, 6, 76, "IN +", "d", COR["v12"])
    su_in = pino(ax, 6, 66, "IN −", "d", COR["gnd"])
    su_op = pino(ax, 40, 76, "OUT +", "e", COR["v24"])
    su_on = pino(ax, 40, 66, "OUT −", "e", COR["gnd"])
    # derivacao dos 12 V (depois da chave)
    fio(ax, [(100, 127), (100, 139.5), (1.5, 139.5), (1.5, 76), su_ip], COR["v12"])
    no(ax, (100, 127), COR["v12"])
    fio(ax, [(40, 113), (40, 104), (3.5, 104), (3.5, 66), su_in], COR["gnd"])
    no(ax, (40, 113), COR["gnd"])

    bloco(ax, 50, 54, 44, 38, "Placa do solenoide", "placa perfurada 4 × 2,5 cm", "#ffffff")
    ps_p = pino(ax, 50, 76, "+24 V", "d", COR["v24"])
    ps_n = pino(ax, 50, 66, "GND", "d", COR["gnd"])
    ps_sp = pino(ax, 94, 76, "SOL +", "e", COR["v24"])
    ps_sn = pino(ax, 94, 68, "SOL −", "e", COR["v24"])
    ps_d8 = pino(ax, 94, 60, "D8 −", "e", COR["v24"])
    ax.text(71, 60.5, "C1 1000 µF 50 V\nR1 10 kΩ (descarga)\nD1 1N4007 (roda livre)\nLED1 + R2 2,2 kΩ", ha="center", va="center",
            fontsize=6.9, color="#37474f", zorder=6)
    fio(ax, [su_op, ps_p], COR["v24"])
    fio(ax, [su_on, ps_n], COR["gnd"])
    fio(ax, [ps_d8, (99, 60), (99, 91), d8n], COR["v24"])
    nota(ax, 42.0, 78.6, "24 V", 7.5, COR["v24"])

    bloco(ax, 50, 18, 44, 24, "", "", COR["amarelo"])
    ax.text(72, 34, "Solenoide JF-0826B", ha="center", va="center", fontsize=10, fontweight="bold", zorder=5)
    ax.text(72, 26, "24 V · 350 mA · 68 Ω\nno carro de cima (cabo flexível)", ha="center", va="center", fontsize=7.2, color="#455a64", zorder=5)
    so_p = pino(ax, 62, 42, "+", "e", COR["v24"])
    so_n = pino(ax, 82, 42, "−", "d", COR["v24"])
    fio(ax, [ps_sp, (97, 76), (97, 48), (62, 48), so_p], COR["v24"])
    fio(ax, [ps_sn, (96, 68), (96, 50.5), (82, 50.5), so_n], COR["v24"], ls=(0, (4, 1.5)))

    # ---------------- motores e sensores (direita)
    bloco(ax, 200, 108, 36, 24, "Motor X", "NEMA 17 17HS4401\ncarros (eixo vertical)", COR["mega"])
    bloco(ax, 200, 80, 36, 24, "Motor Y", "NEMA 17 17HS4401\nroletes do papel", COR["mega"])
    for nome, yb, cor, y0 in (("X", 108, COR["a"], 124), ("Y", 80, COR["b"], 102)):
        for k, lab in enumerate(("2B", "2A", "1A", "1B")):
            yy = yb + 19 - k * 4.6
            fio(ax, [mx[nome + lab], (rx + rw + 6 + k * 2.2, y0 - k * 3.6), (rx + rw + 6 + k * 2.2, yy), (200, yy)], cor, 1.6)
            ax.add_patch(Circle((200, yy), 0.7, fc="white", ec=cor, lw=1.2, zorder=6))
    nota(ax, 200, 134.5, "bobina 1 = par 1A/1B · bobina 2 = par 2A/2B", 6.5)

    bloco(ax, 200, 60, 36, 17, "Fim de curso X", "microchave: C e NF", "#ffffff", tam=9)
    fc_s = pino(ax, 200, 71, "NF", "d", COR["sinal"], 7)
    fc_g = pino(ax, 200, 64, "C", "d", COR["gnd"], 7)
    fio(ax, [xmin_s, (190, 80), (190, 71), fc_s], COR["sinal"], 1.6)
    fio(ax, [xmin_g, (187.5, 76), (187.5, 64), fc_g], COR["gnd"], 1.6)
    bloco(ax, 200, 40, 36, 17, "Sensor de papel", "microchave: C e NA", "#ffffff", tam=9)
    sp_s = pino(ax, 200, 51, "NA", "d", COR["sinal"], 7)
    sp_g = pino(ax, 200, 44, "C", "d", COR["gnd"], 7)
    fio(ax, [ymin_s, (194.5, 68), (194.5, 51), sp_s], COR["sinal"], 1.6)
    fio(ax, [ymin_g, (192.2, 64), (192.2, 44), sp_g], COR["gnd"], 1.6)

    # ---------------- opcionais (embaixo)
    bloco(ax, 104, 4, 132, 26, "", "", "#f5fbfc", tracejado=True)
    ax.text(107, 27, "Opcionais recomendados (aviso sonoro e botões ajudam o usuário cego)", fontsize=8.2,
            fontweight="bold", color=COR["opc"], va="center", zorder=6)
    bloco(ax, 108, 7, 26, 15, "Buzzer passivo", "com resistor de 100 Ω", "#ffffff", tam=8)
    bloco(ax, 140, 7, 44, 15, "3 botões", "carregar · testar · cancelar\n(cada um entre o pino e o GND)", "#ffffff", tam=8)
    bloco(ax, 190, 7, 42, 15, "2 LEDs", "verde D40 e vermelho D42\ncada um com 330 Ω para o GND", "#ffffff", tam=8)
    fio(ax, [bz_s, (rx + 12, 36), (115, 36), (115, 22)], COR["opc"], 1.6)
    fio(ax, [bz_g, (rx + 18, 39), (127, 39), (127, 22)], COR["gnd"], 1.6)
    for i, p in enumerate(bt):
        fio(ax, [p, (p[0], 32.4 + i * 1.6), (146 + i * 8, 32.4 + i * 1.6), (146 + i * 8, 22)], COR["opc"], 1.6)
    fio(ax, [bt_g, (bt_g[0], 39.4), (176, 39.4), (176, 22)], COR["gnd"], 1.6)
    for i, p in enumerate(ld):
        fio(ax, [p, (p[0], 37.4 - i * 2.0), (203 + i * 14, 37.4 - i * 2.0), (203 + i * 14, 22)], COR["opc"], 1.6)

    # ---------------- legenda
    lx, ly = 6, 50
    for i, (cor, txt) in enumerate(((COR["v12"], "+12 V (1,0 mm²)"), (COR["v24"], "24 V do solenoide (0,5 mm²)"),
                                    (COR["gnd"], "GND / negativo"), (COR["sinal"], "sinal (0,14 a 0,25 mm²)"),
                                    (COR["a"], "motor X"), (COR["b"], "motor Y"), (COR["opc"], "opcional"))):
        fio(ax, [(lx, ly - i * 4.6), (lx + 9, ly - i * 4.6)], cor, 2.6)
        nota(ax, lx + 11, ly - i * 4.6, txt, 7.8)
    nota(ax, 6, 10, "Antes de ligar o solenoide: ajuste o step-up para 24,0 V\ncom o multímetro, SEM nada na saída.", 7.6,
         "#b71c1c")
    nota(ax, 6, 3.5, "O Mega recebe 12 V pela própria RAMPS (diodo D1);\nnão ligue nada no jack preto do Mega.", 7.6)
    for ext in ("png", "svg"):
        fig.savefig(os.path.join(AQUI, "esquema_ligacao." + ext), bbox_inches="tight", facecolor="white")
    plt.close(fig)


# ============================================================================ 2) circuito do solenoide
def resistor(ax, x, y0, y1, nome, valor, lado=1):
    """Resistor vertical entre y0 (baixo) e y1 (cima)."""
    ym = (y0 + y1) / 2
    fio(ax, [(x, y0), (x, ym - 4)], "#212121", 1.6)
    fio(ax, [(x, ym + 4), (x, y1)], "#212121", 1.6)
    ax.add_patch(Rectangle((x - 1.6, ym - 4), 3.2, 8, fc="white", ec="#212121", lw=1.6, zorder=5))
    ax.text(x + lado * 3.2, ym, nome + "\n" + valor, ha="left" if lado > 0 else "right", va="center", fontsize=8.5, zorder=6)


def capacitor(ax, x, y0, y1, nome, valor):
    ym = (y0 + y1) / 2
    fio(ax, [(x, y0), (x, ym - 1)], "#212121", 1.6)
    fio(ax, [(x, ym + 1), (x, y1)], "#212121", 1.6)
    fio(ax, [(x - 3.2, ym + 1), (x + 3.2, ym + 1)], "#212121", 2.4)
    fio(ax, [(x - 3.2, ym - 1), (x + 3.2, ym - 1)], "#212121", 2.4)
    ax.text(x - 4.2, ym + 2.6, "+", ha="center", va="center", fontsize=10, zorder=6)
    ax.text(x + 4.4, ym, nome + "\n" + valor, ha="left", va="center", fontsize=8.5, zorder=6)


def diodo(ax, x, y0, y1, nome, valor, led=False, lado=1, para_baixo=False):
    """Diodo vertical. Normal: anodo embaixo (y0), catodo em cima (y1), conduz para cima.
    para_baixo=True inverte: anodo em cima, catodo embaixo."""
    ym = (y0 + y1) / 2
    k = -1 if para_baixo else 1
    fio(ax, [(x, y0), (x, ym - 2.2)], "#212121", 1.6)
    fio(ax, [(x, ym + 2.2), (x, y1)], "#212121", 1.6)
    ax.add_patch(Polygon([(x - 2.6, ym - k * 2.2), (x + 2.6, ym - k * 2.2), (x, ym + k * 2.2)], closed=True,
                         fc="#212121" if not led else "#ef5350", ec="#212121", lw=1.4, zorder=5))
    fio(ax, [(x - 2.6, ym + k * 2.2), (x + 2.6, ym + k * 2.2)], "#212121", 2.2)
    if led:
        for d in (0, 1.8):
            ax.annotate("", xy=(x - 6.0, ym + 2.5 + d), xytext=(x - 3.4, ym + d), arrowprops=dict(arrowstyle="->", lw=1.0), zorder=6)
    ax.text(x + lado * 4.0, ym, nome + "\n" + valor, ha="left" if lado > 0 else "right", va="center", fontsize=8.5, zorder=6)


def bobina(ax, x, y0, y1, nome, valor):
    n = 5
    h = (y1 - y0 - 8) / n
    fio(ax, [(x, y0), (x, y0 + 4)], "#212121", 1.6)
    fio(ax, [(x, y1 - 4), (x, y1)], "#212121", 1.6)
    import numpy as np
    for i in range(n):
        t = np.linspace(-np.pi / 2, np.pi / 2, 30)
        ax.plot(x + 2.4 * np.cos(t), y0 + 4 + h * (i + 0.5) + (h / 2) * np.sin(t), color="#212121", lw=1.8, zorder=5)
    ax.text(x + 4.6, (y0 + y1) / 2, nome + "\n" + valor, ha="left", va="center", fontsize=8.5, zorder=6)


def solenoide():
    fig, ax = plt.subplots(figsize=(13.5, 7.6), dpi=110)
    ax.set_xlim(0, 180)
    ax.set_ylim(0, 100)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.text(3, 96, "Circuito do solenoide", fontsize=16, fontweight="bold", va="center")
    ax.text(3, 91, "O MOSFET da saída D8 da RAMPS fecha o negativo do solenoide; o positivo vem do step-up.", fontsize=9.5,
            color="#455a64", va="center")
    yT, yG = 74, 14            # barramento +24 V e GND
    # entrada 12 V
    ax.text(3, yT + 2.0, "+12 V", fontsize=10, color=COR["v12"], fontweight="bold", va="bottom")
    ax.text(3, yT - 2.0, "depois do fusível\ne da chave", fontsize=7.6, color="#455a64", va="top")
    fio(ax, [(3, yT), (30, yT)], COR["v12"], 2.2)
    ax.add_patch(Rectangle((30, 58), 26, 22, fc=COR["mod"], ec=COR["borda"], lw=1.4, zorder=3))
    ax.text(43, 73, "Step-up\nXL6009", ha="center", va="center", fontsize=10, fontweight="bold", zorder=5)
    ax.text(43, 63.5, "12 V → 24 V\n(trimpot: 24 a 32 V)", ha="center", va="center", fontsize=7.4, color="#455a64", zorder=5)
    fio(ax, [(4, yG), (172, yG)], COR["gnd"], 2.2)
    ax.text(4, yG - 2.6, "GND (comum com a RAMPS)", fontsize=8.5, va="top")
    fio(ax, [(52, 58), (52, yG)], COR["gnd"], 2.0)
    no(ax, (52, yG), COR["gnd"])
    fio(ax, [(56, yT), (150, yT)], COR["v24"], 2.2)
    ax.text(58, yT + 2.2, "+24 V", fontsize=10, color=COR["v24"], fontweight="bold", va="bottom")
    # C1 e R1
    capacitor(ax, 68, yG, yT, "C1", "1000 µF\n50 V")
    no(ax, (68, yT), COR["v24"]); no(ax, (68, yG), COR["gnd"])
    resistor(ax, 90, yG, yT, "R1", "10 kΩ\n¼ W")
    no(ax, (90, yT), COR["v24"]); no(ax, (90, yG), COR["gnd"])
    # ramo do solenoide: tres caminhos em paralelo entre +24 V e o no do dreno
    yD = 40
    bobina(ax, 132, yD, yT, "L1 solenoide", "JF-0826B\n24 V · 68 Ω")
    no(ax, (132, yT), COR["v24"])
    diodo(ax, 112, yD, yT, "D1", "1N4007", lado=-1)
    no(ax, (112, yT), COR["v24"])
    fio(ax, [(150, yT), (150, yT - 1)], COR["v24"], 1.6)
    resistor(ax, 150, 56, yT, "R2", "2,2 kΩ")
    diodo(ax, 150, yD, 56, "LED1", "acende a\ncada ponto", led=True, para_baixo=True)
    # o LED conduz de cima para baixo: desenha a seta de corrente
    ax.text(150, yD + 16.6, "", fontsize=1)
    fio(ax, [(112, yD), (150, yD)], "#212121", 1.8)
    no(ax, (132, yD), "#212121")
    # MOSFET
    xm = 132
    fio(ax, [(xm, yD), (xm, 32)], "#212121", 1.8)
    ax.add_patch(Rectangle((xm - 9, 19), 18, 13, fc=COR["ramps"], ec=COR["borda"], lw=1.4, zorder=3))
    ax.text(xm, 27.8, "MOSFET Q3", ha="center", va="center", fontsize=8.5, fontweight="bold", zorder=5)
    ax.text(xm, 22.8, "saída D8 da RAMPS", ha="center", va="center", fontsize=7.4, color="#455a64", zorder=5)
    fio(ax, [(xm, 19), (xm, yG)], COR["gnd"], 1.8)
    no(ax, (xm, yG), COR["gnd"])
    fio(ax, [(xm + 9, 25.5), (xm + 22, 25.5)], COR["sinal"], 1.8)
    ax.text(xm + 23, 25.5, "pino D8 do Mega\n(5 V = solenoide ligado)", ha="left", va="center", fontsize=8.2, color=COR["sinal"])
    ax.text(xm + 2.0, 35.8, "borne  D8 −", ha="left", va="center", fontsize=8.2)
    # observacoes
    ax.text(95, 28, "D1 fica ao contrário:\ncatodo (faixa) no +24 V.\nSem ele, o pico da bobina\nqueima o MOSFET.", fontsize=7.4, va="center",
            ha="left", color="#b71c1c")
    ax.text(3, 52, "Contas\n"
                   "I = 24 V ÷ 68 Ω = 0,35 A (8,4 W)\n"
                   "a 30 V: 0,44 A (13 W, +56 % de força)\n"
                   "pulso de 25 ms, no máximo 10 por segundo\n"
                   "R2: (24 − 2) ÷ 2200 = 10 mA no LED\n"
                   "R1 descarrega C1 ao desligar: 24² ÷ 10 k = 0,06 W", fontsize=8.2, va="top", color="#263238",
            bbox=dict(fc=COR["amarelo"], ec="#bdbdbd", pad=4))
    for ext in ("png", "svg"):
        fig.savefig(os.path.join(AQUI, "esquema_solenoide." + ext), bbox_inches="tight", facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    ligacao()
    solenoide()
    print("ok")
