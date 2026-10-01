#!/usr/bin/env bash
# Builds the CV and cover letter PDFs into the repo root (aux files go to .build/).
# The PDF name comes from the "%! jobname = ..." line at the top of each .tex file.
# Usage: ./build.sh            build both
#        ./build.sh cv         build only cv.tex
#        ./build.sh clean      remove .build/ and generated PDFs
set -euo pipefail
cd "$(dirname "$0")"

build() {
  local src="$1.tex" name
  name=$(sed -n 's/^%! *jobname *= *//p' "$src" | head -1)
  name=${name:-$1}
  latexmk -pdf -interaction=nonstopmode -halt-on-error -auxdir=.build -jobname="$name" "$src"
}

case "${1:-all}" in
  all)          build cover_letter && build cv ;;
  cv)           build cv ;;
  cover_letter) build cover_letter ;;
  clean)        rm -rf .build && for f in cv cover_letter; do
                  n=$(sed -n 's/^%! *jobname *= *//p' "$f.tex" | head -1); rm -f "${n:-$f}.pdf"
                done ;;
  *)            echo "usage: $0 [all|cv|cover_letter|clean]" >&2; exit 1 ;;
esac
