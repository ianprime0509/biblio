#!/usr/bin/env python3

import argparse
import os
import sys
import xml.etree.ElementTree as ET

def titoluskligi(titolo):
    # Etaj vortoj kiuj ne devas majuskliĝi en titolo
    vortetoj = frozenset(['al', 'de', 'la'])
    vortoj = titolo.split(' ')
    def titoluskligi_vorton(vorto):
        vorto = vorto.lower()
        return vorto.capitalize() if vorto not in vortetoj else vorto
    resto = [titoluskligi_vorton(vorto) for vorto in vortoj[1:]]
    return ' '.join([vortoj[0].capitalize(), *resto])

def eligi_ĉapitron(eligo, ĉapitro):
    alineoj = ĉapitro.findall("./lg[@type='para']")
    for alineo in alineoj:
        if alineo.get('rend') == 'indent':
            eligo.write('\\begin{indented}\n')
        versoj = alineo.findall("./l")
        for verso in versoj:
            eligi_verson(eligo, verso)
        if alineo.get('rend') == 'indent':
            eligo.write('\\end{indented}\n')
        eligo.write('\\par\n')

def eligi_libron(eligo, libro):
    rubrikoj = libro.findall("./head")
    titolo = titoluskligi(rubrikoj[0].text)
    if len(rubrikoj) == 1:
        eligo.write('\\begin{{book}}{{{}}}\n'.format(titolo))
    else:
        subtitolo = titoluskligi(rubrikoj[1].text)
        eligo.write('\\begin{{book}}[{}]{{{}}}\n'.format(subtitolo, titolo))
    ĉapitroj = libro.findall("./div[@type='chapter']")
    for ĉapitro in ĉapitroj:
        eligo.write('\\begin{{chapter}}{{{}}}\n'.format(ĉapitro.get('n')))
        eligi_ĉapitron(eligo, ĉapitro)
        eligo.write('\\end{chapter}\n')
    eligo.write('\\end{book}\n')

def eligi_verson(eligo, verso):
    if verso.get('rend') != 'cont':
        eligo.write('\\verse{{{}}}{{'.format(verso.get('n')))
    eligo.write(verso.text)
    for filo in verso:
        vosto = '' if filo.tail is None else filo.tail
        if filo.tag == 'lb':
            eligo.write('\\newline')
        elif filo.tag == 'note' and filo.get('type') == 'footnote':
            eligo.write('\\footnote{{{}}}'.format(filo.text))
        else:
            print('Trovis nerekonitan elementon {}'.format(filo.tag),
                  file=sys.stderr)
        eligo.write(vosto)
    if verso.get('rend') != 'cont':
        eligo.write('}')
    eligo.write('\n')

if __name__ == '__main__':
    argumentilo = argparse.ArgumentParser()
    argumentilo.add_argument('-n', '--nur', required=True)
    argumentoj = argumentilo.parse_args()

    arbo = ET.parse('biblio.xml')
    radiko = arbo.getroot()

    with open('sankta-biblio.tex', 'w') as biblio_eligo:
        biblio_eligo.write('\\input{antaŭparolo}\n')
        if argumentoj.nur is not None:
            biblio_eligo.write('\\includeonly{{{}}}\n'.format(argumentoj.nur))
        biblio_eligo.write('\\begin{document}\n')
        biblio_eligo.write('\\input{titolpaĝo}\n')
        biblio_eligo.write('\\mainmatter\n')

        # Malnova Testamento
        biblio_eligo.write('\\input{titolpaĝo-mt}\n')
        biblio_eligo.write('\\biblecontent\n')

        malnova_testamento = radiko.find(".//text[@id='MT']")
        mt_libroj = malnova_testamento.findall("./body/div[@type='book']")
        mt_dosierujo = 'libroj/mt'
        os.makedirs(mt_dosierujo, exist_ok=True)
        for libro in mt_libroj:
            dosiernomo = '{}/{}'.format(mt_dosierujo, libro.get('id'))
            biblio_eligo.write('\\include{{{}}}\n'.format(dosiernomo))
            with open(dosiernomo + '.tex', 'w') as eligo:
                eligi_libron(eligo, libro)

        # Nova Testamento
        biblio_eligo.write('\\input{titolpaĝo-nt}\n')
        biblio_eligo.write('\\biblecontent\n')

        nova_testamento = radiko.find(".//text[@id='NT']")
        nt_libroj = nova_testamento.findall("./body/div[@type='book']")
        nt_dosierujo = 'libroj/nt'
        os.makedirs(nt_dosierujo, exist_ok=True)
        for libro in nt_libroj:
            dosiernomo = '{}/{}'.format(nt_dosierujo, libro.get('id'))
            biblio_eligo.write('\\include{{{}}}\n'.format(dosiernomo))
            with open(dosiernomo + '.tex', 'w') as eligo:
                eligi_libron(eligo, libro)

        biblio_eligo.write('\\end{document}\n')
