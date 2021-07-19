#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# (C) Drono, 2021
#
from __future__ import absolute_import
from lxml import etree as ET
import os
from . import deed

class Barter(object):
    __instance = None

    def __init__(self):
        if Barter.__instance != None:
            raise Exception("This class is a singleton! " +
                "Use 'Barter.getInstance()'")
        else:
            Barter.__instance = self
            pathToXml = "../data/lotro-data/trade/barters.xml"
            pathToXml = os.path.join(os.path.dirname(__file__), pathToXml)
            self.root = ET.parse(pathToXml).getroot()
            self.requirments = dict()

    def getInstance():
        if Barter.__instance == None:
            Barter()
        return Barter.__instance

    def getBarterString(self, item):
        output = ""
        rid = item.get('key')
        for elem in self.root.findall(".//receive[@id='%s']"%(rid)):
            elem = elem.getparent()
            quantity = elem.find('give').get('quantity')
            currency = elem.find('give').get('name')
            if quantity == None:
                quantity = ""
            if currency == None:
                currency = ""
            elem = elem.getparent()
            require = elem.get('requiredQuest')
            if require != None:
                require = require.split(';')[0]
                if require not in self.requirments:
                    d = deed.Deed.getInstance()
                    d.setId(require)
                    deedName = d.getName()
                    self.requirments[require] = deedName
                require = self.requirments[require]
                require = "Requires completion of '[["+require+"]]'"
            else:
                require = ""
            profileId = elem.get('profileId')
            barters = self.root.findall(".//barterer/" +
                "barterProfile[@profileId='%s']"%(profileId))
            barterNames = set()
            for barter in barters:
                barterName = barter.getparent().get('name')
                barterNames.add(barterName)
            barterName = "]], [[".join(barterNames)
            print(barterName)
            output = output + """
== Barter Information ==
{{Barter
| npc    = [["""+barterName+"""]] """+require+"""
| colums = 2
| get1   = {{Reward|"""+item.get('name')+"""}}
| give1  = {{Reward|"""+currency+"""|"""+quantity+"""}}
}}
"""
        return output

