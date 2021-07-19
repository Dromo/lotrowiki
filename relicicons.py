#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# (C) Drono, 2021
#
from __future__ import absolute_import
import pywikibot
import os
import hashlib

class RelicIconEditor(object):

    def __init__(self, *args):
        self.site = pywikibot.Site()
        self.edited = 0
        self.comment = "Drono-bot: Upload icon"
        self.file = "./scripts/userscripts/lotrowiki/icons"
        self.iconDir = "./scripts/userscripts/data/lotro-relics/relicIcons/"
        if not os.path.isfile(self.file):
            pywikibot.error('File "'+self.file+'" does not exist!')
            sys.exit(1)
        if not os.path.isdir(self.iconDir):
            pywikibot.error('Directory for icon files "'+self.iconDir+
                '" does not exists!')
            sys.exit(1)


    def edit_page(self, page, filename):
        try:
            pagename = page.title(underscore=True, with_ns=False)
            page.download()
            if hashfile(pagename) == hashfile(filename):
                pywikibot.output("No difference.")
                os.remove(pagename)
                return
            os.remove(pagename)
        except pywikibot.exceptions.NoPageError:
            pywikibot.output("Page does not exists.")
        result = page.upload(source=filename,
                             ignore_warnings="exists",
                             comment=self.comment)
        if result:
            pywikibot.output("File "+pagename+" uploaded seccesfuly")
            self.edited += 1
        else:
            pywikibot.output("Error uploading "+filename)


    def run(self):
        self.site.login()
        with open(self.file) as f:
            for line in f:
                icon_id, icon_name = line.strip().split(" ",1)
                page_name = icon_name+".png"
                page = pywikibot.FilePage(self.site, page_name)
                self.edit_page(page, self.iconDir+icon_id)
        pywikibot.output('Changed '+str(self.edited)+' icons.')


def hashfile(path, blocksize = 65536):
    afile = open(path, 'rb')
    hasher = hashlib.md5()
    buf = afile.read(blocksize)
    while len(buf) > 0:
        hasher.update(buf)
        buf = afile.read(blocksize)
    afile.close()
    return hasher.hexdigest()


def main(*args):
    app = RelicIconEditor(*args)
    app.run()


if __name__ == '__main__':
    main()
