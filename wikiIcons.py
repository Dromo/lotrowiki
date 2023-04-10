#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# (C) Drono, 2022
#
from __future__ import absolute_import
import os, sys
import glob
import hashlib
from lxml import etree as ET
import cv2
import numpy as np
import argparse
import pywikibot
from pywikibot import pagegenerators

homedir = "~"
datadir = homedir + "/pywikibot/scripts/userscripts/data/"

categories = {
    "MAIN_HAND_AURA" : "",
    "FINGER" : "Ring",
    "CHEST" : "Chest",
    "OFF_HAND" : "",
    "POCKET" : "Pocket",
    "BACK" : "Back",
    "RANGED_ITEM" : "",
    "EAR" : "Earring",
    "HEAD" : "Head",
    "WRIST" : "Bracelet",
    "LEGS" : "Legs",
    "SHOULDER" : "Shoulder",
    "CLASS_SLOT" : "",
    "FEET" : "Feet",
    "HAND" : "Gloves",
    "NECK" : "Necklace",
    "MAIN_HAND" : "",
    "OTHER" : "",
    "BRIDLE" : "",
    "TOOL" : ""
}

weaponType = {
    "BOW": "Bow",
    "CROSSBOW": "Crossbow",
    "ONE_HANDED_SWORD": "One-handed Sword",
    "ONE_HANDED_AXE": "One-handed Axe",
    "DAGGER": "Dagger",
    "ONE_HANDED_MACE": "One-handed Mace",
    "ONE_HANDED_HAMMER": "One-handed Hammer",
    "ONE_HANDED_CLUB": "One-handed Club",
    "BATTLE_GAUNTLETS": "Battle-gauntlets",
    "TWO_HANDED_AXE" : "Two-handed Axe",
    "TWO_HANDED_SWORD" : "Two-handed Sword",
    "SPEAR" : "Spear",
    "TWO_HANDED_HAMMER" : "Two-handed Hammer",
    "STAFF": "Staff",
    "TWO_HANDED_CLUB" : "Two-handed Club",
    "HALBERD" : "Halberd",
    "JAVELIN" : "Javelin",
    "RUNE_STONE" : "Rune-stone"
}

def tOverlay(src , overlay , pos=(0,0)):
    h,w,_ = overlay.shape
    rows,cols,_ = src.shape
    y,x = pos[0],pos[1]
    for i in range(h):
        for j in range(w):
            if x+i >= rows or y+j >= cols:
                continue
            alpha = float(overlay[i][j][3]/255.0)
            src[x+i][y+j] = alpha*overlay[i][j][:3]+(1-alpha)*src[x+i][y+j]
    return src

def joinDicts(dict1, dict2):
    for key in dict2.keys():
        if key in dict1:
            dict1[key] = dict1[key] + dict2[key]
        else:
            dict1[key] = dict2[key]

def hashfile(path, blocksize = 65536):
    afile = open(path, 'rb')
    hasher = hashlib.md5()
    buf = afile.read(blocksize)
    while len(buf) > 0:
        hasher.update(buf)
        buf = afile.read(blocksize)
    afile.close()
    return hasher.hexdigest()

def createIconFile():
    itypes = set()
    icons = set()
    root = ET.parse(datadir+"lotro-items-db/items.xml").getroot()
    eroot = ET.parse(datadir+"lotro-data/common/enums/EquipmentCategory.xml").getroot()
    eCats = {}
    for entry in eroot.iter('entry'):
        eCats[entry.get('code')] = entry.get('name')
    total = len(root.findall('item'))
    progress = 0
    for item in root.iter('item'):
        progress = progress + 1
        print("Progress "+"{:.2f}".format(progress/total*100)+"%", end='\r')
        icon = item.get('icon')
        icontype = item.get('slot')
        eCat = item.get('equipmentCategory')
        if eCat != None:
            eCat = int(eCat)
        if icontype == None:
            icontype = 'OTHER'
        #print(icontype)
        icontype = categories[icontype]
        itypes.add(icontype)
        if item.get('class')!= None and item.get('class').strip()=="49":
            if icon:
                icons.add(icon+', '+icontype)
        elif item.get('category').strip()=="ARMOUR":
            if icon:
                if(eCat == 17 or eCat == 11 or eCat == 40):
                    icontype = 'Shield'
                if(eCat == 18) and icontype!="Back":
                    icontype = 'Light ' + icontype
                if(eCat == 9):
                    icontype = 'Medium ' + icontype
                if(eCat == 10):
                    icontype = 'Heavy ' + icontype
                icons.add(icon+', '+icontype)
        elif item.get('category').strip()=="WEAPON":
            wType = item.get('weaponType')
            icontype = weaponType[wType]
            if(wType == "RUNE_STONE"):
                icontype = item.get('damageType').capitalize()+" "+icontype
            if icon:
                icons.add(icon+', '+icontype)
    print()
    #for itype in itypes:
    #    print(itype)
    f = open('./icons.txt','w')
    for icon in sorted(icons):
        f.write(icon+'\n')
    f.close()

def readIconFile():
    f = open('./icons.txt','r')
    idict = {}
    for line in f:
        iname, icat = line.split(',')
        idict[iname.strip()] = icat.strip()
    f.close()
    return idict

def makeIcon(icon):
    layers = icon.split('-')
    layers += [layers.pop(0)]
    if len(layers) > 3:
        layers[1],layers[2] = layers[2],layers[1]
    result = np.zeros((32,32,3), np.uint8)
    for i in range(0, len(layers)):
        filename = datadir+"lotro-icons/items/"+layers[i]+".png"
        pom = cv2.imread(filename, cv2.IMREAD_UNCHANGED)
        pom = cv2.cvtColor(pom, cv2.COLOR_RGB2RGBA)
        result = tOverlay(result,pom)
        #showImage(result)
        if len(layers) > 3:
            pom1 = np.zeros((32,32,3), np.uint8)
            #showImage(tOverlay(pom1,pom))
            pom2 = np.ones((32,32,3), np.uint8)*255
            #showImage(tOverlay(pom2,pom))
    return result

def showImage(img):
    while(1):
        cv2.imshow("img",img)
        k = cv2.waitKey(0)
        cv2.destroyAllWindows()
        k = chr(k & 255)
        if k == -1:
            contine
        elif k == 'q':
            sys.exit(0)
        else:
            break

def printMatrix(img):
    h,w,_ = img.shape
    y,x = 0,0
    for i in range(h):
        line = "("
        for j in range(w):
            line = line + str(img[i][j]) + ", "
        line = line[:-2] + ")"
        print(line)

def loadImage(path):
    pom = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    if pom is None:
        print(path+" is None")
        return
    pom = cv2.cvtColor(pom, cv2.COLOR_RGB2RGBA)
    return pom

def pixelDiff(pixel1, pixel2, tolerance=0):
    dim = len(pixel1)
    for i in range(dim):
        if abs(int(pixel1[i])-int(pixel2[i]))>tolerance:
            return False
    return True

def iconDiff(icon1, icon2, tolerance = 0):
    h,w,_ = icon1.shape
    h1,w1,_ = icon2.shape
    if h != h1 or w !=w1:
        print("Icon size does not match. "+str(h)+"x"+str(w)+" and "
            +str(h1)+"x"+str(w1))
        return
    diff = icon1.copy()
    score = 0
    for i in range(h):
        for j in range(w):
            if not pixelDiff(icon1[i][j],icon2[i][j],tolerance):
                diff[i,j] = (0, 0, 255, 255)
                #print("Icon pixel missmatch ["+str(i)+","+str(j)+"]: "+
                #    str(icon1[i][j])+" "+str(icon2[i][j]))
                score += 1
    bg = np.zeros((300,300,3), np.uint8)
    bg = tOverlay(bg,icon1,(9,9))
    bg = tOverlay(bg,icon2,(59,9))
    bg = tOverlay(bg,diff,(109,9))
    icon1 = cv2.resize(icon1, (0,0), fx=2, fy=2)
    icon2 = cv2.resize(icon2, (0,0), fx=2, fy=2)
    diff = cv2.resize(diff, (0,0), fx=2, fy=2)
    bg = tOverlay(bg,icon1,(9,118))
    bg = tOverlay(bg,icon2,(109,118))
    bg = tOverlay(bg,diff,(209,118))
    #if score > 0:
    #    showImage(bg)
    return score

class IconEditor(object):

    def __init__(self, *args):
        self.site = pywikibot.Site()
        self.edited = 0
        self.comment = "Drono-bot uploaded"


    def edit_page(self, page):
        filename = page.title(underscore=true, with_ns=false)
        try:
            page.download()
        except pywikibot.exceptions.nopageerror:
            pywikibot.output(page.title()+' does not exist.')
            return
        img = cv2.imread(filename, cv2.imread_unchanged)
        w,h,channels = img.shape
        if w != 32 or h != 32 :
            #os.remove(filename)
            pywikibot.output(page.title()+' is '+str(w)+'x'+str(h))
            #return
            img = img[:32, :32]
        rgba = cv2.cvtColor(img, cv2.COLOR_RGB2RGBA)
        img = rgba.copy()
        while(1):
            cv2.imshow(filename,img_show)
            k = cv2.waitKey(0)
            cv2.destroyAllWindows()
            k = chr(k & 255)
            if k == -1:
                continue
            elif k == 'c':
                cv2.imwrite(filename,rgba)
                result = page.upload(source=filename,
                    ignore_warnings="exists", comment=self.comment)
                if result:
                    pywikibot.output("File "+filename+" uploaded seccesfuly")
                    self.edited += 1
                else:
                    pywikibot.output("Error uploading "+filename)
                    try:
                        answer = pywikibot.input_choice(
                            "Upload if dupliciate?",
                            [('Yes', 'y'), ('No', 'n')])
                    except pywikibot.bot_choice.QuitKeyboardInterrupt:
                        break
                    if answer == 'y':
                        result = page.upload(source=filename,
                            ignore_warnings='exists,duplicate',
                            comment = self.comment)
                        self.edited += 1
                break
            elif k == 'q':
                os.remove(filename)
                pywikibot.output('Changed '+str(self.edited)+' icons.')
                sys.exit(0)
            else:
                print('Skipping image '+filename)
                break
        os.remove(filename)


    def run(self):
        self.missing = set()
        self.changed = set()
        self.site.login()
        f = open("./icons.txt",'r')
        total = 0
        with open(r"./icons.txt", 'r') as fp:
            total = len(fp.readlines())
        lin = 0
        # f = glob.glob(homedir+"/Desktop/temp/*.png")
        # total = len(f)
        typeDict = readIconFile()
        for line in sorted(f):
            lin = lin + 1
            print("Image "+str(lin)+"/"+str(total)+
                " {:.2f}".format(lin/total*100)+"%", end='\r')
            arr = line.split(',')
            iconName, iconType = arr[0].strip(), arr[1].strip()
            #iconName = line.strip()[line.find("temp/")+5:-4]
            #iconType = typeDict[iconName].strip()
            self.handleFile(iconName,iconType)
        print("Changed:")
        for icon in self.changed:
            print(icon)
        #self.edit_page(page)
        pywikibot.output('Uploaded '+str(self.edited)+' icons.')


    def handleFile(self, iconName, iconType):
        if iconType == "":
            print("Skipping "+iconName+" because Type is empty.")
            return
        iconImage = makeIcon(iconName)
        dirr = homedir+'/Desktop/temp/'
        if not os.path.isdir(dirr):
            os.mkdir(dirr)
        filename = dirr+iconName+".png"
        page = "File:"+iconName+".png"
        page = pywikibot.FilePage(self.site, page)

        cv2.imwrite(filename,iconImage)
        filename1 = page.title(underscore=True, with_ns=False)
        try:
            page.download()
        except pywikibot.exceptions.NoPageError:
            pywikibot.output(page.title()+' does not exist.')
            self.missing.add(filename)
            self.comment = "[[Category:"+iconType+" Icons]]"
            print(filename, self.comment)
            #''' Uncoment for dry run
            result = page.upload(source=filename,
                ignore_warnings="exists", comment=self.comment)
            if result:
                pywikibot.output("File "+filename+" uploaded seccesfuly")
                self.edited += 1
            else:
                pywikibot.output("Error uploading "+filename)
                try:
                    answer = pywikibot.input_choice(
                        "Upload if dupliciate?",
                        [('Yes', 'y'), ('No', 'n')])
                except pywikibot.bot_choice.QuitKeyboardInterrupt:
                    sys.exit(1)
                if answer == 'y':
                    result = page.upload(source=filename,
                        ignore_warnings='exists,duplicate',
                        comment = self.comment)
                    self.edited += 1
            #<'''
            return
        s = iconDiff(loadImage(filename),loadImage(filename1),5)
        if s > 0:
            self.changed.add(filename)
        if(filename not in self.missing):
            os.remove(filename)
        os.remove(filename1)
        #showImage(iconImage)

def makeTable():
    tableHeader = '''{| class="altRowsMed sortable"
! Icon !! Icon name !! Icon category\n'''
    f = glob.glob(homedir+"/Desktop/temp/*.png")
    output = open(homedir+"/Desktop/temp/table.txt",'w')
    typeDict = readIconFile()
    output.write(tableHeader)
    for line in sorted(f):
        iconName = line.strip()[line.find("temp/")+5:-4]
        iconType = typeDict[iconName].strip()
        row = "\n|-\n"
        output.write(row)
        row = "| [[File:"+iconName+".png]] || " +iconName+ ".png || [[:Category:" + iconType +" Icons]]"
        output.write(row)
    tableEnd = "|}\n"
    output.write(tableEnd)
    output.close()

def main(*args):
    createIconFile()
    app = IconEditor(*args)
    app.run()
    makeTable()


if __name__ == '__main__':
    main()
