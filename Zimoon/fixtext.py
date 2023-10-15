#!/usr/bin/python
# -*- coding: utf-8 -*-

import pywikibot, sys
from pywikibot import pagegenerators
import mwparserfromhell as mwparser
from pywikibot import editor as editarticle
import common as ac

def start():
    site = pywikibot.Site()

    #page = pywikibot.Page(site, title="Template:Item Tooltip")
    page = pywikibot.Page(site, title="Goblin-town")
    
    gen = page.getReferences(only_template_inclusion=False)
    return gen

def prt():
    count = 1
    gen = start()
    ff = open("./repeateble.txt","w")
    for page in gen:
        text = page.get()
        wikicode = mwparser.parse(text)
        templates = wikicode.filter_templates()
        for template in templates:
            if str(template.name).strip() == 'Infobox Quests':
                if template.has('repeatable'):
                    print(count + "\t" + page.title())
                    value = str(template.get('repeatable').value).strip()
                    if value:
                        ff.write(f"{value}, {page.title()}\n")
    ff.close()

def fix_text(page):
    find = "area       = Goblin-town"
    repl = "area       = Goblin-town (Area)"
    
    text = page.get()
    text = text.replace(find, repl)
    
    return text

def fix_params(page):
    text = page.get()
    wikicode = mwparser.parse(text)
    templates = wikicode.filter_templates()
    for template in templates:
        if str(template.name).strip() == 'Item Tooltip':
            if template.has('bind'):
                value = str(template.get('bind').value).strip()
                ff.write(f"{value}, {link}\n")
    return wikicode
    
def main():
    #prt()
    ac.run(start(), fix_text, "fix link")

if __name__ == '__main__':
    main()
