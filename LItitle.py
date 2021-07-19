#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# (C) Drono, 2021
#
from lxml import etree as ET
import os
import worth
import deed
import functions as lf

class Titles(object):
    __instance = None

    def __init__(self):
        if Titles.__instance != None:
            raise Exception("This class is a singleton! " +
                "Use 'Titles.getInstance()'")
        else:
            Titles.__instance = self
            pathToXml = "../data/lotro-data/legendary/legendary_titles.xml"
            pathToXml = os.path.join(os.path.dirname(__file__), pathToXml)
            self.root = ET.parse(pathToXml).getroot()
            pathToXml = "../data/lotro-items-db/items.xml"
            pathToXml = os.path.join(os.path.dirname(__file__), pathToXml)
            self.itemroot = ET.parse(pathToXml).getroot()
            pathToXml = "../oftheThreshold.icon"
            pathToXml = os.path.join(os.path.dirname(__file__), pathToXml)
            self.icons = lf.getIconDict(pathToXml)
            pathToXml = "../data/lotro-data/items/containers.xml"
            pathToXml = os.path.join(os.path.dirname(__file__), pathToXml)
            self.containerroot = ET.parse(pathToXml).getroot()
            pathToXml = "../data/lotro-data/loots/loots.xml"
            pathToXml = os.path.join(os.path.dirname(__file__), pathToXml)
            self.lootroot = ET.parse(pathToXml).getroot()
            directory = "../pages/"
            self.directory = os.path.join(os.path.dirname(__file__), directory)

    def getInstance():
        if Titles.__instance == None:
            Titles()
        return Titles.__instance

    def getPath(path):
        return os.path.join(os.path.dirname(__file__), directory)

    def setTitleName(self, name):
        self.item = self.itemroot.find(".//item[@name='%s']"%name)
        self.title = self.root.find(".//title[@name='%s']"%name)

    def itemTooltip(self):
        item = self.item
        title = self.title
        if item == None or title == None:
            return ""
        output = "<onlyinclude>{{Item Tooltip"
        output = output + lf.addParam('mode', '{{{mode|}}}')
        output = output + lf.addParam('arg', '{{{arg|}}}')
        output = output + lf.addParam('amount', '{{{amount|}}}')
        output = output + lf.addParam('name', item.get('name'))
        icon = lf.getIconName(self.icons, item.get('icon'))
        output = output + lf.addParam('icon', icon)
        output = output + lf.addParam('disambigpage', 'Item:'+item.get('name'))
        quality = item.get('quality').capitalize()
        if quality == 'Legendary':
            quality = 'Epic'
        output = output + lf.addParam('quality', quality)
        output = output + lf.addParam('item_level', item.get('level'))
        output = output + lf.addParam('consumed', 'y')
        output = output + lf.addParam('bind',
            lf.getBinding(item.get('binding')))
        LImodifier = title.get('category') + ", Tier " + title.get('tier')
        output = output + lf.addParam('LImodifier', LImodifier)
        if item.get('requiredClass') == None:
            attrib = "Applies a title to a legendary weapon item."
        else:
            attrib = "Applies a title to a legendary class item."
        output = output + lf.addParam('attrib', attrib)
        output = output + lf.addParam('level', item.get('minLevel'))
        if item.get('requiredClass') != None:
            classN = 1
            for klass in item.get('requiredClass').split(";"):
                if classN == 1:
                    output = output + lf.addParam('class', klass)
                else:
                    output = output + lf.addParam('class'+str(classN), klass)
                classN = classN + 1
        flavor = item.get('description').replace('\n', '<br>')
        output = output + lf.addParam('flavor', flavor)
        worthObject = worth.Worth.getInstance()
        sell = worthObject.getWorthString(item.get('valueTableId'),
            item.get('level'), item.get('quality'))
        output = output + lf.addParam('sell', sell)
        firstcategory = 'Legendary Item Title Items'
        output = output + lf.addParam('first-category', firstcategory)
        output = output + "\n}}</onlyinclude>__NOTOC__"
        return output + "\n\n"

    def itemInfo(self, item):
        output = "== Item Information =="
        output = output + """
This item can be obtained from a {{Reward|"""+item+"""}}."""
        return output + "\n\n"

    def statInfo(self):
        itype = 'Weapon'
        if self.item.get('requiredClass') != None:
            itype = 'Class'
        output = "Applying this item to a [[Legendary Items|Legendary "
        output = output + itype + " Item]] provides the following bonuses:"
        #TODO create function for making index table instead of this:
        table = '|-\n| {{Reward|'+self.item.get('name')+'}} || '
        if self.damageType() != None:
            output = output + "\n* Sets damage type to [[" + self.damageType()
            output = output + "]]"
            table = table + '[[' + self.damageType() + ']] ||'
        if self.damageTo() != None:
            output = output + "\n* +11 damage to [[" + self.damageTo() + "]]"
            table = table + "+11 damage to [[" + self.damageTo() + "]],"
        for stat in self.title.findall(".//stat"):
            statName = stat.get('name')
            statValue = lf.formatStatNumber(statName, stat.get('value'))
            statName = lf.getStatString(statName)
            percent = ""
            if statName[0] == '%':
                statName = statName[2:]
                percent = '%'
            if "-type Damage" in statName:
                statName = "Damage Types|"+statName
            output = output + "\n* +"+statValue+percent+" [["+statName+"]]"
            table = table + " +"+statValue + percent + " [[" + statName + "]],"
        table = table[:-1]
        print(table)
        return output + "\n\n"

    def damageTo(self):
        types = [
            "Ancient Evil",
        ]
        for dtype in types:
            if dtype in self.item.get('name'):
                return dtype

    def damageType(self):
        types = {
            "Deep Halls" : "Ancient Dwarf-make",
            "Eldar Days" : "Beleriand",
            "Númenór" : "Westernesse",
        }
        for dtype in types:
            if dtype in self.item.get('name'):
                return types[dtype]

    def generateBoxPages(self, boxnames):
        for boxname in boxnames:
            #print(boxname)
            box = self.itemroot.find(".//item[@name='%s']"%boxname)
            boxId = box.get('key')
            self.LIbox(box)

    def makeTitlePage(self, boxname):
        output = ""
        output = output + self.itemTooltip()
        output = output + self.itemInfo(boxname)
        output = output + self.statInfo()
        if output != "":
            dest = self.directory + boxname + " Content/"
            if not os.path.isdir(dest):
                os.makedirs(dest)
            f = open(dest+self.item.get('name'), "w")
            f.write(output)
            f.close()

    def LIboxContent(self, box):
        boxId = box.get('key')
        container = self.containerroot.find(".//container[@id='%s']"%boxId)
        trophyListId = container.get('trophyListId')
        trophyList = self.lootroot.find(".//trophyList[@id='%s']"%trophyListId)
        trophies =  trophyList.findall(".//trophyListEntry")
        content = ""
        for trophy in trophies:
            #print(trophy.get('name'))
            content = content + "\n* {{Reward|"+trophy.get('name')+"}}"
            self.setTitleName(trophy.get('name'))
            self.makeTitlePage(box.get('name'))
        return len(trophies), content


    def LIbox(self, item):
        quality = item.get('quality').capitalize()
        if quality == 'Legendary':
            quality = 'Epic'
        contains, content = self.LIboxContent(item)
        output = """ <onlyinclude>{{Item Tooltip
| mode            = {{{mode|}}}
| arg             = {{{arg|}}}
| amount          = {{{amount|}}}
| name            = """+item.get('name')+"""
| icon            = Box 11 (store)-icon
| disambigpage    = Item:"""+item.get('name')+"""
| quality         = """+quality+"""
| item_level      = 1
| containsitems   = """+str(contains)+"""
| bind            = """+lf.getBinding(item.get('binding'))+"""
| cooldown        = 5s
| level           = 105
| flavor          = """+item.get('description')+"""
}}</onlyinclude>__NOTOC__

== Item Information ==
This box is a possible drop in the [[The Fall of Khazad-dûm]] raid.

Opening this box allows you to choose one of the following:
""" + content
        f = open(self.directory+item.get('name'), "w")
        f.write(output)
        f.close()

if __name__ == "__main__":
    factory = Titles.getInstance()
    boxes = [
        "Fall of Khazad-dûm Box of Avoidance Legendary Item Titles",
        "Fall of Khazad-dûm Box of Defensive Legendary Item Titles",
        "Fall of Khazad-dûm Box of Offensive Legendary Item Titles",
        "Fall of Khazad-dûm Box of Primary Legendary Item Titles",
        "Fall of Khazad-dûm Box of Skillful Legendary Item Titles",
    ]
    factory.generateBoxPages(boxes)
