#!/usr/bin/env python3

import os
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
            if verso.get('rend') != 'cont':
                eligo.write('\\verse{{{}}} '.format(verso.get('n')))
            eligo.write(verso.text)
            for lb in verso.findall("./lb"):
                tail = '' if lb.tail is None else lb.tail
                eligo.write('\\newline' + tail)
            eligo.write('\n')
        if alineo.get('rend') == 'indent':
            eligo.write('\\end{indented}\n')
        eligo.write('\\par\n')

if __name__ == '__main__':
    tree = ET.parse('biblio.xml')
    root = tree.getroot()

    malnova_testamento = root.find(".//text[@id='MT']")
    mt_libroj = malnova_testamento.findall("./body/div[@type='book']")
    mt_dosierujo = 'libroj/mt'
    os.makedirs(mt_dosierujo, exist_ok=True)
    for libro in mt_libroj:
        eligo = open('{}/{}.tex'.format(mt_dosierujo, libro.get('id')), 'w')
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
        eligo.close()
