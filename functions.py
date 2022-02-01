#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# (C) Drono, 2021
#


# Function for proper formating of stat numbers, stats in comma list use
# comma, to separate tousands
def formatStatNumber(stat, number):
    comma = ["ARMOUR", "AGILITY", "FATE", "MIGHT", "VITALITY", "WILL"]
    percent = ["TACTICAL_CRITICAL_MULTIPLIER"]
    if stat in percent:
        number = float(number) / 100
        number = round(number)
        return f'{number:,.1f}'
    number = int(number) / 100
    if stat in comma:
        return f'{number:,.0f}'
    else:
        return f'{number:.0f}'


# Function to convert binding string to wiki abbreviation
def getBinding(string):
    binding = {
        "BOUND_TO_ACCOUNT_ON_ACQUIRE" : "BtAoA",
        "BIND_ON_ACQUIRE" : "BoA",
        "BIND_ON_EQUIP" : "BoE",
    }
    if string in binding:
        return binding[string]
    else:
        if not string is None:
            print("'"+string+"' not found in binding table.")
        return string


# Function to convert stat string to format used on wiki
def getStatString(stat):
    stats = {
        "CRITICAL_RATING" : "Critical Rating",
        "BLOCK" : "Block Rating",
        "PARRY" : "Parry Rating",
        "EVADE" : "Evade Rating",
        "FINESSE" : "Finesse Rating",
        "TACTICAL_MITIGATION" : "Tactical Mitigation",
        "PHYSICAL_MITIGATION" : "Physical Mitigation",
        "RESISTANCE" : "Resistance Rating",
        "CRITICAL_DEFENCE" : "Critical Defence",
        "AGILITY" : "Agility",
        "FATE" : "Fate",
        "MIGHT" : "Might",
        "VITALITY" : "Vitality",
        "WILL" : "Will",
        "MORALE" : "Maximum Morale",
        "POWER" : "Maximum Power",
        "PHYSICAL_MASTERY" : "Physical Mastery Rating",
        "TACTICAL_MASTERY" : "Tactical Mastery Rating",
        "OUTGOING_HEALING" : "Outgoing Healing Rating",
        "INCOMING_HEALING" : "Incoming Healing Rating",
        "OCMR" : "non-Combat Morale Regen",
        "ICPR" : "in-Combat Power Regen ",
        "Combat_TacticalHPS_Modifier" : "Tactical Healing Rating",
        "Combat_TacticalDPS_Modifier" : "Tactical Damage Rating",
        "Combat_Damage_Mod" : "Base Combat Damage Modifier",
        "TACTICAL_CRITICAL_MULTIPLIER" : "% Tactical Critical Multiplier",
        "Combat_SkillDamageMultiplier_Fire" : "% Fire-type Damage",
        "Combat_SkillDamageMultiplier_Light" : "% Light-type Damage",
        "Combat_SkillDamageMultiplier_Frost" : "% Frost-type Damage",
        "Combat_SkillDamageMultiplier_Lightning" : "% Lightning-type Damage",
    }
    if stat in stats:
        return stats[stat]
    else:
        #print("'"+stat+"' not found in stats table.")
        return None


# Function that reads comma separated file and loads it into dictionary
# file format line example:
# 1092525606-1090519044.png, Light Leggings 52
def getIconDict(f):
    f = open(f, "r")
    iconDict = dict()
    for line in f:
        if line.strip() == "":
            continue
        icon = line.strip().split(",")
        iconDict[icon[0][:-4]] = icon[1].strip()
    return iconDict


# Function to get full icon name as in use on wiki
def getIconName(iconDict, iconId):
    """
    iconQuality = {
        "43" : "rare",
        "44" : "incomparable",
        "45" : "epic",
    }
    q = iconId[-2:-1]
    if q in iconQuality:
        q = iconQuality[q]
        for k,v in iconQuality.items():
            tempId = iconId[:-1]+k
            if tempId in iconDict:
                iconName = iconDict[tempId]
                if '*' in iconName:
                    return iconName[:-2]+" ("+q+" "+iconName[-1]+")-icon"
                else:
                    return iconName + " (" + q + ")-icon"
    """
    if iconId in iconDict:
        iconName = iconDict[iconId]
        iconName = iconName.replace('_',' ')
        if iconName[-4:] == '.png':
            iconName = iconName[:-4]
        if iconName[-5:] != '-icon':
            iconName = iconName+'-icon'
        return iconName
    return None


# Function to add parameter to a template
# name - name of the parameter
# value - value of the parameter
# width - optional, will add space up to the width so that '=' are alligned
#         in same column in the reselting template, default = 16
def addParam(name, value, width = 16):
    if value != None and value != "":
        return "\n| " + name.ljust(width) + "= " + value
    else:
        return ""
