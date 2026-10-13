# -*- coding: utf-8 -*-
"""
Impressora Braille - parametros do projeto mecanico (fonte unica de medidas).

Tudo em milimetros. Este arquivo nao depende do FreeCAD: e lido pelo gerador
do CAD, pelos testes e pelos scripts que conferem o firmware.

Sistema de coordenadas da maquina:
  X = esquerda -> direita (curso dos carros). x = 0 na face INTERNA da lateral esquerda.
  Y = frente  -> tras    (avanco do papel).   y = 0 na LINHA DE PUNCAO. O papel entra
      por tras (+y) e sai pela frente (-y).
  Z = para cima. z = 0 no topo da base (piso interno).
"""

# ---------------------------------------------------------------- material
T = 6.0                 # espessura do MDF (mude aqui se cortar em outra chapa)
FOLGA_ENC = 0.15        # folga somada aos rasgos de encaixe (largura = T + folga)
FOLGA_TAB = 0.20        # folga no comprimento dos rasgos
FURO_EIXO_MDF = 8.0     # furo dos eixos de 8 mm nas laterais (acerte com o gabarito de teste)

# ---------------------------------------------------------------- pecas do estoque
D_EIXO = 8.0
L_EIXO_X = 330.0        # 4 eixos dos carros
L_EIXO_PAPEL = 366.0    # eixo dos roletes de tracao
L_EIXO_VERT = 103.0     # eixo vertical que sincroniza as duas correias

LM8_D, LM8_L = 15.0, 24.0           # bucha linear LM8UU
R608_D, R608_d, R608_B = 22.0, 8.0, 7.0   # rolamento 608

# polia GT2 20 dentes (furo 8 ou 5): flange 16, altura total 16
POLIA_FLANGE_D = 16.0
POLIA_H = 16.0
POLIA_CUBO_H = 7.0      # parte lisa com os parafusos allen
POLIA_DENTES = 20
GT2_PASSO = 2.0
POLIA_DP = POLIA_DENTES * GT2_PASSO / 3.14159265   # diametro primitivo = 12,73
POLIA_CORREIA_C = 4.5   # centro da correia medido a partir da ponta COM flange (sem cubo)

# polia lisa (tensora) furo 5
TENS_FLANGE_D = 18.0
TENS_D = 12.0
TENS_H = 8.5

ACOPL_D, ACOPL_L = 19.0, 25.0       # acoplamento flexivel 5x8
ACOPL_ENT = 11.0                    # quanto cada eixo entra no acoplamento

NEMA_L = 42.3           # lado do NEMA 17
NEMA_H = 40.0           # corpo do 17HS4401
NEMA_FUROS = 31.0       # entre furos M3
NEMA_RESSALTO_D, NEMA_RESSALTO_H = 22.0, 2.0
NEMA_EIXO_D, NEMA_EIXO_L = 5.0, 24.0

# solenoide JF-0826B (medidas de catalogo: CONFERIR com paquimetro)
SOL_L = 27.0            # comprimento do quadro, na direcao do embolo
SOL_W = 25.0            # largura do quadro
SOL_H = 22.0            # altura do quadro
SOL_EMBOLO_D = 8.0
SOL_COMP_TOTAL = 55.0
SOL_CURSO = 10.0

# microchave tipo KW11-3Z
MS_L, MS_E, MS_A = 19.8, 6.4, 10.2
MS_FUROS = 9.5
MS_FURO_D = 2.4

# ---------------------------------------------------------------- caixa
W_IN = L_EIXO_X - 2 * T   # largura interna: os eixos de 330 atravessam as duas laterais
YF = 68.0                 # parede frontal interna em y = -YF
YB = 82.0                 # parede traseira interna em y = +YB
H_IN = 222.0              # altura interna (topo das paredes)
SAIA = 8.0                # paredes descem abaixo da base (viram pe e protegem as cabecas dos parafusos)
ABA = 8.0                 # laterais passam das paredes frontal e traseira

# ---------------------------------------------------------------- papel
Z_P = 126.0               # plano do papel = topo da mesa traseira
DEGRAU = 1.0              # mesa frontal mais baixa, para os pontos (que saem por baixo) nao rasparem
FENDA = 10.0              # vao entre a mesa traseira e a frontal (linha de puncao no meio)
PAPEL_W = 210.0           # A4
PAPEL_L = 297.0
X_PAPEL0 = W_IN / 2 - PAPEL_W / 2   # borda esquerda do A4
ABERT_W = 250.0           # largura das aberturas de entrada/saida e das linguetas das mesas
X_ABERT0 = W_IN / 2 - ABERT_W / 2
LINGUETA_TRAS = 110.0     # bandeja de entrada para fora da caixa
LINGUETA_FRENTE = 30.0

# ---------------------------------------------------------------- eixos dos carros
Y_EIXO_SUP = 25.0         # eixos do carro de cima em y = +-25
Z_EIXO_SUP = Z_P + 14.0
Y_EIXO_INF = 20.0         # eixos do carro de baixo em y = +-20
Z_EIXO_INF = Z_P - 20.0

CARRO_L = 56.0            # comprimento dos carros em X
X_CARRO_MIN = 62.0        # centro do carro encostado no fim de curso (home)
X_CARRO_MAX = 258.0
X_CARRO_REF = 150.0       # posicao em que o conjunto e desenhado

# ---------------------------------------------------------------- transmissao X
X_EIXO_V = 23.0           # eixo vertical (y = 0)
X_TENS = 296.0            # polias tensoras (posicao nominal)
Z_COR_SUP = Z_EIXO_SUP    # plano da correia de cima
Z_COR_INF = Z_EIXO_INF    # plano da correia de baixo

# pilha do eixo vertical (cotas z absolutas)
Z_POLIA_SUP_BASE = Z_COR_SUP - POLIA_CORREIA_C          # flange de baixo; cubo para cima
Z_POLIA_SUP_TOPO = Z_POLIA_SUP_BASE + POLIA_H
Z_ROL_SUP = Z_P + 36.0                                  # base do 608 de cima
Z_POLIA_INF_TOPO = Z_COR_INF + POLIA_CORREIA_C          # flange de cima; cubo para baixo
Z_POLIA_INF_BASE = Z_POLIA_INF_TOPO - POLIA_H
Z_ROL_INF = Z_POLIA_INF_BASE - 1.5 - R608_B             # base do 608 de baixo
Z_ACOPL_TOPO = Z_ROL_INF - 2.0
Z_ACOPL_BASE = Z_ACOPL_TOPO - ACOPL_L
Z_EIXO_V_BASE = Z_ACOPL_TOPO - ACOPL_ENT - 1.0
Z_EIXO_V_TOPO = Z_EIXO_V_BASE + L_EIXO_VERT
Z_MOTOR_X_FACE = Z_ACOPL_BASE + ACOPL_ENT - NEMA_EIXO_L  # face do motor (eixo para cima)

# ---------------------------------------------------------------- tracao do papel
Y_ROLO = 48.0             # eixo dos roletes, atras da linha de puncao
ROLO_D = 26.5             # diametro efetivo do rolete com o O-ring 20x3 esticado no canal de 20,6
ROLO_L = 18.0             # o O-ring fica a 5,7 mm de uma ponta; o parafuso de trava, do outro lado
ROLO_SALIENCIA = 0.7      # quanto o O-ring passa acima da mesa
Z_ROLO = Z_P + ROLO_SALIENCIA - ROLO_D / 2
X_ROLOS = (W_IN / 2 - 70.0, W_IN / 2 + 70.0)
EIXO_PAPEL_ESQ = 12.0     # sobra do eixo para fora da lateral esquerda
X_POLIA_Y = 6.0           # inicio da polia do eixo do papel (lado da parede)
CORREIA_Y_L = 200.0       # correia fechada GT2
DIST_MOTOR_Y = (CORREIA_Y_L - POLIA_DENTES * GT2_PASSO) / 2.0   # 80 mm entre centros
Y_MOTOR_Y = Y_ROLO + 3.0
Z_MOTOR_Y = Z_ROLO - (DIST_MOTOR_Y ** 2 - 3.0 ** 2) ** 0.5
X_MOTOR_Y_FACE = 27.0     # face do motor Y (eixo apontando para a lateral esquerda)
AJUSTE_MOTOR_Y = 4.0      # +- curso dos rasgos que esticam a correia fechada

# ---------------------------------------------------------------- encaixes entre chapas
# intervalos (inicio, fim) das linguetas e posicoes dos parafusos com porca presa ("T")
TAB_BASE_LAT = ((-58.0, -38.0), (-8.0, 12.0), (42.0, 62.0))    # ao longo de y
T_BASE_LAT = (-23.0, 27.0)
TAB_BASE_FT = ((20.0, 60.0), (139.0, 179.0), (258.0, 298.0))   # ao longo de x
T_BASE_FT = (100.0, 218.0)
TAB_FT_LAT = ((15.0, 45.0), (85.0, 115.0), (170.0, 200.0))     # ao longo de z
T_FT_LAT = (65.0, 142.0)
TAB_MESA_T = ((12.0, 32.0), (60.0, 78.0))                      # mesa traseira, ao longo de y
TAB_MESA_F = ((-60.0, -40.0), (-30.0, -12.0))                  # mesa frontal
PARAF_T_L = 16.0          # parafuso M3 x 16 das juntas em T

# ---------------------------------------------------------------- puncao e matriz
SOL_Z_BASE = Z_P + 32.5   # face de baixo do solenoide (ajustavel com calcos)
PONTA_PROF = 1.8          # ponta do puncao no fim da batida, abaixo do plano do papel:
                          # 1,2 ate o topo da matriz + 0,6 dentro do sextavado
MATRIZ_Z = Z_P - 1.2      # topo do parafuso-matriz
CURSO_USADO = 5.0

# ---------------------------------------------------------------- eletronica (posicao no piso)
X_MEGA = 200.0            # canto da placa (lado do conector de alimentacao)
Y_MEGA_USB = YB - 16.0    # borda da placa do lado do USB (recuada: o borne verde da RAMPS passa 12 mm da placa)
MEGA_L, MEGA_W = 101.6, 53.34
MEGA_FUROS = ((13.97, 2.54), (15.24, 50.8), (90.17, 2.54), (96.52, 50.8))
Z_PCB_MEGA = 8.5          # face de baixo da placa acima do piso (bandeja 2,5 + pilar 6)

# ---------------------------------------------------------------- braille (padrao papel)
BR_PONTO = 2.5            # entre pontos da mesma cela
BR_CELA = 6.0             # entre celas
BR_LINHA = 10.0           # entre linhas
BR_PONTO_D = 1.5          # base do ponto
BR_PONTO_H = 0.5          # altura do ponto


def resumo():
    """Numeros derivados usados na documentacao e no firmware."""
    import math
    passos_rev = 200 * 16
    return {
        "largura_interna": W_IN,
        "largura_externa": W_IN + 2 * T,
        "profundidade_externa": YF + YB + 2 * T + 2 * ABA,
        "altura_externa": H_IN + T + SAIA,
        "curso_x": X_CARRO_MAX - X_CARRO_MIN,
        "x_papel_esq": X_PAPEL0,
        "margem_esq_min": X_CARRO_MIN - X_PAPEL0,
        "margem_dir_min": X_PAPEL0 + PAPEL_W - X_CARRO_MAX,
        "celas_max": int((X_CARRO_MAX - X_CARRO_MIN - BR_PONTO) // BR_CELA) + 1,
        "passos_mm_x": passos_rev / (POLIA_DENTES * GT2_PASSO),
        "passos_mm_y": passos_rev / (math.pi * ROLO_D),
        "dist_rolo_puncao": Y_ROLO,
        "correia_x_comprimento": 2 * (X_TENS - X_EIXO_V) + POLIA_DENTES * GT2_PASSO,
        "z_motor_x_base": Z_MOTOR_X_FACE - NEMA_H,
        "eixo_vertical": (Z_EIXO_V_BASE, Z_EIXO_V_TOPO),
    }


if __name__ == "__main__":
    for k, v in resumo().items():
        print(f"{k:28s} {v}")
