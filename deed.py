#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# (C) Drono, 2021
#
from __future__ import absolute_import
from lxml import etree as ET
import os

class Deed(object):
    __instance = None

    def __init__(self):
        if Deed.__instance != None:
            raise Exception("This class is a singleton! " +
                "Use 'Deed.getInstance()'")
        else:
            Deed.__instance = self
            pathToXml = "../data/lotro-data/deeds/deeds.xml"
            pathToXml = os.path.join(os.path.dirname(__file__), pathToXml)
            self.root = ET.parse(pathToXml).getroot()
            self.deed = None

    def getInstance():
        if Deed.__instance == None:
            Deed()
        return Deed.__instance

    def setId(self, deedId):
        self.deed = self.root.find(".//deed[@id='%s']"%deedId)

    def getName(self):
        if self.deed == None:
            return ""
        else:
            return self.deed.get('name')
