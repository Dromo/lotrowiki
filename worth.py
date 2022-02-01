#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# (C) Drono, 2021
#
from __future__ import absolute_import
from lxml import etree as ET
import os

class Worth(object):
    __instance = None

    def getInstance():
        if Worth.__instance == None:
            Worth()
        return Worth.__instance

    def __init__(self, *args):
        if Worth.__instance != None:
            raise Exception("This class is a singleton! " +
                "Use 'Worth.getInstance()'")
        else:
            Worth.__instance = self
        dirr = "../data"
        pathToXml = dirr+"/lotro-data/items/valueTables.xml"
        pathToXml = os.path.join(os.path.dirname(__file__), pathToXml)
        self.wroot = ET.parse(pathToXml).getroot()
        pathToXml = dirr+"/lotro-data/items/disenchantments.xml"
        pathToXml = os.path.join(os.path.dirname(__file__), pathToXml)
        self.droot = ET.parse(pathToXml).getroot()

    def getValue(self, table_id, level, quality):
        table = self.wroot.find(".//*[@id='%s']"%(table_id))
        quality = quality.upper()
        if quality == "EPIC":
            quality = "LEGENDARY"
        factor = table.find(".//quality[@key='%s']"%(quality)).get('factor')
        value = table.find(".//baseValue[@level='%s']"%(level)).get('value')
        value = int(float(value) * float(factor))
        c = int(value%100)
        s = int(((value-c)/100)%1000)
        g = int((value-c-100*s)/100000)
        return g, s, c

    def getWorthString(self, table_id, level, quality):
        g, s, c = self.getValue(table_id, level, quality)
        result = "{{worth"
        if g > 0:
            result = result + "|g=" + str(g)
        if s > 0:
            result = result + "|s=" + str(s)
        if c > 0:
            result = result + "|c=" + str(c)
        result = result + "}}"
        return result

    def getDisenchant(self, item_id):
        entry = self.droot.find(".//*[@sourceItemId='%s']"%(item_id))
        if entry != None:
            if entry.get('trophyListId') == '1879416401':
                return ('1', 'Crate of Crafting Materials')
            return (entry.get('quantity'), entry.get('name'))
        else:
            return None

    def getDisenchantString(self, item_id):
        temp = self.getDisenchant(item_id)
        if temp != None:
            return "{{Disenchant|"+temp[0]+"|"+temp[1]+"}}"
        else:
            return None


