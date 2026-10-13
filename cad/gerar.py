# -*- coding: utf-8 -*-
"""Gera todos os arquivos de fabricacao a partir do modelo. Roda no FreeCAD em modo console:
    freecadcmd gerar.py        (ou ./rodar.sh gerar)

Saidas (pasta cad/saida):
  stl/                 pecas para imprimir, ja deitadas na orientacao certa
  step/                as mesmas pecas em STEP
  corte_laser/         cada chapa de MDF em DXF e SVG (1:1, mm) + pranchas montadas
  lista_pecas.json     tudo que entra na maquina (para a documentacao)
  ../../simulador/modelo.js   malhas para o visualizador 3D
"""
import os
import sys
import json
import math
import base64
import struct

AQUI = os.path.dirname(os.path.abspath(__file__))
if AQUI not in sys.path:
    sys.path.insert(0, AQUI)

import FreeCAD as App
import Part
import MeshPart
import parametros as P
from fc_util import *
import maquina
import desenho2d as D

SAIDA = os.path.join(AQUI, "saida")
DENS_PLA = 1.24e-3      # g/mm3
FATOR_PREENCH = 0.55    # fracao do volume que vira plastico (3 paredes + 30 % de preenchimento)

# de qual copia sai o STL quando a peca aparece mais de uma vez (ou espelhada)
FONTE_STL = {"trava_eixos": "trava_eixos_sup_dir", "mancal_eixo_papel": "mancal_eixo_papel_dir",
             "esticador": "esticador_sup", "rolete": "rolete_1", "pressor_base": "pressor_base_1",
             "pressor_braco": "pressor_braco_1", "bucha_608": "bucha_608_1",
             "espacador_bucha_curto": "espacador_bucha_curto_sup", "espacador_bucha_longo": "espacador_bucha_longo_sup_1",
             "suporte_modulo": "suporte_stepup"}

ROTULOS = {  # nome gravado em cada chapa: (texto, posicao u, v em mm a partir do canto do desenho)
    "lateral_esquerda": ("LATERAL ESQUERDA (face de dentro)", 30.0, 205.0),
    "lateral_direita": ("LATERAL DIREITA (face de fora)", 30.0, 205.0),
    "parede_frontal": ("FRENTE", 20.0, 215.0),
    "parede_traseira": ("TRAS", 20.0, 215.0),
    "base": ("BASE (vista de cima)", 60.0, 60.0),
    "mesa_traseira": ("MESA TRASEIRA (entrada do papel)", 110.0, 150.0),
    "mesa_frontal": ("MESA FRONTAL (saida)", 110.0, 50.0),
}


def garante(p):
    os.makedirs(p, exist_ok=True)
    return p


def deita(forma, giros):
    f = forma.copy()
    for eixo, graus in giros:
        f.rotate(V(0, 0, 0), EIXOS[eixo], graus)
    bb = f.BoundBox
    f.translate(V(-(bb.XMin + bb.XLength / 2), -(bb.YMin + bb.YLength / 2), -bb.ZMin))
    return f


def analisa_impressao(f):
    """Area de apoio na mesa e area de faces viradas para baixo fora da mesa (pontes/balancos)."""
    apoio = 0.0
    balanco = 0.0
    maior = 0.0
    for face in f.Faces:
        try:
            u0, u1, v0, v1 = face.ParameterRange
            n = face.normalAt((u0 + u1) / 2, (v0 + v1) / 2)
        except Exception:
            continue
        zc = face.CenterOfMass.z
        if n.z < -0.99 and face.BoundBox.ZMax < 0.05:
            apoio += face.Area
        elif n.z < -0.75 and zc > 0.3 and type(face.Surface).__name__ == "Plane":
            balanco += face.Area
            maior = max(maior, face.Area)
    return apoio, balanco, maior


def exporta_impressas(m, rel):
    d_stl = garante(os.path.join(SAIDA, "stl"))
    d_step = garante(os.path.join(SAIDA, "step"))
    qtd = m.pecas("impresso")
    por_nome = {i["nome"]: i for i in m.itens}
    linhas = []
    for peca, n in qtd.items():
        fonte = FONTE_STL.get(peca, peca)
        it = por_nome.get(fonte)
        if it is None:
            it = next(i for i in m.por_tipo("impresso") if i["peca"] == peca)
        giros = maquina.ORIENTACAO.get(peca)
        if giros is None:
            raise KeyError("sem orientacao de impressao para " + peca)
        f = deita(it["forma"], giros)
        bb = f.BoundBox
        malha = MeshPart.meshFromShape(Shape=f, LinearDeflection=0.03, AngularDeflection=0.20, Relative=False)
        malha.write(os.path.join(d_stl, peca + ".stl"))
        f.exportStep(os.path.join(d_step, peca + ".step"))
        apoio, balanco, maior = analisa_impressao(f)
        massa = f.Volume * DENS_PLA * FATOR_PREENCH
        linhas.append(dict(peca=peca, qtd=n, x=round(bb.XLength, 1), y=round(bb.YLength, 1), z=round(bb.ZLength, 1),
                           volume_cm3=round(f.Volume / 1000.0, 2), massa_g=round(massa, 1),
                           apoio_mm2=round(apoio), ponte_mm2=round(balanco), maior_ponte_mm2=round(maior),
                           triangulos=malha.CountFacets, solido_ok=bool(f.isValid() and malha.isSolid())))
    rel["impressas"] = linhas
    return linhas


def exporta_chapas(m, rel):
    d = garante(os.path.join(SAIDA, "corte_laser"))
    pecas = []
    desenhos = {}
    linhas = []
    for it in m.por_tipo("mdf"):
        larg, alt, conts = D.contornos(it["forma"])
        desenhos[it["nome"]] = (larg, alt, conts)
        rot = ROTULOS.get(it["nome"])
        textos = [(rot[1], rot[2], 4.0, rot[0])] if rot else []
        D.escreve_dxf(os.path.join(d, it["nome"] + ".dxf"), conts, textos)
        D.escreve_svg(os.path.join(d, it["nome"] + ".svg"), larg, alt, conts, textos)
        pecas.append((it["nome"], larg, alt))
        n_furos = sum(1 for c in conts if c[0] == "circulo")
        n_cont = len(conts)
        area = it["forma"].Volume / P.T
        linhas.append(dict(peca=it["nome"], largura=round(larg, 1), altura=round(alt, 1), contornos=n_cont,
                           furos_redondos=n_furos, area_cm2=round(area / 100.0, 1),
                           massa_g=round(it["forma"].Volume * 0.75e-3)))
    rel["chapas"] = linhas
    # pranchas
    pranchas = {}
    for nome_ch, (lc, ac) in (("600x400", (600.0, 400.0)), ("900x600", (900.0, 600.0))):
        try:
            chapas = D.encaixa(pecas, lc, ac)
        except ValueError as e:
            rel["aviso_" + nome_ch] = str(e)
            continue
        pranchas[nome_ch] = len(chapas)
        for i, chapa in enumerate(chapas):
            tudo, textos = [], []
            for nome, x, y, gir in chapa:
                larg, alt, conts = desenhos[nome]
                rot = ROTULOS.get(nome)
                tx = [(rot[1], rot[2], 4.0, rot[0])] if rot else []
                if gir:
                    larg, alt, conts = D.gira90(larg, alt, conts)
                    tx = [(8.0, 8.0, 4.0, rot[0])] if rot else []
                tudo.extend(D.desloca(conts, x, y))
                textos.extend([(a + x, b + y, h, t) for a, b, h, t in tx])
            base = os.path.join(d, "prancha_%s_%d_de_%d" % (nome_ch, i + 1, len(chapas)))
            D.escreve_dxf(base + ".dxf", tudo, textos)
            D.escreve_svg(base + ".svg", lc, ac, tudo, textos, moldura=True)
    rel["pranchas"] = pranchas


def exporta_gabarito():
    """Pecinha de teste: corte ANTES das chapas grandes para acertar a folga da sua maquina."""
    d = garante(os.path.join(SAIDA, "corte_laser"))
    T = P.T
    placa = box(0, 90, 0, 60, 0, T)
    cortes = [box(10, 10 + 20 + P.FOLGA_TAB, 40, 40 + T + P.FOLGA_ENC, -1, T + 1),      # rasgo de encaixe
              cylz(7.9, 45, 45, -1, T + 1), cylz(8.0, 58, 45, -1, T + 1), cylz(8.1, 71, 45, -1, T + 1),
              cylz(3.4, 82, 50, -1, T + 1), cylz(12.5, 76, 22, -1, T + 1),
              box(-0.01, P.PARAF_T_L - T + 1.0, 20 - 1.7, 20 + 1.7, -1, T + 1),         # junta em T
              box(4.5, 4.5 + 2.7, 20 - 2.85, 20 + 2.85, -1, T + 1)]
    placa = dif(placa, cortes)
    macho = uni(box(0, 40, 0, 25, 0, T), box(10, 30, 25, 25 + T, 0, T))
    macho = dif(macho, cylz(3.4, 20, 12, -1, T + 1))
    l1, a1, c1 = D.contornos(placa)
    l2, a2, c2 = D.contornos(macho)
    tudo = c1 + D.desloca(c2, 95.0, 0.0)
    textos = [(42.0, 34.0, 3.0, "7,9"), (55.0, 34.0, 3.0, "8,0"), (68.0, 34.0, 3.0, "8,1"), (20.0, 5.0, 3.5, "TESTE MDF %g mm" % T)]
    D.escreve_dxf(os.path.join(d, "gabarito_teste.dxf"), tudo, textos)
    D.escreve_svg(os.path.join(d, "gabarito_teste.svg"), 135.0, 60.0, tudo, textos)


def exporta_listas(m, rel):
    rel["comprados"] = [dict(peca=k, qtd=v) for k, v in m.pecas("comprado").items()]
    rel["ferragens"] = [dict(peca=k, qtd=v) for k, v in sorted(m.ferragens.items())]
    rel["resumo"] = P.resumo()
    usos = {}
    for it in m.por_tipo("ferragem"):
        if it["obs"]:
            usos.setdefault(it["peca"], {})
            usos[it["peca"]][it["obs"]] = usos[it["peca"]].get(it["obs"], 0) + 1
    rel["usos_parafusos"] = usos


# ---------------------------------------------------------------- visualizador
def _b64(fmt, valores):
    return base64.b64encode(struct.pack("<%d%s" % (len(valores), fmt), *valores)).decode("ascii")


def exporta_visualizador(m, rel):
    pasta = garante(os.path.join(AQUI, "..", "simulador"))
    ESC = 0.02                    # mm por unidade (int16)
    partes = []
    n_tri = 0
    for it in m.itens:
        if it["nome"] == "papel_a4":
            continue
        tol = 0.25 if it["tipo"] == "mdf" else (0.12 if it["tipo"] != "ferragem" else 0.3)
        pts, tris = it["forma"].tessellate(tol)
        if not tris:
            continue
        v = []
        for p in pts:
            v.extend((int(round(p.x / ESC)), int(round(p.y / ESC)), int(round(p.z / ESC))))
        idx = [i for t in tris for i in t]
        if max(abs(a) for a in v) > 32767 or len(pts) > 65535:
            raise ValueError("malha fora da faixa: " + it["nome"])
        partes.append(dict(n=it["nome"], t=it["tipo"], g=it["grupo"], p=it["peca"],
                           c=[round(c, 3) for c in it["cor"]], v=_b64("h", v), i=_b64("H", idx)))
        n_tri += len(tris)
    dados = dict(escala=ESC, partes=partes, par=dict(
        Z_P=P.Z_P, DEGRAU=P.DEGRAU, X_REF=P.X_CARRO_REF, X_MIN=P.X_CARRO_MIN, X_MAX=P.X_CARRO_MAX,
        CURSO=P.CURSO_USADO, Y_ROLO=P.Y_ROLO, Z_ROLO=P.Z_ROLO, ROLO_D=P.ROLO_D, X_PAPEL0=P.X_PAPEL0,
        PAPEL_W=P.PAPEL_W, PAPEL_L=P.PAPEL_L, W_IN=P.W_IN, T=P.T, X_EIXO_V=P.X_EIXO_V, POLIA_DP=P.POLIA_DP,
        BR_PONTO=P.BR_PONTO, BR_CELA=P.BR_CELA, BR_LINHA=P.BR_LINHA, YF=P.YF, YB=P.YB, H_IN=P.H_IN))
    with open(os.path.join(pasta, "modelo.js"), "w", encoding="utf-8") as f:
        f.write("// gerado por cad/gerar.py - nao editar\nwindow.MODELO = ")
        json.dump(dados, f, separators=(",", ":"))
        f.write(";\n")
    rel["visualizador"] = dict(pecas=len(partes), triangulos=n_tri)


def main():
    garante(SAIDA)
    rel = {}
    L = []
    m = maquina.construir()
    exporta_listas(m, rel)
    exporta_impressas(m, rel)
    exporta_chapas(m, rel)
    exporta_gabarito()
    exporta_visualizador(m, rel)
    with open(os.path.join(SAIDA, "lista_pecas.json"), "w", encoding="utf-8") as f:
        json.dump(rel, f, indent=1, ensure_ascii=False)
    L.append("impressas: %d tipos, %d pecas, %.0f g de filamento" % (
        len(rel["impressas"]), sum(l["qtd"] for l in rel["impressas"]),
        sum(l["qtd"] * l["massa_g"] for l in rel["impressas"])))
    for l in rel["impressas"]:
        L.append("  %-26s x%d  %5.1f x %5.1f x %5.1f  %5.1f g  apoio %5d  ponte %5d (maior %4d)  %s" % (
            l["peca"], l["qtd"], l["x"], l["y"], l["z"], l["massa_g"], l["apoio_mm2"], l["ponte_mm2"],
            l["maior_ponte_mm2"], "ok" if l["solido_ok"] else "MALHA ABERTA"))
    L.append("chapas de MDF:")
    for l in rel["chapas"]:
        L.append("  %-18s %6.1f x %6.1f  %3d contornos  %5.0f cm2" % (l["peca"], l["largura"], l["altura"],
                                                                       l["contornos"], l["area_cm2"]))
    L.append("pranchas: %s" % rel["pranchas"])
    L.append("visualizador: %s" % rel["visualizador"])
    L.append("pecas compradas / do estoque:")
    for l in rel["comprados"]:
        L.append("  %3d  %s" % (l["qtd"], l["peca"]))
    L.append("ferragens:")
    for l in rel["ferragens"]:
        L.append("  %3d  %s" % (l["qtd"], l["peca"]))
    return L


try:
    linhas = main()
except Exception:
    import traceback
    linhas = [traceback.format_exc()]
with open(os.path.join(SAIDA, "resumo_geracao.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(linhas) + "\n")
