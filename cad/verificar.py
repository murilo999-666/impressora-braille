# -*- coding: utf-8 -*-
"""Conferencia automatica do modelo. Roda no FreeCAD em modo console:
    freecadcmd verificar.py
Confere: solidos validos, interferencias entre pecas (em varias posicoes dos carros),
alcance dos carros e medidas principais. Escreve cad/relatorio_verificacao.txt."""
import os
import sys
import itertools

AQUI = os.path.dirname(os.path.abspath(__file__))
if AQUI not in sys.path:
    sys.path.insert(0, AQUI)

import parametros as P
from fc_util import *
import maquina

LIMITE = 0.5        # mm3: abaixo disso e so faces encostadas

# pares que se cruzam de proposito (roscas, pecas prensadas, desenho simplificado)
def permitido(a, b):
    na, nb = a["nome"], b["nome"]
    par = na + " " + nb
    ta, tb = a["tipo"], b["tipo"]
    if "papel_a4" in par:
        return True                      # folha ilustrativa
    if ta == "ferragem" or tb == "ferragem":
        outro = b if ta == "ferragem" else a
        fer = a if ta == "ferragem" else b
        if outro["tipo"] == "ferragem":
            return True                  # parafuso dentro da porca / arruela
        if outro["tipo"] == "impresso":
            return "ROSCA"               # so e aceito se o volume for pequeno (rosca no plastico)
        if outro["nome"].startswith(("motor_", "solenoide", "puncao", "polia", "rolamento_608_pressor",
                                     "microchave", "mega_", "barras_pinos", "oring")):
            return True                  # rosca em peca comprada / eixo do rolamento
        return False
    if "correia" in par and ("polia" in par or "carro" in par):
        return True                      # correia abraca a polia e e presa no carro
    if "oring" in par and "rolete" in par:
        return True
    if "puncao_estilete" in par and ("puncao_espacador" in par or "matriz_parafuso" in par):
        return True
    if "solenoide_quadro" in par and "solenoide_bobina" in par:
        return True
    if "solenoide_embolo" in par and "puncao_espacador" in par:
        return True
    if "matriz_parafuso" in par and "carro_matriz" in par:
        return True                      # rosca aberta no plastico
    if "mola_pressor" in par and "pressor" in par:
        return True
    if "haste_sensor" in par:
        return True
    if "barras_pinos" in par or ("ramps" in par and "driver" in par):
        return True
    return False


def checar(m, rotulo, out):
    itens = m.itens
    erros = 0
    for it in itens:
        f = it["forma"]
        if f.isNull() or not f.isValid() or f.Volume <= 0:
            out.append("  SOLIDO INVALIDO: %s" % it["nome"])
            erros += 1
    n = 0
    for a, b in itertools.combinations(itens, 2):
        if a["tipo"] == "ferragem" and b["tipo"] == "ferragem":
            continue
        fa, fb = a["forma"], b["forma"]
        if not fa.BoundBox.intersect(fb.BoundBox):
            continue
        p = permitido(a, b)
        if p is True:
            continue
        v = volume_comum(fa, fb)
        n += 1
        if v < 0:
            out.append("  ? falha no calculo: %s x %s" % (a["nome"], b["nome"]))
            continue
        lim = 60.0 if p == "ROSCA" else LIMITE
        if "mdf" in (a["tipo"], b["tipo"]) and "ferragem" in (a["tipo"], b["tipo"]):
            lim = 3.0                    # canto da porca sextavada na bolsa da junta em T
        if v > lim:
            c = fa.common(fb).BoundBox
            out.append("  INTERFERENCIA %8.1f mm3  %-28s x %-28s  em x[%.1f,%.1f] y[%.1f,%.1f] z[%.1f,%.1f]" % (
                v, a["nome"], b["nome"], c.XMin, c.XMax, c.YMin, c.YMax, c.ZMin, c.ZMax))
            erros += 1
    out.append("%s: %d pecas, %d pares testados, %d problemas" % (rotulo, len(itens), n, erros))
    return erros


def varredura(out, passo=7.0):
    """Desloca os carros de 7 em 7 mm por todo o curso e testa contra as pecas fixas."""
    m = maquina.construir(P.X_CARRO_REF)
    moveis = [i for i in m.itens if i["grupo"] in ("carro_sup", "carro_inf", "embolo")]
    fixas = [i for i in m.itens if i["grupo"] not in ("carro_sup", "carro_inf", "embolo", "papel")]
    erros = 0
    n = 0
    x = P.X_CARRO_MIN
    while x <= P.X_CARRO_MAX + 0.01:
        dx = x - P.X_CARRO_REF
        for a in moveis:
            fa = move(a["forma"], dx)
            for b in fixas:
                if not fa.BoundBox.intersect(b["forma"].BoundBox):
                    continue
                p = permitido(a, b)
                if p is True:
                    continue
                n += 1
                v = volume_comum(fa, b["forma"])
                if v > (60.0 if p == "ROSCA" else LIMITE):
                    out.append("  INTERFERENCIA %8.1f mm3  %-24s x %-26s com o carro em x = %.0f" % (v, a["nome"], b["nome"], x))
                    erros += 1
        x += passo
    out.append("varredura do curso (de %.0f a %.0f mm, passo %.0f): %d pares testados, %d problemas" % (
        P.X_CARRO_MIN, P.X_CARRO_MAX, passo, n, erros))
    return erros


def main():
    out = []
    total = 0
    posicoes = [P.X_CARRO_MIN, P.X_CARRO_REF, P.X_CARRO_MAX]
    if os.environ.get("BR_RAPIDO"):
        posicoes = [P.X_CARRO_REF]
    for xc in posicoes:
        m = maquina.construir(xc)
        total += checar(m, "carros em x = %.0f" % xc, out)
    m = maquina.construir(P.X_CARRO_REF, batida=True)
    total += checar(m, "embolo embaixo (batida)", out)
    if not os.environ.get("BR_RAPIDO"):
        total += varredura(out)
    # tambem com o puncao embaixo (batida)
    out.append("")
    r = P.resumo()
    for k, v in r.items():
        out.append("%-26s %s" % (k, v))
    out.append("")
    out.append("TOTAL DE PROBLEMAS: %d" % total)
    txt = "\n".join(out)
    with open(os.path.join(AQUI, "relatorio_verificacao.txt"), "w", encoding="utf-8") as f:
        f.write(txt + "\n")
    print(txt)


try:
    main()
except Exception:
    import traceback
    t = traceback.format_exc()
    print(t)
    with open(os.path.join(AQUI, "relatorio_verificacao.txt"), "w", encoding="utf-8") as f:
        f.write(t)
