#!/usr/bin/env bash
# Publica esta pasta no repositorio publico do GitHub (murilo999-666/impressora-braille).
#   ./publicar.sh "o que mudou"
#
# O git deste repositorio fica FORA da pasta do projeto (em Murilo/.repos/impressora-braille.git):
# a pasta 1-Competicoes inteira vai para outro repositorio, o do backup, e um .git aqui dentro atrapalharia.
# O token do GitHub nunca e gravado: use a variavel GH_TOKEN ou digite quando o script pedir.
AQUI="$(cd "$(dirname "$0")" && pwd)"
GITDIR="${BRAILLE_GIT_DIR:-$(cd "$AQUI/../../.." && pwd)/.repos/impressora-braille.git}"
[ -d "$GITDIR" ] || { echo "nao achei o git do projeto em $GITDIR"; exit 1; }
MSG="${1:-atualizacao}"
if [ -z "$GH_TOKEN" ]; then read -r -s -p "Token do GitHub: " GH_TOKEN; echo; fi
B64=$(printf 'x-access-token:%s' "$GH_TOKEN" | base64 -w0)
export GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0="http.https://github.com/.extraheader" GIT_CONFIG_VALUE_0="AUTHORIZATION: basic $B64"
export GIT_TERMINAL_PROMPT=0 GIT_DIR="$GITDIR" GIT_WORK_TREE="$AQUI"
cd "$AQUI" || exit 1
git add -A
if git diff --cached --quiet; then
  echo "nada mudou desde a ultima publicacao"
else
  git status --short | head -40
  git commit -q -m "$MSG" && echo "commit feito"
fi
git push origin HEAD:main
