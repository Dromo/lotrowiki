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
            #TEMP
            pathToXml = "../data/lotro-data/quests/quests.xml"
            pathToXml = os.path.join(os.path.dirname(__file__), pathToXml)
            self.qroot = ET.parse(pathToXml).getroot()
            pathToXml = "../data/lotro-data/deeds/deeds.xml"
            pathToXml = os.path.join(os.path.dirname(__file__), pathToXml)
            self.droot = ET.parse(pathToXml).getroot()
            pathToXml = "../data/lotro-data/common/factions.xml"
            pathToXml = os.path.join(os.path.dirname(__file__), pathToXml)
            self.froot = ET.parse(pathToXml).getroot()

    def getInstance():
        if Barter.__instance == None:
            Barter()
        return Barter.__instance

    def getBarterString(self, item):
        output = ""
        rid = item.get('key')
        for elem in self.root.findall(".//receive[@id='%s']"%(rid)):
            elem = elem.getparent()
            give = elem.findall('give')
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
            givestr = ""
            for g in give:
                quantity = g.get('quantity')
                if quantity is None:
                    quantity = ""
                else:
                    quantity = "|" + quantity
                givestr = givestr + "{{Reward|" + g.get('name')
                givestr = givestr + quantity + "}}{{!!}}"
            if givestr != "":
                givestr = givestr[:-6]
            output = output + """
== Barter Information ==
{{Barterer
| npc     = [["""+barterName+"""]] """+require+"""
| columns = """+str(len(give)+1)+"""
| get1    = {{Reward|{{subst:BASEPAGENAME}}}}
| give1   = """+givestr+"""
}}
"""
        return output

    def getBartererTable(self, name):
        barterer = self.root.findall(".//barterer[@name='%s']"%(name))
        if len(barterer) > 1:
            print("Found "+lenbarter+" barterers with name "+name)
        elif len(barterer) < 1:
            print("Barterer name "+name+" not found.")
            return
        barterer = barterer[0]
        profiles = barterer.findall('barterProfile')
        result = ""
        for profile in profiles:
            result += self.getProfileTable(profile.get("profileId"))
        return result

    def getProfileTable(self, profileId):
        profile = self.root.find("./barterProfile[@profileId='%s']"%profileId)
        requiredQ = profile.get("requiredQuest")
        requiredF = profile.get("requiredFaction")
        require = ""
        if requiredQ is not None:
            requiredQ = requiredQ.split(';')[0]
            quest = self.qroot.find(".//quest[@id='%s']"%requiredQ)
            if quest is None:
                quest = self.droot.find(".//deed[@id='%s']"%requiredQ)
            require += "Require completion of "+quest.get('name')
        if requiredF is not None:
            requiredF, tier = requiredF.split(';')
            faction = self.froot.find(".//faction[@id='%s']"%requiredF)
            fname = faction.get('name')
            flevel = faction.find("./level[@tier='%s']"%tier).get('name')
            the = "" if fname[:3].lower() == "the" else "the "
            if len(require) > 0:
                require +="\n"
            require += "Require "+flevel+" standing with "+the+fname
#        print("'"+require+"'")
        tbody = ""
        for entry in profile.findall("barterEntry"):
            givemax = 0
            given = 0
            givestr = ""
            for give in entry.findall("give"):
                given += 1
                gquantity = give.get("quantity")
                gquantity = "|"+gquantity if gquantity is not None else ""
                givestr +=" || {{Reward|"+give.get("name")+gquantity+"}}"
            givemax = max(given, givemax)
            receive = entry.find("receive")
            if receive is None:
                receive = entry.find("receiveReputation")
                if receive is not None:
                    rquantity = receive.get("quantity")
                    rquantity = "|"+rquantity if rquantity is not None else ""
                    receivestr = rquantity+receive.get("factionName")
                else:
                    print(profileId+ " has unexpected entry")
                continue
            rquantity = receive.get("quantity")
            rquantity = "|"+rquantity if rquantity is not None else ""
            receivestr = "{{Reward|"+receive.get("name")+rquantity+"}}"
            pname = profile.get('name')
            if "Traceries" in pname:
                receivestr = "{{Reward|"+receive.get("name")
                quality = ["Uncommon","Rare","Legendary","Incomparable"]
                level = pname[pname.find("Lvl"):]
                level = level.split(',')[0][4:]
                level = "45" if level == "50" else level
                for q in quality:
                    if q.lower() in pname.lower():
                        receivestr += " ("+q+", Level "+level+")}}"
            rowstr = "\n|-\n| "+receivestr+givestr
            tbody += rowstr
        theader = '{| class="altRowsMed collapsible collapsed"'\
            'style="width:800px;" \n'\
            '! colspan="'+str(givemax+1)+'" style="text-align: center;" | '\
            +profile.get('name')+'\n|-'\
            '\n! style="width:40%;" | Item to Receive\n'\
            '! colspan="'+str(givemax)+'" style="width:60%;" | Items to Trade'
        return theader + tbody + "\n|}\n"

    def testRequirements(self):
        #profiles with both requiredQuest and requiredFaction
        profiles = self.root.findall("./barterProfile")
        for profile in profiles:
            if profile.get("requiredQuest") is not None:
                if profile.get("requiredFaction") is not None:
                    print(profile.get("profileId"))
        return

    def generateProfiles(self):
        barterers = self.root.findall('barterer')
        for barterer in barterers:
            profiles = barterer.findall('barterProfile')
            for profile in profiles:
                self.getProfileTable(profile.get("profileId"))

