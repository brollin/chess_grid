#!/usr/bin/env zsh

find . -type f -name '??.svg' | awk -F / '{print $0 " " $3 " " $4}' | while read filepath chessset filename; do (cp "${filepath}" "${filename/.*}/${chessset}.svg" && cd "${filename/.*}" && qlmanage -t -s 100 -o . "${chessset}.svg" && rm "${chessset}.svg"); done

find . -name "*.svg.png" | while read filename; do mv $filename ${filename/.svg}; done
