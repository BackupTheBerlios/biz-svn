#! /bin/bash
# Creates Biz documentation

files="tutorial routing overview templating specialprops"

for f in $files
do
	rst2html $f.txt > $f.html
	rst2latex $f.txt > $f.tex
	pdflatex $f.tex
done

