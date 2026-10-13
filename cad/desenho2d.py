# -*- coding: utf-8 -*-
"""Extrai o contorno 2D das chapas de MDF e escreve DXF (R12) e SVG em escala 1:1 (mm).
Cada contorno vira uma polilinha fechada com arcos de verdade; furos redondos viram circulos."""
import math
from fc_util import EIXOS


def contornos(forma):
    """Devolve (largura, altura, lista de contornos). Cada contorno e
    ('circulo', cx, cy, r) ou ('poli', [(x, y, bulge), ...])."""
    bb = forma.BoundBox
    dims = {"x": bb.XLength, "y": bb.YLength, "z": bb.ZLength}
    eixo = min(dims, key=dims.get)
    meio = {"x": bb.XMin + bb.XLength / 2, "y": bb.YMin + bb.YLength / 2, "z": bb.ZMin + bb.ZLength / 2}[eixo]
    wires = forma.slice(EIXOS[eixo], meio)
    if eixo == "x":
        f = lambda p: (p.y - bb.YMin, p.z - bb.ZMin)
        larg, alt = bb.YLength, bb.ZLength
    elif eixo == "y":
        f = lambda p: (p.x - bb.XMin, p.z - bb.ZMin)
        larg, alt = bb.XLength, bb.ZLength
    else:
        f = lambda p: (p.x - bb.XMin, p.y - bb.YMin)
        larg, alt = bb.XLength, bb.YLength
    out = []
    for w in wires:
        arestas = w.OrderedEdges
        if len(arestas) == 1 and type(arestas[0].Curve).__name__ == "Circle" and arestas[0].isClosed():
            c = f(arestas[0].Curve.Center)
            out.append(("circulo", c[0], c[1], arestas[0].Curve.Radius))
            continue
        segs = []
        for e in arestas:
            a, b = e.FirstParameter, e.LastParameter
            p0, p1, pm = f(e.valueAt(a)), f(e.valueAt(b)), f(e.valueAt((a + b) / 2))
            tipo = type(e.Curve).__name__
            if tipo == "Circle":
                c = f(e.Curve.Center)
                a0 = math.atan2(p0[1] - c[1], p0[0] - c[0])
                am = math.atan2(pm[1] - c[1], pm[0] - c[0])
                a1 = math.atan2(p1[1] - c[1], p1[0] - c[0])
                d_m = (am - a0) % (2 * math.pi)
                d_1 = (a1 - a0) % (2 * math.pi)
                if d_m < d_1:
                    ang = d_1                       # anti-horario
                else:
                    ang = d_1 - 2 * math.pi         # horario
                segs.append((p0, p1, math.tan(ang / 4.0)))
            elif tipo in ("Line", "LineSegment"):
                segs.append((p0, p1, 0.0))
            else:
                pts = [f(p) for p in e.discretize(Deflection=0.03)]
                for i in range(len(pts) - 1):
                    segs.append((pts[i], pts[i + 1], 0.0))
        # encadeia os segmentos na ordem (invertendo os que vierem ao contrario)
        cadeia = []
        atual = None
        for i, (p0, p1, b) in enumerate(segs):
            if atual is None:
                prox = segs[1] if len(segs) > 1 else None
                if prox and not (_perto(p1, prox[0]) or _perto(p1, prox[1])):
                    p0, p1, b = p1, p0, -b
            elif not _perto(atual, p0):
                p0, p1, b = p1, p0, -b
            cadeia.append((p0[0], p0[1], b))
            atual = p1
        out.append(("poli", cadeia))
    return larg, alt, out


def _perto(a, b, tol=1e-4):
    return abs(a[0] - b[0]) < tol and abs(a[1] - b[1]) < tol


def gira90(larg, alt, conts):
    """Gira o desenho 90 graus (para aproveitar melhor a chapa)."""
    out = []
    for c in conts:
        if c[0] == "circulo":
            out.append(("circulo", alt - c[2], c[1], c[3]))
        else:
            out.append(("poli", [(alt - y, x, b) for x, y, b in c[1]]))
    return alt, larg, out


def desloca(conts, dx, dy):
    out = []
    for c in conts:
        if c[0] == "circulo":
            out.append(("circulo", c[1] + dx, c[2] + dy, c[3]))
        else:
            out.append(("poli", [(x + dx, y + dy, b) for x, y, b in c[1]]))
    return out


# ------------------------------------------------------------------ DXF
def escreve_dxf(caminho, conts, textos=()):
    L = []
    w = L.append
    w("0\nSECTION\n2\nHEADER\n9\n$ACADVER\n1\nAC1009\n9\n$INSUNITS\n70\n4\n0\nENDSEC")
    w("0\nSECTION\n2\nTABLES\n0\nTABLE\n2\nLAYER\n70\n2")
    w("0\nLAYER\n2\nCORTE\n70\n0\n62\n1\n6\nCONTINUOUS")
    w("0\nLAYER\n2\nGRAVAR\n70\n0\n62\n5\n6\nCONTINUOUS")
    w("0\nENDTAB\n0\nENDSEC\n0\nSECTION\n2\nENTITIES")
    for c in conts:
        if c[0] == "circulo":
            w("0\nCIRCLE\n8\nCORTE\n10\n%.4f\n20\n%.4f\n30\n0.0\n40\n%.4f" % (c[1], c[2], c[3]))
        else:
            w("0\nPOLYLINE\n8\nCORTE\n66\n1\n70\n1\n10\n0.0\n20\n0.0\n30\n0.0")
            for x, y, b in c[1]:
                s = "0\nVERTEX\n8\nCORTE\n10\n%.4f\n20\n%.4f\n30\n0.0" % (x, y)
                if abs(b) > 1e-9:
                    s += "\n42\n%.6f" % b
                w(s)
            w("0\nSEQEND\n8\nCORTE")
    for x, y, h, txt in textos:
        w("0\nTEXT\n8\nGRAVAR\n10\n%.3f\n20\n%.3f\n30\n0.0\n40\n%.2f\n1\n%s" % (x, y, h, txt))
    w("0\nENDSEC\n0\nEOF")
    with open(caminho, "w", encoding="ascii", errors="replace", newline="\r\n") as f:
        f.write("\n".join(L) + "\n")


# ------------------------------------------------------------------ SVG
def escreve_svg(caminho, larg, alt, conts, textos=(), moldura=False):
    """SVG em mm reais. Corte = traco vermelho fino; gravacao (nomes) = azul."""
    L = ['<?xml version="1.0" encoding="UTF-8"?>',
         '<svg xmlns="http://www.w3.org/2000/svg" width="%.2fmm" height="%.2fmm" viewBox="0 0 %.2f %.2f">' % (
             larg, alt, larg, alt)]
    if moldura:
        L.append('<rect x="0" y="0" width="%.2f" height="%.2f" fill="none" stroke="#00aa00" stroke-width="0.3"/>' % (larg, alt))
    L.append('<g fill="none" stroke="#ff0000" stroke-width="0.1">')
    for c in conts:
        if c[0] == "circulo":
            L.append('<circle cx="%.3f" cy="%.3f" r="%.3f"/>' % (c[1], alt - c[2], c[3]))
        else:
            v = c[1]
            d = ["M %.3f %.3f" % (v[0][0], alt - v[0][1])]
            n = len(v)
            for i in range(n):
                x0, y0, b = v[i]
                x1, y1, _ = v[(i + 1) % n]
                if abs(b) < 1e-9:
                    d.append("L %.3f %.3f" % (x1, alt - y1))
                else:
                    corda = math.hypot(x1 - x0, y1 - y0)
                    ang = 4 * math.atan(abs(b))
                    r = corda / (2 * math.sin(ang / 2))
                    grande = 1 if ang > math.pi else 0
                    sentido = 0 if b > 0 else 1          # y invertido no SVG
                    d.append("A %.3f %.3f 0 %d %d %.3f %.3f" % (r, r, grande, sentido, x1, alt - y1))
            L.append('<path d="%s Z"/>' % " ".join(d))
    L.append("</g>")
    if textos:
        L.append('<g fill="#0000ff" stroke="none" font-family="Arial, sans-serif">')
        for x, y, h, txt in textos:
            L.append('<text x="%.2f" y="%.2f" font-size="%.2f">%s</text>' % (x, alt - y, h * 1.35, txt))
        L.append("</g>")
    L.append("</svg>")
    with open(caminho, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")


# ------------------------------------------------------------------ encaixe nas chapas
def encaixa(pecas, larg_chapa, alt_chapa, margem=5.0, vao=4.0):
    """Distribui pecas (nome, larg, alt) em chapas por prateleiras, girando quando ajuda.
    Devolve lista de chapas; cada chapa = [(nome, x, y, girada)]."""
    resto = sorted(pecas, key=lambda p: -max(p[1], p[2]))
    chapas = []
    while resto:
        chapa = []
        y = margem
        while resto:
            # escolhe a altura da prateleira pela maior peca que ainda cabe
            cabe = []
            for p in resto:
                for gir in (False, True):
                    w, h = (p[2], p[1]) if gir else (p[1], p[2])
                    if w <= larg_chapa - 2 * margem and y + h <= alt_chapa - margem:
                        cabe.append((h, w, p, gir))
            if not cabe:
                break
            cabe.sort(key=lambda t: (-t[0], -t[1]))
            h_prat = cabe[0][0]
            x = margem
            colocou = True
            while colocou:
                colocou = False
                melhor = None
                for p in resto:
                    for gir in (False, True):
                        w, h = (p[2], p[1]) if gir else (p[1], p[2])
                        if h <= h_prat + 1e-6 and x + w <= larg_chapa - margem + 1e-6:
                            if melhor is None or w * h > melhor[0]:
                                melhor = (w * h, p, gir, w, h)
                if melhor:
                    _, p, gir, w, h = melhor
                    chapa.append((p[0], x, y, gir))
                    x += w + vao
                    resto.remove(p)
                    colocou = True
            y += h_prat + vao
        if not chapa:
            raise ValueError("peca maior que a chapa: %s" % resto[0][0])
        chapas.append(chapa)
    return chapas
