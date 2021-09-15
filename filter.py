#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# (C) Drono, 2020
#
from lxml import etree
import xml.etree.ElementTree as ET

name = [
    "Secret Seeker's",
]

blacklist = [
    'zzzzz'
]

def main():
    root = ET.parse("../data/lotro-items-db/items.xml").getroot()
    f = open("../filtered.xml", "w")
    f.write("<items>")
    for item in root.iter('item'):
        skip = False
        for b in blacklist:
            if b in item.get('name'):
                skip = True
        if skip:
            continue
        for n in name:
            if n in item.get('name'):
                f.write(ET.tostring(item).decode())
    f.write("</items>")
    f.close()
    return

if __name__ == "__main__":
    main()
