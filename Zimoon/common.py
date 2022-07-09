#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import pywikibot
from pywikibot import editor as editarticle
#from __future__ import absolute_import
#from pywikibot import pagegenerators
#import mwparserfromhell as mwparser

count   = 0
changed = 0
debug   = False
context = 0

# Usage: run([dry_run], generator, replace_func, comment)
# dry_run       defaults to False
# generator     object of the pywikibot.pagegenerators module
# replace_func  custom replace function that takes the page as
#               input and returns its changed, or unchanged, text contents
# comment       summary text added to each commit
def run(gen, replace_func, comment, dry_run=False):
    always = False
    for page in gen:
        always = __edit_page__(page, comment, always, dry_run, replace_func)
    print(changed)

def __edit_page__(page, summary, always, dry_run, replace_func):
    global context
    global count
    count += 1
    pywikibot.output(f"\n{count}\t{page.title()}")
    try:
        original_text = page.get()
        if not page.has_permission():
            pywikibot.output(f"You can't edit page {page.title()}")
            return always
    except pywikibot.NoPageError:
        pywikibot.output(f"Page {page.title()} not found")
        return always
    except pywikibot.IsRedirectPage:
        return always

    new_text = replace_func(page)

    if new_text == original_text:
        if debug:
            pywikibot.output(f"No changes were necessary in {page.title()}")
        return always

    if not always:
        print("\a")
    if dry_run:
        pywikibot.showDiff(original_text, new_text, context=context)
        return always
        
    def save(p, nt):
        global changed
        p.text = nt
        try:
            p.save(summary=summary)
        except pywikibot.EditConflict:
            pywikibot.output(
                f"Skipping {page.title()} because of edit conflict")
        except pywikibot.SpamfilterError as e:
            pywikibot.output(
                f"Cannot change {page.title()} because of blacklist entry {e.url}")
        except pywikibot.LockedPage:
            pywikibot.output(f"Skipping {page.title()} (locked page)")
        except pywikibot.PageNotSaved as error:
            pywikibot.output(f"Error putting page: {error.args}")
        changed += 1

    while True:
        pywikibot.showDiff(original_text, new_text, context=context)
        if always:
            break
        try:
            choice = pywikibot.input_choice(
                'Do you want to accept these changes?',
                [('Yes', 'y'), ('No', 'n'), ('Edit original', 'e'),
                 ('edit Latest', 'l'), ('open in Browser', 'b'),
                 ('More context', 'm'), ('All', 'a')],
            default='N')
        except pywikibot.bot_choice.QuitKeyboardInterrupt:
            sys.exit(0)
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
                pywikibot.output(f"Page {page.title()} has been deleted.")
                break
            new_text = original_text
            last_text = None
            continue
        if choice == 'a':
            always = True
        if choice == 'y':
            save(page, new_text)
        break

    if always and new_text != original_text:
        save(page, new_text)
    return always
