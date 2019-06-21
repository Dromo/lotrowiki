#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# (C) Drono, 2019
#
import pywikibot
from pywikibot import pagegenerators
import mwparserfromhell as mwparser
from pywikibot import editor as editarticle

always = False
d = {}

def main(dry_run):
    always = False
    site = pywikibot.Site()
    cat = pywikibot.Category(site, 'Virtue Deeds')
    gen = pagegenerators.CategorizedPageGenerator(cat, recurse=True)
    for page in gen:
        always = edit_page(page,'Drono-bot:virtue conversion',always,dry_run)

def edit_page(page,summary,always=False,dry_run=False):
    pywikibot.output(page.title())
    try:
        original_text = page.get()
        if not page.canBeEdited():
            pywikibot.output("You can't edit page " + page.title(as_link=True))
            return always
    except pywikibot.NoPage:
        pywikibot.output(u"Page {0} not found".format(page.title(as_link=True)))
        return always
    except pywikibot.IsRedirectPage:
        return always
    new_text = replace_text(original_text)
    if new_text == original_text:
        pywikibot.output('No changes were necessary in '
                         + page.title(as_link=True))
        return always
    context = 0
    if dry_run:
        pywikibot.showDiff(original_text, new_text, context=context)
        return always

    while True:
        pywikibot.showDiff(original_text, new_text, context=context)
        if always:
            break
        choice = pywikibot.input_choice(
            'Do you want to accept these changes?',
            [('Yes', 'y'), ('No', 'n'), ('Edit original', 'e'),
             ('edit Latest', 'l'), ('open in Browser', 'b'),
             ('More context', 'm'), ('All', 'a')],
            default='N')
        if choice == 'm':
            context = context * 3 if context else 3
            continue
        if choice == 'e':
            editor = editarticle.TextEditor()
            as_edited = editor.edit(original_text)
            # if user didn't press Cancel
            if as_edited and as_edited != new_text:
                new_text = as_edited
            continue
        if choice == 'l':
            editor = editarticle.TextEditor()
            as_edited = editor.edit(new_text)
            # if user didn't press Cancel
            if as_edited and as_edited != new_text:
                new_text = as_edited
                # prevent changes from being applied again
                last_text = new_text
            continue
        if choice == 'b':
            pywikibot.bot.open_webbrowser(page)
            try:
                original_text = page.get(get_redirect=True, force=True)
            except pywikibot.NoPage:
                pywikibot.output('Page {0} has been deleted.'
                                 .format(page.title()))
                break
            new_text = original_text
            last_text = None
            continue
        if choice == 'a':
            always = True
        if choice == 'y':
            page.text = new_text
            page.save(summary=summary)
        break
    if always and new_text != original_text:
        try:
            page.text = new_text
            page.save(summary=summary)
        except pywikibot.EditConflict:
            pywikibot.output('Skipping {0} because of edit conflict'
                             .format(page.title(),))
        except pywikibot.SpamfilterError as e:
            pywikibot.output(
                'Cannot change {0} because of blacklist entry {1}'
                .format(page.title(), e.url))
        except pywikibot.LockedPage:
            pywikibot.output('Skipping {0} (locked page)'
                             .format(page.title(),))
        except pywikibot.PageNotSaved as error:
            pywikibot.output('Error putting page: {0}'
                             .format(error.args,))
    return always

def replace_text(text):
    wikicode = mwparser.parse(text)
    templates = wikicode.filter_templates()
    for template in templates:
        if template.name == 'Deed\n':
            if template.has('Virtue'):
                virtue = str(template.get('Virtue').value).strip()
                if virtue == 'Virtue Experience':
                    return unicode(wikicode)
                if len(virtue) > 0 :
                    template.add('Virtue','Virtue Experience')
                if template.has('Virtue2'):
                    virtue2 = str(template.get('Virtue2').value).strip()
                    if len(virtue2) > 0 :
                        template.add('Virtue2','')
                virtuevalue = str(template.get('Virtue-value').value).strip()
                virtuevalue2 = 0
                if template.has('Virtue2-value'):
                    virtuevalue2 = str(template.get('Virtue2-value').value).strip()
                    if len(virtuevalue2) > 0 :
                        virtuevalue2 = int(virtuevalue2) * 2000
                        template.add('Virtue2-value','')
                    else:
                        virtuevalue2 = 0
                if len(virtuevalue) > 0 :
                    virtuevalue = int(virtuevalue) * 2000 + virtuevalue2
                    template.add('Virtue-value',virtuevalue)
    return unicode(wikicode)


if __name__ == '__main__':
    main(False)
