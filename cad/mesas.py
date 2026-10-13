# -*- coding: utf-8 -*-
"""Arruma TODAS as pecas impressas em mesas de 250 x 250 mm, na quantidade certa e ja deitadas.
Roda no FreeCAD em modo console:   freecadcmd mesas.py     (ou ./rodar.sh mesas)

Saidas em cad/saida/mesas_250x250/:
  mesa_N.3mf   projeto com cada peca como um objeto separado (abra no Bambu Studio, Orca, Prusa, Cura)
  mesa_N.stl   as mesmas pecas fundidas num arquivo so (para fatiadores que nao abrem 3MF)
  mesa_N.png   mapa da mesa, com o nome de cada peca
Antes, rode ./rodar.sh gerar: este script le os STL de cad/saida/stl e a lista de pecas.
"""
import io
import json
import os
import sys
import zipfile

AQUI = os.path.dirname(os.path.abspath(__file__))
if AQUI not in sys.path:
    sys.path.insert(0, AQUI)

import FreeCAD as App
import Mesh
import desenho2d as D

MESA = 250.0        # lado da mesa (mm)
BORDA = 8.0         # faixa livre na beirada
VAO = 6.0           # distancia entre pecas
SAIDA = os.path.join(AQUI, "saida", "mesas_250x250")
STL = os.path.join(AQUI, "saida", "stl")

# pecas que trabalham sob carga: ficam juntas na mesa 1, para quem quiser imprimir em PETG
CARGA = ("carro_puncao", "carro_matriz", "pressor_braco", "esticador", "rolete", "torre_motor_x", "mancal_superior",
         "mancal_eixo_papel", "espacador_bucha_curto", "espacador_bucha_longo", "bucha_608", "calco_solenoide", "anel_encosto")


class MesaLivre:
    """Encaixe por retangulos livres (MaxRects): aproveita melhor a mesa que o encaixe em prateleiras."""

    def __init__(self, lado):
        self.livres = [(0.0, 0.0, lado, lado)]
        self.itens = []          # (nome, x, y, girada)

    def melhor(self, w, h):
        m = None
        for fx, fy, fw, fh in self.livres:
            for gir, (a, b) in ((False, (w, h)), (True, (h, w))):
                if a <= fw + 1e-6 and b <= fh + 1e-6:
                    cand = (min(fw - a, fh - b), fy, fx, gir, a, b)
                    if m is None or cand < m:
                        m = cand
        return m

    def poe(self, nome, w, h):
        m = self.melhor(w, h)
        if m is None:
            return False
        _, y, x, gir, a, b = m
        self.itens.append((nome, x, y, gir))
        novas = []
        for fx, fy, fw, fh in self.livres:
            if x >= fx + fw - 1e-6 or x + a <= fx + 1e-6 or y >= fy + fh - 1e-6 or y + b <= fy + 1e-6:
                novas.append((fx, fy, fw, fh))
                continue
            if x > fx + 1e-6:
                novas.append((fx, fy, x - fx, fh))
            if x + a < fx + fw - 1e-6:
                novas.append((x + a, fy, fx + fw - (x + a), fh))
            if y > fy + 1e-6:
                novas.append((fx, fy, fw, y - fy))
            if y + b < fy + fh - 1e-6:
                novas.append((fx, y + b, fw, fy + fh - (y + b)))
        self.livres = [r for i, r in enumerate(novas) if not any(
            j != i and o[0] <= r[0] + 1e-6 and o[1] <= r[1] + 1e-6 and o[0] + o[2] >= r[0] + r[2] - 1e-6 and
            o[1] + o[3] >= r[1] + r[3] - 1e-6 and (o != r or j < i) for j, o in enumerate(novas))]
        return True


def modelo_3mf(objetos, itens):
    """objetos = {id: (nome, pontos, faces)}; itens = [(id, matriz 3x4 em texto)]"""
    x = ['<?xml version="1.0" encoding="UTF-8"?>',
         '<model unit="millimeter" xml:lang="pt-BR" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">',
         ' <metadata name="Title">Impressora braille - pecas impressas</metadata>',
         ' <metadata name="Application">cad/mesas.py</metadata>', ' <resources>']
    for oid, (nome, pts, faces) in objetos.items():
        x.append('  <object id="%d" type="model" name="%s"><mesh><vertices>' % (oid, nome))
        x.append("".join('<vertex x="%.4f" y="%.4f" z="%.4f"/>' % (p.x, p.y, p.z) for p in pts))
        x.append("</vertices><triangles>")
        x.append("".join('<triangle v1="%d" v2="%d" v3="%d"/>' % f for f in faces))
        x.append("</triangles></mesh></object>")
    x.append(" </resources>\n <build>")
    for oid, mat in itens:
        x.append('  <item objectid="%d" transform="%s"/>' % (oid, mat))
    x.append(" </build>\n</model>")
    return "\n".join(x)


def escreve_3mf(caminho, objetos, itens):
    tipos = ('<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
             '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
             '<Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
    rels = ('<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
    with zipfile.ZipFile(caminho, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", tipos)
        z.writestr("_rels/.rels", rels)
        z.writestr("3D/3dmodel.model", modelo_3mf(objetos, itens))


def mapa(caminho, n, total, colocadas):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    fig, ax = plt.subplots(figsize=(7.5, 7.9), dpi=110)
    ax.set_xlim(-4, MESA + 4)
    ax.set_ylim(-4, MESA + 4)
    ax.set_aspect("equal")
    ax.add_patch(Rectangle((0, 0), MESA, MESA, fc="#f5f2ea", ec="#37474f", lw=1.6))
    for nome, x, y, w, h in colocadas:
        carga = nome.split(" ")[0] in CARGA
        ax.add_patch(Rectangle((x, y), w, h, fc="#f2a35e" if carga else "#7fb0e0", ec="#263238", lw=0.9))
        rot = 90 if h > w * 1.3 else 0
        tam = 6.6 if min(w, h) > 18 else 5.2
        ax.text(x + w / 2, y + h / 2, nome.replace("_", " "), ha="center", va="center", fontsize=tam, rotation=rot, color="#10151a")
    ax.set_title("Mesa %d de %d  (250 x 250 mm, vista de cima)" % (n, total), fontsize=12)
    ax.set_xlabel("laranja: pecas que trabalham sob carga (PETG, se tiver)   azul: suportes (PLA)", fontsize=8.5)
    ax.set_xticks([0, 50, 100, 150, 200, 250])
    ax.set_yticks([0, 50, 100, 150, 200, 250])
    ax.tick_params(labelsize=8)
    fig.savefig(caminho, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def main():
    os.makedirs(SAIDA, exist_ok=True)
    for f in os.listdir(SAIDA):
        os.remove(os.path.join(SAIDA, f))
    rel = json.load(io.open(os.path.join(AQUI, "saida", "lista_pecas.json"), encoding="utf-8"))
    malhas, copias = {}, []
    for l in rel["impressas"]:
        m = Mesh.Mesh(os.path.join(STL, l["peca"] + ".stl"))
        bb = m.BoundBox
        malhas[l["peca"]] = (m, bb.XLength, bb.YLength, bb.XMin, bb.YMin, bb.ZMin)
        for k in range(l["qtd"]):
            copias.append((l["peca"], k + 1, l["qtd"]))
    util = MESA - 2 * BORDA

    def chave(c):
        return "%s %d" % (c[0], c[1]) if c[2] > 1 else c[0]

    # as pecas entram ja "engordadas" pelo vao, numa mesa engordada do mesmo tanto: sobra sempre VAO entre elas
    livres = []
    grupos = [[c for c in copias if c[0] in CARGA], [c for c in copias if c[0] not in CARGA]]
    for gi, g in enumerate(grupos):
        g = sorted(g, key=lambda c: -max(malhas[c[0]][1], malhas[c[0]][2]))
        inicio = 0
        if gi:                                     # os suportes comecam numa mesa nova...
            livres.append(MesaLivre(util + VAO))
            inicio = len(livres) - 1
        for c in g:
            w, h = malhas[c[0]][1] + VAO, malhas[c[0]][2] + VAO
            ordem = list(range(inicio, len(livres))) + list(range(0, inicio))    # ...e so voltam para as primeiras se faltar lugar
            if not any(livres[k].poe(chave(c), w, h) for k in ordem):
                livres.append(MesaLivre(util + VAO))
                if not livres[-1].poe(chave(c), w, h):
                    raise ValueError("peca maior que a mesa: " + c[0])
    mesas = [m.itens for m in livres]
    linhas = []
    for n, chapa in enumerate(mesas, 1):
        objetos, itens, colocadas, ids = {}, [], [], {}
        junta = Mesh.Mesh()
        for nome, x, y, gir in chapa:
            peca = nome.split(" ")[0]
            m, w, h, x0, y0, z0 = malhas[peca]
            if peca not in ids:
                ids[peca] = len(ids) + 1
                pts, faces = m.Topology
                objetos[ids[peca]] = (peca, pts, faces)
            px, py = x + BORDA, y + BORDA
            if gir:      # giro de 90 graus em Z: (x, y) -> (-y, x)
                mat = "0 1 0 -1 0 0 0 0 1 %.4f %.4f %.4f" % (px + (y0 + h), py - x0, -z0)
                w2, h2 = h, w
                c = m.copy()
                c.rotate(0, 0, 1.5707963267948966)
                c.translate(px + (y0 + h), py - x0, -z0)
            else:
                mat = "1 0 0 0 1 0 0 0 1 %.4f %.4f %.4f" % (px - x0, py - y0, -z0)
                w2, h2 = w, h
                c = m.copy()
                c.translate(px - x0, py - y0, -z0)
            bb = c.BoundBox
            if bb.XMin < BORDA - 0.2 or bb.YMin < BORDA - 0.2 or bb.XMax > MESA - BORDA + 0.2 or bb.YMax > MESA - BORDA + 0.2 or abs(bb.ZMin) > 0.05:
                raise ValueError("peca fora da mesa: %s (%.1f..%.1f, %.1f..%.1f, z %.2f)" % (nome, bb.XMin, bb.XMax, bb.YMin, bb.YMax, bb.ZMin))
            junta.addMesh(c)
            itens.append((ids[peca], mat))
            colocadas.append((nome, px, py, w2, h2))
        # nenhuma peca pode encostar na outra
        for i in range(len(colocadas)):
            for j in range(i + 1, len(colocadas)):
                a, b = colocadas[i], colocadas[j]
                if a[1] < b[1] + b[3] + VAO - 0.2 and b[1] < a[1] + a[3] + VAO - 0.2 and a[2] < b[2] + b[4] + VAO - 0.2 and b[2] < a[2] + a[4] + VAO - 0.2:
                    raise ValueError("pecas muito perto: %s e %s" % (a[0], b[0]))
        base = os.path.join(SAIDA, "mesa_%d" % n)
        junta.write(base + ".stl")
        escreve_3mf(base + ".3mf", objetos, itens)
        mapa(base + ".png", n, len(mesas), colocadas)
        alt = max(malhas[c[0].split(" ")[0]][0].BoundBox.ZLength for c in colocadas)
        massa = sum(l["massa_g"] for c in colocadas for l in rel["impressas"] if l["peca"] == c[0].split(" ")[0])
        linhas.append("mesa %d: %d pecas, altura maxima %.0f mm, cerca de %.0f g  -> %s" % (
            n, len(colocadas), alt, massa, ", ".join(sorted(set(c[0].split(" ")[0] for c in colocadas)))))
    linhas.append("total: %d pecas em %d mesas" % (sum(len(c) for c in mesas), len(mesas)))
    if sum(len(c) for c in mesas) != len(copias):
        linhas.append("ERRO: faltou peca")
    return linhas


try:
    L = main()
except Exception:
    import traceback
    L = [traceback.format_exc()]
with open(os.path.join(SAIDA if os.path.isdir(SAIDA) else AQUI, "resumo_mesas.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(L) + "\n")
