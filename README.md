# html2doku

Converts HTML to DokuWiki markup.  It currently only supports the following tags and attributes:

* Links: `<a href="...">link</a>`
* Headings: `<h1>`-`<h6>`
* Strike-through text (~~like this~~): `<span style="text-decoration:strike-through;">`
* *Italics* and **bold**: `<em>`, `<strong>`, `<i>`, `<b>`
* Line breaks: `<br>`
* Unordered lists: `<ul>`, `<li>`
* Ordered lists: `<ol>`, `<li>`

This is very limited at the moment. It is intended to aid conversions from HTML, but the result will
likely have to be manually edited as well.

## Usage

```bash
python html2doku.py [-i input_file] [-o output_file]
```

You can specify an input HTML file (using `-i file`) and output file in DokuWiki markup (using `-o file`).
If either one is not specified, standard input and standard output will be used for input and output, respectively.

Running `python html2doku.py --help` displays usage instructions:

```
usage: html2doku.py [-h] [--input INPUT] [--output OUTPUT]

Convert HTML to DokuWiki markup

optional arguments:
  -h, --help            show this help message and exit
  --input INPUT, -i INPUT
                        an HTML document file (stdin if not specified)
  --output OUTPUT, -o OUTPUT
                        destination file for the DokuWiki markup (stdout if not specified)
```
