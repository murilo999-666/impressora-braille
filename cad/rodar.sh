#!/usr/bin/env bash
# Atalhos para rodar os scripts do CAD no FreeCAD (Git Bash).
#   ./rodar.sh verificar [rapido]      confere interferencias (modo console)
#   ./rodar.sh render <cena> [pasta]   gera imagens de uma cena de vistas.py (abre o FreeCAD por alguns segundos)
#   ./rodar.sh gerar                   exporta STL, STEP, DXF/SVG e listas (modo console)
# pasta bin do FreeCAD: mude com a variavel FREECAD_BIN se o seu estiver em outro lugar
FC="${FREECAD_BIN:-$(cygpath -u "$LOCALAPPDATA")/Programs/FreeCAD 1.1/bin}"
AQUI="$(cd "$(dirname "$0")" && pwd)"
FILTRO='^\s*$|Recompute|\(100 %\)|^FreeCAD 1|^\(C\) 20|^FreeCAD is free'
case "$1" in
  verificar)
    [ "$2" = "rapido" ] && export BR_RAPIDO=1
    timeout 900 "$FC/freecadcmd.exe" "$(cygpath -w "$AQUI/verificar.py")" 2>&1 | grep -v -E "$FILTRO"
    ;;
  render)
    export BR_ALVO="$2"
    SAIDA="${3:-$AQUI/../imagens}"
    mkdir -p "$SAIDA"
    export BR_SAIDA="$(cygpath -w "$SAIDA")"
    timeout 600 "$FC/freecad.exe" "$(cygpath -w "$AQUI/render.py")" >/dev/null 2>&1
    cat "$SAIDA/render.log"
    ;;
  gerar)
    mkdir -p "$AQUI/saida"
    timeout 1200 "$FC/freecadcmd.exe" "$(cygpath -w "$AQUI/gerar.py")" > "$AQUI/saida/console.log" 2>&1
    cat "$AQUI/saida/resumo_geracao.txt"
    ;;
  mesas)
    timeout 900 "$FC/freecadcmd.exe" "$(cygpath -w "$AQUI/mesas.py")" > "$AQUI/saida/console_mesas.log" 2>&1
    cat "$AQUI/saida/mesas_250x250/resumo_mesas.txt" 2>/dev/null || cat "$AQUI/resumo_mesas.txt"
    ;;
  *)
    echo "uso: ./rodar.sh verificar [rapido] | render <cena> [pasta] | gerar | mesas"
    ;;
esac
