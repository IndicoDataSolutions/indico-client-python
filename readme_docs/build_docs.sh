#!/bin/bash

pip install sphinx-markdown-builder==0.6.5 sphinx-autodoc-typehints==1.24.0
# docs are outputted to ./markdown
sphinx-build -M markdown ./docsrc .
cd ./markdown

# update links
find . -type f -name '*.md' -print0 | xargs -0 sed -i -r 's/\[(`\w+`)\]\(.+\)/\1/'
find . -type f -name '*.md' -print0 | xargs -0 sed -i 's/.md//'

# move docs into folders for upload
mkdir types
mkdir classes
for filename in $(find . -maxdepth 1 -type f); do
    if [[ $filename == *"-types.md" ]]; then
        mv $filename ./types
    elif [[ $filename != *"/types.md"  ]] && [[ $filename != *"/classes.md"  ]] && [[ $filename != *"/index.md"  ]] ; then
        mv $filename ./classes 
    fi
done