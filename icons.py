#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# (C) Drono, 2019
#
import pywikibot
from pywikibot import pagegenerators
import cv2
import os
import numpy as np

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

def main():
    site = pywikibot.Site()
    cat = pywikibot.Category(site,'War-steed Skill Icons')
    gen = pagegenerators.CategorizedPageGenerator(cat, recurse=True)
    count = 0
    bg_image = np.zeros((300,300,3), np.uint8)
    bg_image[50:100,:] = (255,255,255)
    bg_image[200:300,:] = (255,255,255)
    for page in gen:
        filename = page.title(underscore=True, with_ns=False)
        page = pywikibot.FilePage(page)
        page.download()
        img = cv2.imread(filename, cv2.IMREAD_UNCHANGED)
        w,h,channels = img.shape
#        if channels == 4:
#            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)
        if w != 32 or h != 32 :
            os.remove(filename)
            continue
        rgba = cv2.cvtColor(img, cv2.COLOR_RGB2RGBA)
        img = rgba.copy()
        rgba[0,0] = (255, 255, 255, 0)
        rgba[1,0] = (255, 255, 255, 0)
        rgba[0,1] = (255, 255, 255, 0)
        rgba[0,31] = (255, 255, 255, 0)
        rgba[1,31] = (255, 255, 255, 0)
        rgba[0,30] = (255, 255, 255, 0)
        rgba[31,0] = (255, 255, 255, 0)
        rgba[30,0] = (255, 255, 255, 0)
        rgba[31,1] = (255, 255, 255, 0)
        rgba[31,31] = (255, 255, 255, 0)
        rgba[30,31] = (255, 255, 255, 0)
        rgba[31,30] = (255, 255, 255, 0)
        img_show = bg_image.copy()
        img_show = tOverlay(img_show,img,(9,9))
        img_show = tOverlay(img_show,rgba,(59,9))
        img_show = tOverlay(img_show,img,(9,59))
        img_show = tOverlay(img_show,rgba,(59,59))
        img1 = cv2.resize(img, (0,0), fx=2, fy=2)
        rgba1 = cv2.resize(rgba, (0,0), fx=2, fy=2)
        img_show = tOverlay(img_show,img1,(118,118))
        img_show = tOverlay(img_show,rgba1,(218,118))
        img_show = tOverlay(img_show,img1,(118,218))
        img_show = tOverlay(img_show,rgba1,(218,218))
        while(1):
            cv2.imshow(filename,img_show)
            k = cv2.waitKey(0)
            k = chr(k & 255)
            if k == -1:
                continue
            elif k == 'c':
                cv2.imwrite(filename,rgba)
                result = page.upload(source=filename, ignore_warnings="exists",comment="Drono-bot uploaded a version without corners.")
                if result:
                    pywikibot.output("File "+filename+" uploaded seccesfuly")
                    count += 1
                else:
                    pywikibot.output("Error uploading "+filename)
                break
            else:
                print('Skipping image '+filename)
                break
        os.remove(filename)
        cv2.destroyAllWindows()
    print(count)
if __name__ == '__main__':
    main()
