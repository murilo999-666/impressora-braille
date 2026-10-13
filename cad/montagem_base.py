# -*- coding: utf-8 -*-
"""Registro da montagem: cada peca entra com nome, forma (ja na posicao da maquina),
tipo, cor e grupo de movimento. As ferragens sao contadas para a lista de compras."""
from collections import OrderedDict
from fc_util import *

# cores (r, g, b) 0..1
COR = {
    "mdf": (0.82, 0.64, 0.42),
    "mdf2": (0.76, 0.58, 0.37),
    "aco": (0.72, 0.74, 0.77),
    "aluminio": (0.85, 0.86, 0.88),
    "preto": (0.13, 0.13, 0.14),
    "correia": (0.08, 0.08, 0.08),
    "latao": (0.83, 0.69, 0.30),
    "cobre": (0.80, 0.45, 0.20),
    "pcb_azul": (0.10, 0.25, 0.60),
    "pcb_vermelha": (0.72, 0.10, 0.10),
    "pcb_roxa": (0.45, 0.20, 0.55),
    "impresso": (0.95, 0.50, 0.10),      # pecas impressas moveis (laranja)
    "impresso2": (0.16, 0.45, 0.75),     # pecas impressas fixas (azul)
    "impresso3": (0.30, 0.65, 0.35),     # guias e manipulo (verde)
    "borracha": (0.05, 0.05, 0.05),
    "papel": (0.97, 0.97, 0.93),
    "parafuso": (0.35, 0.36, 0.38),
    "verde": (0.15, 0.60, 0.25),
    "branco": (0.92, 0.92, 0.92),
}


class Montagem:
    def __init__(self):
        self.itens = []                 # dicts
        self.ferragens = OrderedDict()  # descricao -> quantidade
        self.com_ferragens = True       # desenhar parafusos e porcas

    def add(self, nome, forma, tipo, cor, grupo="fixo", peca=None, obs=""):
        """tipo: mdf | impresso | comprado | ferragem.  grupo: fixo | carro_sup |
        carro_inf | embolo | eixo_papel | eixo_vertical."""
        if isinstance(cor, str):
            cor = COR[cor]
        self.itens.append(dict(nome=nome, forma=forma, tipo=tipo, cor=cor, grupo=grupo,
                               peca=peca or nome, obs=obs))
        return forma

    def conta(self, descricao, n=1):
        self.ferragens[descricao] = self.ferragens.get(descricao, 0) + n

    # ------------------------------------------------------------ ferragens
    def parafuso(self, d, L, eixo, a, b, c, sentido=1, grupo="fixo", cabeca="allen", onde=""):
        """Parafuso metrico. (a, b) = posicao no plano perpendicular ao eixo; c = cota da
        face de apoio da cabeca; sentido = +1 se a rosca aponta para o lado positivo do eixo."""
        self.conta("Parafuso M%g x %g (%s)" % (d, L, cabeca))
        if not self.com_ferragens:
            return
        hk = {2: 2.0, 2.5: 2.5, 3: 3.0, 4: 4.0, 5: 5.0, 8: 5.3}.get(d, d)
        dk = {2: 3.8, 2.5: 4.5, 3: 5.5, 4: 7.0, 5: 8.5, 8: 13.0}.get(d, 1.8 * d)
        corpo = cyl(d * 0.92, eixo, a, b, c, c + sentido * L)
        cab = cyl(dk, eixo, a, b, c, c - sentido * hk)
        forma = corpo if cabeca == "sem cabeca" else uni(corpo, cab)
        n = sum(1 for i in self.itens if i["tipo"] == "ferragem")
        self.add("parafuso_%03d" % n, forma, "ferragem", "parafuso", grupo,
                 peca="Parafuso M%g x %g" % (d, L), obs=onde)

    def porca(self, d, eixo, a, b, c, sentido=1, grupo="fixo", tipo="sextavada"):
        """Porca: c = cota da face de apoio; ocupa de c ate c + sentido * altura."""
        self.conta("Porca M%g (%s)" % (d, tipo))
        if not self.com_ferragens:
            return
        m = {2: 1.6, 2.5: 2.0, 3: 2.4, 4: 3.2, 5: 4.0, 8: 6.5}.get(d, 0.8 * d)
        s = {2: 4.0, 2.5: 5.0, 3: 5.5, 4: 7.0, 5: 8.0, 8: 13.0}.get(d, 1.7 * d)
        if tipo == "travante":
            m += 1.5
        f = dif(hexagono(s, eixo, a, b, c, c + sentido * m), cyl(d, eixo, a, b, c - 10, c + 10))
        n = sum(1 for i in self.itens if i["tipo"] == "ferragem")
        self.add("porca_%03d" % n, f, "ferragem", "parafuso", grupo, peca="Porca M%g" % d)

    def arruela(self, d, eixo, a, b, c, sentido=1, grupo="fixo"):
        self.conta("Arruela lisa M%g" % d)
        if not self.com_ferragens:
            return
        de = {3: 7.0, 4: 9.0, 5: 10.0, 8: 16.0}.get(d, 2.2 * d)
        e = {3: 0.5, 4: 0.8, 5: 1.0, 8: 1.6}.get(d, 0.8)
        f = dif(cyl(de, eixo, a, b, c, c + sentido * e), cyl(d + 0.3, eixo, a, b, c - 5, c + 5))
        n = sum(1 for i in self.itens if i["tipo"] == "ferragem")
        self.add("arruela_%03d" % n, f, "ferragem", "parafuso", grupo, peca="Arruela M%g" % d)

    # ------------------------------------------------------------ consultas
    def por_tipo(self, tipo):
        return [i for i in self.itens if i["tipo"] == tipo]

    def pecas(self, tipo):
        """Agrupa por designacao: {peca: quantidade}."""
        r = OrderedDict()
        for i in self.por_tipo(tipo):
            if i["obs"] == "sub":       # pedaco de uma peca ja contada
                continue
            r[i["peca"]] = r.get(i["peca"], 0) + 1
        return r
