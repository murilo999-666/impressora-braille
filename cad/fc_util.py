# -*- coding: utf-8 -*-
"""Funcoes auxiliares de modelagem (FreeCAD Part) usadas por todo o gerador."""
import math
import FreeCAD as App
import Part

V = App.Vector
EIXOS = {"x": V(1, 0, 0), "y": V(0, 1, 0), "z": V(0, 0, 1)}


def box(x0, x1, y0, y1, z0, z1):
    """Paralelepipedo pelos limites (aceita limites invertidos)."""
    x0, x1 = min(x0, x1), max(x0, x1)
    y0, y1 = min(y0, y1), max(y0, y1)
    z0, z1 = min(z0, z1), max(z0, z1)
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def cylz(d, x, y, z0, z1):
    return Part.makeCylinder(d / 2.0, abs(z1 - z0), V(x, y, min(z0, z1)), EIXOS["z"])


def cylx(d, y, z, x0, x1):
    return Part.makeCylinder(d / 2.0, abs(x1 - x0), V(min(x0, x1), y, z), EIXOS["x"])


def cyly(d, x, z, y0, y1):
    return Part.makeCylinder(d / 2.0, abs(y1 - y0), V(x, min(y0, y1), z), EIXOS["y"])


def cyl(d, eixo, a, b, c0, c1):
    """Cilindro ao longo de 'eixo'; (a, b) sao as outras duas coordenadas em ordem xyz."""
    if eixo == "x":
        return cylx(d, a, b, c0, c1)
    if eixo == "y":
        return cyly(d, a, b, c0, c1)
    return cylz(d, a, b, c0, c1)


def limpa(s):
    try:
        return s.removeSplitter()
    except Exception:
        return s


def uni(*formas):
    formas = [f for f in _achata(formas) if f is not None]
    r = formas[0]
    if len(formas) > 1:
        r = r.multiFuse(formas[1:])
    return limpa(r)


def dif(a, *b):
    b = [f for f in _achata(b) if f is not None]
    if not b:
        return a
    ferr = b[0] if len(b) == 1 else b[0].multiFuse(b[1:])
    return limpa(a.cut(ferr))


def _achata(seq):
    out = []
    for s in seq:
        if isinstance(s, (list, tuple)):
            out.extend(_achata(s))
        else:
            out.append(s)
    return out


def _pt(eixo, a, b, c):
    """Converte (a, b) do plano perpendicular a 'eixo' + cota c em vetor xyz."""
    if eixo == "x":
        return V(c, a, b)
    if eixo == "y":
        return V(a, c, b)
    return V(a, b, c)


def prisma(pontos, eixo, c0, c1):
    """Extrusao de um poligono fechado. pontos = [(a, b), ...] no plano perpendicular
    a 'eixo' (x -> (y, z); y -> (x, z); z -> (x, y)), entre as cotas c0 e c1."""
    c0, c1 = min(c0, c1), max(c0, c1)
    vs = [_pt(eixo, a, b, c0) for a, b in pontos]
    vs.append(vs[0])
    face = Part.Face(Part.makePolygon(vs))
    return face.extrude(EIXOS[eixo] * (c1 - c0))


def oblongo(larg, comp, eixo, a, b, c0, c1, ao_longo="a"):
    """Furo oblongo (rasgo) de largura 'larg' e comprimento total 'comp' centrado em (a, b).
    ao_longo = 'a' ou 'b' indica em qual das duas coordenadas do plano ele se alonga."""
    meio = max(comp - larg, 0.0) / 2.0
    if ao_longo == "a":
        r = box_plano(eixo, a - meio, a + meio, b - larg / 2.0, b + larg / 2.0, c0, c1)
        p1, p2 = (a - meio, b), (a + meio, b)
    else:
        r = box_plano(eixo, a - larg / 2.0, a + larg / 2.0, b - meio, b + meio, c0, c1)
        p1, p2 = (a, b - meio), (a, b + meio)
    if meio <= 0:
        return cyl(larg, eixo, a, b, c0, c1)
    return uni(r, cyl(larg, eixo, p1[0], p1[1], c0, c1), cyl(larg, eixo, p2[0], p2[1], c0, c1))


def box_plano(eixo, a0, a1, b0, b1, c0, c1):
    """Caixa definida no plano perpendicular a 'eixo'."""
    if eixo == "x":
        return box(c0, c1, a0, a1, b0, b1)
    if eixo == "y":
        return box(a0, a1, c0, c1, b0, b1)
    return box(a0, a1, b0, b1, c0, c1)


def ret_arred(eixo, a0, a1, b0, b1, c0, c1, r):
    """Retangulo de cantos arredondados extrudado ao longo de 'eixo'."""
    a0, a1 = min(a0, a1), max(a0, a1)
    b0, b1 = min(b0, b1), max(b0, b1)
    r = min(r, (a1 - a0) / 2.0 - 1e-6, (b1 - b0) / 2.0 - 1e-6)
    if r <= 0.01:
        return box_plano(eixo, a0, a1, b0, b1, c0, c1)
    partes = [box_plano(eixo, a0 + r, a1 - r, b0, b1, c0, c1),
              box_plano(eixo, a0, a1, b0 + r, b1 - r, c0, c1)]
    for a in (a0 + r, a1 - r):
        for b in (b0 + r, b1 - r):
            partes.append(cyl(2 * r, eixo, a, b, c0, c1))
    return uni(*partes)


def hexagono(chave, eixo, a, b, c0, c1, giro=0.0):
    """Prisma hexagonal (sextavado) com abertura de chave 'chave'."""
    R = chave / 2.0 / math.cos(math.pi / 6)
    pts = [(a + R * math.cos(giro + i * math.pi / 3), b + R * math.sin(giro + i * math.pi / 3))
           for i in range(6)]
    return prisma(pts, eixo, c0, c1)


def move(s, dx=0.0, dy=0.0, dz=0.0):
    r = s.copy()
    r.translate(V(dx, dy, dz))
    return r


def gira(s, eixo, graus, centro=(0, 0, 0)):
    r = s.copy()
    r.rotate(V(*centro), EIXOS[eixo], graus)
    return r


def bbox(s):
    b = s.BoundBox
    return (b.XMin, b.XMax, b.YMin, b.YMax, b.ZMin, b.ZMax)


def volume_comum(a, b):
    """Volume da intersecao de dois solidos (0 se as caixas envolventes nao se tocam)."""
    if not a.BoundBox.intersect(b.BoundBox):
        return 0.0
    try:
        c = a.common(b)
        return c.Volume if not c.isNull() else 0.0
    except Exception:
        return -1.0
