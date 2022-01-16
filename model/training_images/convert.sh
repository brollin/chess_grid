#!/usr/bin/env zsh

find . -type f -name '??.svg' | awk -F / '{print $0 " " $3 " " $4}' | while read filepath chessset filename; do (cp "${filepath}" "${filename/.*}/${chessset}.svg" && cd "${filename/.*}" && qlmanage -t -s 1000 -o . "${chessset}.svg"); done

