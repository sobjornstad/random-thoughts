#!/usr/bin/env bash

sourcefile="$HOME/random-thoughts.txt"
tempfile="/tmp/rt-public.txt"
target="$(dirname "$0")/index.html"

rtgrep -p '.*' "$sourcefile" >"$tempfile"
vim \
    -E \
    -c "let g:html_no_progress=1" \
    -c "set background=light" \
    -c "colorscheme solarized" \
    -c "set ft=randomthoughts" \
    -c "runtime syntax/2html.vim" \
    -c "wqa" \
    "$tempfile"

python "$(dirname "$0")/linkify.py" "$tempfile.html" "$target" || { echo "Linkify failed, stopping"; exit 1; }

# horrendous hack to fix Vim using a bogus set of colors for no discernible or fixable reason
#patch -u index.html fix-colorscheme.diff
#rm -f index.html.orig
git add -p index.html || { echo "Canceling"; exit 1; }
git commit -m "update" || { echo "Commit canceled, stopping"; exit 1; }
git restore index.html
echo "If all looks good, run 'git push'."

rm -- "${tempfile:?eek}"
