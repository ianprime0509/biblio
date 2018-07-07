LUALATEX ?= lualatex
PDFVIEW ?= okular

.PHONY: all clean small view

all: sankta-biblio.pdf

clean:
	rm -rf sankta-biblio.tex sankta-biblio.pdf libroj/

view: sankta-biblio.pdf
	$(PDFVIEW) sankta-biblio.pdf

sankta-biblio.pdf: sankta-biblio.tex
	$(LUALATEX) sankta-biblio.tex

sankta-biblio.tex: antaŭparolo.tex konvertilo.py
	./konvertilo.py
