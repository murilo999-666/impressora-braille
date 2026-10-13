# -*- coding: utf-8 -*-
"""Monta docs/tabelas-geradas.md a partir de cad/saida/lista_pecas.json (saida de cad/gerar.py).
Rodar:  python docs/gerar_tabelas.py"""
import io
import json
import os

AQUI = os.path.dirname(os.path.abspath(__file__))
rel = json.load(io.open(os.path.join(AQUI, "..", "cad", "saida", "lista_pecas.json"), encoding="utf-8"))

L = ["# Tabelas geradas pelo CAD", "",
     "Arquivo gerado por `docs/gerar_tabelas.py` a partir de `cad/saida/lista_pecas.json`. Não edite à mão:",
     "mude o CAD, rode `cad/rodar.sh gerar` e depois `python docs/gerar_tabelas.py`.", ""]

# ------------------------------------------------------------------ impressas
L += ["## Peças impressas em 3D", "",
      "Medidas já na posição de impressão (largura × profundidade × altura). A massa considera 3 paredes e 30 % de",
      "preenchimento (55 % do volume vira plástico). Todas saem sem suporte.", "",
      "| Arquivo (`cad/saida/stl/`) | Qtd | Tamanho na mesa (mm) | Massa cada (g) | Pontes (mm²) |",
      "|---|---:|---|---:|---:|"]
tot_g = 0
tot_n = 0
for l in rel["impressas"]:
    L.append("| `%s.stl` | %d | %.0f × %.0f × %.0f | %.1f | %d |" % (l["peca"], l["qtd"], l["x"], l["y"], l["z"], l["massa_g"], l["ponte_mm2"]))
    tot_g += l["qtd"] * l["massa_g"]
    tot_n += l["qtd"]
L += ["", "**Total: %d peças de %d modelos, cerca de %.0f g de filamento** (compre 1 rolo de 1 kg: sobra para repetir peças)." % (
    tot_n, len(rel["impressas"]), tot_g), ""]

# ------------------------------------------------------------------ chapas
L += ["## Chapas de MDF (corte a laser)", "",
      "| Arquivo (`cad/saida/corte_laser/`) | Tamanho (mm) | Contornos | Área (cm²) |", "|---|---|---:|---:|"]
area = 0
for l in rel["chapas"]:
    L.append("| `%s.dxf` / `.svg` | %.0f × %.0f | %d | %.0f |" % (l["peca"], l["largura"], l["altura"], l["contornos"], l["area_cm2"]))
    area += l["area_cm2"]
L += ["", "Área de MDF nas peças: %.0f cm² (%.2f m²). Pranchas prontas: %s." % (
    area, area / 10000.0, ", ".join("%d de %s mm" % (v, k.replace("x", " × ")) for k, v in rel["pranchas"].items())), ""]

# ------------------------------------------------------------------ ferragens
L += ["## Parafusos, porcas e arruelas (contagem exata do modelo)", "", "| Item | Qtd no modelo | Compre |", "|---|---:|---:|"]
for l in rel["ferragens"]:
    q = l["qtd"]
    compra = max(q + 2, int(round(q * 1.2 + 0.49)))
    L.append("| %s | %d | %d |" % (l["peca"], q, compra))
L += ["", "A coluna Compre soma 20 % de folga (no mínimo 2 a mais).", ""]

L += ["### Onde vai cada parafuso", ""]
for peca in sorted(rel["usos_parafusos"]):
    usos = rel["usos_parafusos"][peca]
    L.append("- **%s**: %s." % (peca, "; ".join("%d em %s" % (n, onde) for onde, n in usos.items())))
L.append("")

# ------------------------------------------------------------------ estoque e compras
L += ["## Peças do estoque e compradas que aparecem no modelo", "", "| Peça | Qtd |", "|---|---:|"]
for l in rel["comprados"]:
    L.append("| %s | %d |" % (l["peca"], l["qtd"]))
L.append("")

# ------------------------------------------------------------------ resumo
r = rel["resumo"]
L += ["## Números da máquina", "", "| Grandeza | Valor |", "|---|---|",
      "| Tamanho externo (L × P × A) | %.0f × %.0f × %.0f mm (sem as bandejas) |" % (r["largura_externa"], r["profundidade_externa"], r["altura_externa"]),
      "| Curso útil do carro (X) | %.0f mm |" % r["curso_x"],
      "| Margem mínima à esquerda / direita da folha A4 | %.0f mm / %.0f mm |" % (r["margem_esq_min"], r["margem_dir_min"]),
      "| Celas por linha (máximo mecânico) | %d |" % r["celas_max"],
      "| Passos por mm no X (1/16 de passo, polia de 20 dentes) | %.2f |" % r["passos_mm_x"],
      "| Passos por mm no papel (rolete de 26,5 mm) | %.2f |" % r["passos_mm_y"],
      "| Distância do rolete até a linha de punção | %.0f mm |" % r["dist_rolo_puncao"],
      "| Comprimento do laço de cada correia do X | %.0f mm (corte 650 mm para sobrar ponta) |" % r["correia_x_comprimento"],
      ""]

io.open(os.path.join(AQUI, "tabelas-geradas.md"), "w", encoding="utf-8", newline="\n").write("\n".join(L))
print("ok: %d pecas impressas, %.0f g, %.0f cm2 de MDF" % (tot_n, tot_g, area))
