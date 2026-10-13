# -*- coding: utf-8 -*-
"""Roda DENTRO do FreeCAD com interface (freecad.exe render.py).
Monta um conjunto, aplica as cores, salva imagens e (opcionalmente) o .FCStd.

Variaveis de ambiente:
  BR_ALVO   = nome de uma funcao de vistas.py (padrao: 'tudo')
  BR_SAIDA  = pasta das imagens
  BR_FCSTD  = caminho do .FCStd a salvar (opcional)
"""
import os
import sys
import traceback

AQUI = os.path.dirname(os.path.abspath(__file__))
if AQUI not in sys.path:
    sys.path.insert(0, AQUI)
SAIDA = os.environ.get("BR_SAIDA", os.path.join(AQUI, "..", "imagens"))
os.makedirs(SAIDA, exist_ok=True)
LOG = open(os.path.join(SAIDA, "render.log"), "w", encoding="utf-8")


def P(*a):
    LOG.write(" ".join(str(x) for x in a) + "\n")
    LOG.flush()


def main():
    import FreeCAD as App
    import FreeCADGui as Gui
    import vistas
    alvo = os.environ.get("BR_ALVO", "tudo")
    P("alvo:", alvo)
    cenas = getattr(vistas, alvo)()
    for cena in cenas:
        doc = App.newDocument(cena["nome"])
        pastas = {}
        for it in cena["itens"]:
            o = doc.addObject("Part::Feature", it["nome"])
            o.Shape = it["forma"]
            o.Label = it["nome"]
            if it.get("pasta"):
                if it["pasta"] not in pastas:
                    pastas[it["pasta"]] = doc.addObject("App::DocumentObjectGroup", it["pasta"])
                pastas[it["pasta"]].addObject(o)
        doc.recompute()
        for it in cena["itens"]:
            vo = doc.getObject(it["nome"]).ViewObject
            vo.ShapeColor = tuple(it["cor"])
            vo.LineColor = (0.10, 0.10, 0.10)
            vo.LineWidth = 1.0
            if it.get("transp"):
                vo.Transparency = it["transp"]
            if it.get("oculto"):
                vo.Visibility = False
        v = Gui.ActiveDocument.ActiveView
        try:
            v.setAnimationEnabled(False)      # senao a imagem sai no meio do giro da camera
            v.setCameraType("Orthographic")
        except Exception:
            pass
        for nome_vista, direcao in cena["vistas"]:
            if isinstance(direcao, str):
                getattr(v, direcao)()
            else:
                v.viewIsometric()
                v.setViewDirection(App.Vector(*direcao))
            try:
                v.setCameraType("Orthographic")
            except Exception:
                pass
            v.fitAll()
            arq = os.path.join(SAIDA, "%s_%s.png" % (cena["nome"], nome_vista))
            v.saveImage(arq, cena.get("larg", 1500), cena.get("alt", 1100), "White")
            P("imagem:", arq)
        fc = cena.get("fcstd")
        if fc:
            v.viewIsometric()
            v.fitAll()
            doc.saveAs(fc)
            P("fcstd:", fc)
        st = cena.get("step")
        if st:
            import Import
            os.makedirs(os.path.dirname(st), exist_ok=True)
            Import.export([doc.getObject(it["nome"]) for it in cena["itens"]], st)
            P("step:", st)
        App.closeDocument(doc.Name)


try:
    main()
    P("OK")
except Exception:
    P(traceback.format_exc())
finally:
    LOG.close()
    try:
        from PySide6 import QtCore, QtWidgets
        QtCore.QTimer.singleShot(300, QtWidgets.QApplication.instance().quit)
    except Exception:
        os._exit(0)
