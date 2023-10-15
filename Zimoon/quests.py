#!/usr/bin/python
# -*- coding: utf-8 -*-

import pywikibot, sys
from pywikibot import pagegenerators
import mwparserfromhell as mwparser
from pywikibot import editor as editarticle
import common as ac

def start():
    site = pywikibot.Site()

    # get references from a page (any kind but ot category)
    page = pywikibot.Page(site, title="Twenty-first hall")
    gen = page.getReferences(only_template_inclusion=False)

    #cat = pywikibot.Category(site, "Walls of Moria Quests")

    # get normal pages from 'cat'
    #gen = pagegenerators.CategorizedPageGenerator(cat, recurse=True)

    # get categories from 'cat'
    #gen = pagegenerators.SubCategoriesPageGenerator(cat, recurse=True)

    return gen
    
def is_obsolete(wcode):
    templates = wcode.filter_templates()
    for t in templates:
        if str(t.name).strip() == 'Obsolete':
            return True
    return False

def prt():
    gen = start()
    ff = open("./startingloc.txt","w+")
    counter = 0
    for page in gen:
        text = page.get()
        wikicode = mwparser.parse(text)
        if is_obsolete(wikicode):
            continue
        templates = wikicode.filter_templates()
        for template in templates:
            qs = sl = l = ""
            if str(template.name).strip() == "Infobox Quests":
                sl = "  === MISSING ==="
                if template.has('startinglocation'):
                    sl = str(template.get('startinglocation').value).strip()
                    if not sl:
                        sl = "  === MISSING ==="
                txt =  f"{sl}\t{page.full_url()}\n"
                counter += 1
                print(f"{page.title()} {counter}")
                ff.write(txt)
            if counter % 100 == 0:
                ff.flush()
        #break
    ff.flush()
    ff.close()
    
def replace(page):
    text = page.get()
    wikicode = mwparser.parse(text)
    if is_obsolete(wikicode):
        return text
        
    # def x2or(txt):
        # txt = txt.replace("<br>", " ") ##### problem with <br> without anything
        # # else, expected ',' or something
        # txt = txt.replace("<br/>", " ")
        # txt = txt.replace("<br />", " ")
        # txt = txt.replace("''or''", "or")
        # txt = txt.replace(", ", " or ")
        # txt = txt.replace("  ", " ")
        # txt = txt.replace("or or", "or")
        # txt = txt.replace(" or ", " <small>''or''</small> ")
        # txt = txt.replace("<small><small>", "<small>")
        # txt = txt.replace("</small></small>", "</small>")
        # txt = txt.replace("<small>or</small>", "<small>''or''</small>")
        # txt = txt.replace("  ", " ")
        # txt = txt.strip()
        # return txt

    # param1 = "queststarter"
    # param2 = "startinglocation"
    # param3 = "questender"
    # param4 = "endinglocation"
    # templates = wikicode.filter_templates()
    # for template in templates:
        # if str(template.name).strip() == "Infobox Quests":
            # if template.has(param1):
                # value = str(template.get(param1).value).strip()
                # val = x2or(value)
                # template.add(param1, val)
            # if template.has(param2):
                # value = str(template.get(param2).value).strip()
                # val = x2or(value)
                # template.add(param2, val)
            # if template.has(param3):
                # value = str(template.get(param3).value).strip()
                # val = x2or(value)
                # template.add(param3, val)
            # if template.has(param4):
                # value = str(template.get(param4).value).strip()
                # val = x2or(value)
                # template.add(param4, val)
            # if template.has("region1"):
                # if (   not template.has("maprefNS1")
                    # or not template.has("maprefEW1")):
                    # template.add("region1", "")
            # if template.has("region2"):
                # if (   not template.has("maprefNS2")
                    # or not template.has("maprefEW2")):
                    # template.add("region2", "")

    txt10 = "Twenty-first hall"
    txt12 = "The Twenty-first Hall"
    text = text.replace(txt10, txt12)
            
    return text # wikicode # text

def main():
    #prt()
    ac.run(start(), replace, "fix redirect links")

if __name__ == '__main__':
    main()
