#!/usr/bin/env bash
# Tira uma foto do simulador com o Edge sem janela.
#   ./capturar.sh saida.png "vista=perto&mdf=0&prog=0.5" [largura] [altura]
EDGE="/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"
AQUI="$(cd "$(dirname "$0")" && pwd)"
SAIDA="$1"; PARAMS="$2"; L="${3:-1500}"; A="${4:-950}"
PERFIL="${TMPDIR:-/tmp}/edge-captura-braille"
URL="file:///$(cygpath -m "$AQUI/index.html")?$PARAMS"
timeout 120 "$EDGE" --headless=new --no-first-run --user-data-dir="$(cygpath -w "$PERFIL")" \
  --enable-unsafe-swiftshader --hide-scrollbars --window-size="$L,$A" --virtual-time-budget=9000 \
  --screenshot="$(cygpath -w "$SAIDA")" "$URL" >/dev/null 2>&1
ls -la "$SAIDA" | awk '{print $5, $9}'
