#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# (C) Drono, 2023
#
from __future__ import absolute_import
from pywikibot.page import Page
import pywikibot
from lxml import etree as ET
import os
import glob
import shutil
import math
import worth
import functions as lf
import mwparserfromhell as mwparser

itemroot = ET.parse("./data/lotro-items-db/items.xml").getroot()
statroot = ET.parse("./data/lotro-data/common/stats.xml").getroot()
localroot = ET.parse("./data/lotro-data/labels/en/items.xml").getroot()
scaleroot = ET.parse("./data/lotro-data/common/progressions.xml")
worthObject = worth.Worth.getInstance()

site = pywikibot.Site()
site.login()

def checkPageExistance(name):
    newPage = Page(site,name)
    if newPage.isRedirectPage():
        newPage = newPage.getRedirectTarget()
    try:
        oldtext = newPage.get()
        return oldtext, newPage
    except pywikibot.exceptions.NoPageError:
        print(name+" does not exists")
        return None, newPage

def getProgression(scaling, level):
    if ',' in scaling:
        ranges = scaling.split(',')
        for r in ranges:
            levels = r.split(':')[0]
            ls, le = levels.split('-')
            if le == '':
                le = 9999
            if level < int(le) and level > int(ls):
                scaling = r
    if ',' in scaling:
        return
    if ':' in scaling:
        levels, prog = scaling.split(':')
        ls, le = levels.split('-')
        if le == '':
            le = 9999
        if level < int(le) and level > int(ls):
            return prog
        else:
            return
    return scaling

def getStatValue(scaling, level):
    scaling = getProgression(scaling, level)
    if scaling is None:
        return
    elem = scaleroot.find(".//linearInterpolationProgression[@identifier='%s']"%(scaling))
    if elem is None:
        print("Didnt find linear scaling for "+scaling+". Trying array.")
        return getArrayProgression(scaling, level)
    point = elem.find(".//point[@x='%s']"%level)
    if point is not None:
        return point.get('y')
    minPoint = None
    for point in elem:
        if minPoint is None:
            minPoint = point
        if level > int(point.get('x')):
            minPoint = point
        else:
            maxPoint = point
            break
    value = float(maxPoint.get('y')) - float(minPoint.get('y'))
    value = value / (float(maxPoint.get('x')) - float(minPoint.get('x')))
    value = value * (float(level) - float(minPoint.get('x')))
    value = value + float(minPoint.get('y'))
    return value

def getArrayProgression(scaling, level):
    elem = scaleroot.find(".//arrayProgression[@identifier='%s']"%(scaling))
    if elem is None:
        print("Didnt find array scaling for "+scaling)
        return
    point = elem.find(".//point[@x='%s']"%level)
    if point is not None:
        return point.get('y')
    else:
        print("Didn't find ponint "+level+" in array "+scaling)
        return

def getAttrs(item):
    itemLevel = item.get("level")
    if itemLevel is not None:
        item = item.find('stats')
    attrs = ""
    for stat in item.findall('stat'):
        armour = ""
        attr = ""
        statName = stat.get('name')
        value = stat.get('constant')
        description = stat.get('descriptionOverride')
        if description is not None:
            if description == '-':
                continue
            elif "${PERCENTVALUE}" in description:
                description = description.replace("${PERCENTVALUE}",f'{float(value):g}'+"%")
            if "${VALUE}" in description:
                value = lf.formatStatNumber(statName, float(stat.get('value')))
                description = description.replace("${VALUE}",f'{float(value):g}')
            attrs = attrs + description + " <br> "
            continue
        statValue = "???"
        operator = stat.get('operator')
        if itemLevel is not None and statName in ['POWER']:
            statScaling = stat.get('scaling')
            if statScaling is None:
                statScaling = stat.get('ranged')
            if statScaling is not None:
                value =  getStatValue(statScaling, int(itemLevel))
        if value is not None:
            value = float(value)
            fix = ["ICPR", "ICMR", "OCPR", "OCMR"]
            if statName in fix:
                value = round((value/60)*1000+0.2)/1000
                statValue = "{:0.3f}".format(value).rstrip('0').rstrip('.')
            else:
                statValue = f'{math.floor(value):g}'
                statValue = lf.formatStatNumber(statName, value*100)
            # TODO: FIX operator
            if operator == "SUBSTRACT":
                statValue = "-"+statValue
        else:
            statValue =  lf.formatStatNumber(statName, float(stat.get('value')))
        if statValue == "0":
            continue
        if statName == "ARMOUR":
            armour = statValue
            continue
        else:
            stat = statroot.find(".//stat[@key='%s']"%(statName))
            if stat is None:
                stat = statroot.find(".//stat[@legacyKey='%s']"%(statName))
                if stat is None:
                    unknownStats.add(statName)
                    continue
            statName = stat.get('name')
            if stat.get('isPercentage') and statName != "TACTICAL_CRITICAL_MULTIPLIER":
                statName = '% '+statName
                if value is not None:
                    statValue =  lf.formatStatNumber("PERCENTAGE", float(value*100))
            space = " "
            if statName[0] == "%":
                space = ""
            if statValue[0] != "-":
                statValue = "+"+statValue
            if statName != None:
                attr = statValue + space + statName
            if statName == "AUDACITY":
                attr = "{{color|red|"+attr+"}}"
        attrs = attrs + attr + " <br> "
    return attrs[:-6]

def updateItem(item):
    itemName = item.get("name")
    itemId = item.get("key")
    disambigpage = "Item:"+itemName
    oldtext, page = checkPageExistance(disambigpage)
    if oldtext is None:
        return False
    worth_string = worthObject.getWorthString(item.get('valueTableId'),
                         item.get('level'),
                         item.get('quality'))
    wikicode = mwparser.parse(oldtext)
    templates = wikicode.filter_templates()
    beta = None
    for template in templates:
        if template.name.strip().lower() == 'beta':
            beta = template
        if template.name == 'Item Tooltip\n':
            attrs = getAttrs(item)

            if template.has("attrib"):
                attrib = template.get("attrib")
                if attrib is not None:
                    attribBlacklist = ["AEffect","Hustle","{{Color","Exploit Opening","...","On any",
                            "Echoes of Battle","On every"]
                    do = True
                    for rule in attribBlacklist:
                        if rule in attrib:
                            do = False
                    if not do:
                        return False
            if len(attrs.strip())>0:
                template.add("attrib", attrs)
            if template.has("item_id"):
                item_id = str(template.get("item_id").value).strip()
                if len(item_id)>0 and item_id != item.get("key"):
                    print(item_id+" "+itemName+" id does not match: "+itemId)
                    return False
                #if len(item_id)<1:
            else:
                template.add("item_id        ", itemId ,before="quality", preserve_spacing=True)
            if template.has("icon"):
                if item.get("class").strip()=="49":
                    template.add("icon           ", item.get("icon"))
            if len(worth_string)>0 and worth_string != "{{Worth|c=1}}":
                template.add("sell           ", worth_string)
    if beta is not None:
        wikicode.remove(beta)
    page.text = wikicode
    pywikibot.showDiff(oldtext, wikicode, context=0)
    if oldtext != wikicode:
        print(itemName)
        #page.save(summary="Drono-bot: update")
        return True
    return False

def updateItems():
    itemroot = ET.parse("./filtered.xml").getroot()
    total = len(itemroot.findall('item'))
    progress = 0
    edited = 0
    for item in itemroot.iter('item'):
        progress = progress + 1
        print("Progress "+"{:.2f}".format(progress/total*100)+"%", end='\r')
        itemName = item.get("name")
        if "\n" in itemName:
            continue
        scaledItem = item.find("./property[@key='Munging']")
        # if scaledItem is not None:
        #     continue
        result = updateItem(item)
        if result:
            edited = edited + 1
    print(edited)
    return

# TODO: WEffect - Demoralize, Armour, weaken wounding, susceptibility etc
# TODO: Greatly reduces threat during ranged combat.
# TODO: Spear dmg type
# TODO: Tactical critical multiplier 3 digit precision - Mentor's Gloves


if __name__ == "__main__":
    updateItems()
