# -*- coding: utf-8 -*-
"""Cenas para render.py: cada funcao devolve uma lista de cenas
{nome, itens:[{nome, forma, cor}], vistas:[(nome, direcao)]}."""
import parametros as P
from montagem_base import COR
from fc_util import *

ISO1 = (-1.0, 1.0, -0.8)     # de frente-esquerda, olhando para tras
ISO2 = (1.0, 1.0, -0.8)
ISO3 = (-1.0, -1.0, -0.7)    # por tras
ISO4 = (1.0, -1.0, -0.7)
BAIXO = (0.6, 0.8, 1.0)


def _it(nome, forma, cor, **k):
    d = dict(nome=nome, forma=forma, cor=COR[cor] if isinstance(cor, str) else cor)
    d.update(k)
    return d


def carros():
    import impressas as I
    xc = P.X_CARRO_REF
    itens = [_it("carro_puncao", I.carro_puncao(xc), "impresso"),
             _it("carro_matriz", I.carro_matriz(xc), "impresso2")]
    return [dict(nome="t_carros", itens=itens,
                 vistas=[("iso1", ISO1), ("iso4", ISO4), ("frente", "viewFront"), ("lado", "viewRight"),
                         ("baixo", BAIXO)])]


def _montagem(filtro=None, xc=None, ferragens=True):
    import maquina
    m = maquina.construir(xc, ferragens)
    itens = []
    for it in m.itens:
        if filtro and not filtro(it):
            continue
        itens.append(dict(nome=it["nome"], forma=it["forma"], cor=it["cor"]))
    return itens


def tudo():
    cenas = [dict(nome="geral", itens=_montagem(), vistas=[("iso1", ISO1), ("iso2", ISO2), ("iso3", ISO3),
                                                         ("cima", "viewTop"), ("frente", "viewFront")])]
    sem = ("parede_frontal", "lateral_direita")
    cenas.append(dict(nome="aberto", itens=_montagem(lambda i: i["nome"] not in sem),
                      vistas=[("iso2", ISO2), ("frente", "viewFront"), ("dir", "viewRight")]))
    return cenas


def interno():
    """So o mecanismo (sem chapas externas)."""
    fora = ("parede_frontal", "parede_traseira", "lateral_direita", "lateral_esquerda", "base", "papel_a4")
    return [dict(nome="mecanismo", itens=_montagem(lambda i: i["nome"] not in fora),
                 vistas=[("iso1", ISO1), ("iso2", ISO2), ("iso3", ISO3), ("cima", "viewTop"), ("frente", "viewFront"),
                         ("esq", "viewLeft"), ("dir", "viewRight")])]


PASTAS = {"mdf": "Chapas_MDF", "impresso": "Pecas_impressas", "comprado": "Pecas_do_estoque", "ferragem": "Parafusos_e_porcas"}


def final():
    """Modelo completo: salva cad/impressora_braille.FCStd, o STEP da montagem e as imagens da documentacao."""
    import os
    import maquina
    aqui = os.path.dirname(os.path.abspath(__file__))
    m = maquina.construir()
    itens = [dict(nome=i["nome"], forma=i["forma"], cor=i["cor"], pasta=PASTAS[i["tipo"]]) for i in m.itens]
    cenas = [dict(nome="montagem", itens=itens, larg=1800, alt=1300,
                  vistas=[("frente_esq", ISO1), ("frente_dir", ISO2), ("tras", ISO3), ("cima", "viewTop"), ("frente", "viewFront")],
                  fcstd=os.path.join(aqui, "impressora_braille.FCStd"),
                  step=os.path.join(aqui, "saida", "step", "montagem_completa.step"))]
    sem = ("parede_frontal", "lateral_direita", "trava_eixos_sup_dir", "trava_eixos_inf_dir", "mancal_eixo_papel_dir",
           "rolamento_608_papel_dir", "manipulo", "papel_a4")
    dentro = [i for i in itens if i["nome"] not in sem and not (i["pasta"] == PASTAS["ferragem"])]
    cenas.append(dict(nome="aberta", itens=dentro, larg=1800, alt=1300,
                      vistas=[("frente_dir", ISO2), ("frente", "viewFront"), ("lado_direito", "viewRight"), ("cima", "viewTop")]))
    fora = ("parede_frontal", "parede_traseira", "lateral_direita", "lateral_esquerda", "base", "papel_a4",
            "mesa_traseira", "mesa_frontal")
    mec = [i for i in itens if i["nome"] not in fora and i["pasta"] != PASTAS["ferragem"]]
    cenas.append(dict(nome="mecanismo", itens=mec, larg=1800, alt=1300,
                      vistas=[("frente_esq", ISO1), ("frente_dir", ISO2), ("tras", ISO3), ("frente", "viewFront"),
                              ("lado_esquerdo", "viewLeft"), ("cima", "viewTop")]))
    carro = [i for i in m.itens if i["grupo"] in ("carro_sup", "carro_inf", "embolo")]
    carro = [dict(nome=i["nome"], forma=i["forma"], cor=i["cor"]) for i in carro]
    cenas.append(dict(nome="carros", itens=carro, larg=1500, alt=1300,
                      vistas=[("iso", ISO2), ("frente", "viewFront"), ("lado", "viewRight")]))
    return cenas
