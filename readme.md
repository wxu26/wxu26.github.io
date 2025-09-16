compiling notion md files to html:
pandoc input_name.md --template=template.html -o output_name.html --mathjax --metadata title="title"
then manually specify image widths