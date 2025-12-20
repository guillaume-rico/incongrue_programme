#!/usr/bin/env python
# coding=utf-8
# python "C:\SLF\Perso\Tiers Lieu\programme\incongrue_programme\incongrue_download_programme\incongrue_download_programme.py" --nom_fichier_entree C:\AM\liste_evenement.txt --option_download monthevt
"""
Test elements extra logic from svg xml lxml custom classes.
"""

import inkex
import requests
import html 
import datetime 
import locale
import argparse

locale.setlocale(
    category=locale.LC_ALL,
    locale=""
)

pars = argparse.ArgumentParser()
pars.add_argument("--nom_fichier_entree", type=str, default="")
pars.add_argument("--option_download", type=str, default="")
args, unknown = pars.parse_known_args()

fileName = args.nom_fichier_entree
f = open(fileName,"w+")
f.write("date;heure;titre;soustitre\n")

anneeActuelle = datetime.datetime.today().year
dateMin = datetime.datetime.today()
dateMax = datetime.datetime.today() + datetime.timedelta(days=1 * 365/12)

# Si l'utilisateur sélectionne le mois prochain :
if args.option_download == "monthevt" :
    dateMin = datetime.datetime.today() + datetime.timedelta(days=1 * 365/12) 
    dateMin = dateMin.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    dateMax = datetime.datetime.today() + datetime.timedelta(days=2 * 365/12) 
    dateMax = dateMax.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

listeMois = []

dateDepasse = 0
nbElement = 0

for numPage in range(1, 10):
    url = "https://lincongrue.fr/events/liste/page/" + str(numPage) + "/"
    r = requests.get(url)
    nl = 0
    for line in r.text.split("\n") :
        if "tribe-event-date-start" in line :
        
            # print("Ligne : " + line)
            # Deux cas, soit c'est un évenement sur plusieurs jours soit sur un nombre d'heure
            event = {}
            event["date"] = ""
            event["heure"] = ""
            event["titre"] = ""
            if "tribe-event-time" in line :
                # Evenement sur quelques heures 
                cleanLine = line.replace('<span class="tribe-event-date-start">',"").replace('<span class="tribe-event-time">',"").replace('</span>',"").replace('</time>',"").strip()
                cleanLineSplit = cleanLine.split(" ")
                
                jourEvenement = datetime.datetime.strptime(cleanLineSplit[0] + " " + cleanLineSplit[1] + " " + cleanLineSplit[2],'%d %B %Y')
                jourTemp = jourEvenement.strftime('%A')
                jour = jourTemp[0].upper() + jourTemp[1:]
                event["dateHard"] = jourEvenement
                event["date"] = jour + " " + jourEvenement.strftime('%d').lstrip("0")
                
                heureDepSplit = cleanLineSplit[4].split(":")
                heureFinSplit = cleanLineSplit[6].split(":")
                heuredepart = heureDepSplit[0]
                minutedepart = heureDepSplit[1]
                heurefin = heureFinSplit[0]
                minutefin = heureFinSplit[1]
                if minutedepart == "00" :
                    minutedepart = ""
                if minutefin == "00" :
                    minutefin = ""
                
                event["heure"] = heuredepart + "h" + minutedepart + "-" + heurefin + "h" + minutefin
                event["titre"] = ""
            else :
                # Evenement sur plusieurs jours
                cleanLine = line.replace('<span class="tribe-event-date-start">',"").replace('<span class="tribe-event-date-end">',"").replace('</span>',"").replace('</time>',"").strip()
                cleanLineSplit = cleanLine.split(" ")
                jourEvenement = datetime.datetime.strptime(cleanLineSplit[0] + " " + cleanLineSplit[1] + " " + cleanLineSplit[2],'%d %B %Y')
                event["dateHard"] = jourEvenement
                event["date"] = "Du " + cleanLineSplit[0] + " au " + cleanLineSplit[4] 
                
        if 'class="tribe-events-calendar-list__event-title-link tribe-common-anchor-thin"' in line :
            #print(line.replace('<span class="tribe-event-date-start">',""))
            nl = 1
        if nl >= 1 :
            nl = nl + 1
            if nl == 4 :
                event["titre"] = html.unescape(line.replace('</a>',"").replace("\xa0"," ").strip())
                #print(line.replace('</a>',"").strip())
                # print(event)
                toWrite = 0
                if args.option_download == "monthevt" :
                    if event["dateHard"] < dateMax and event["dateHard"] >= dateMin :
                        toWrite = 1
                    elif event["dateHard"] > dateMax :
                        dateDepasse = 1
                        
                if args.option_download == "20evt" :
                    toWrite = 1
                
                if toWrite == 1 :
                    # On retire les événements récurants :
                    if "atelier couture" not in event["titre"].lower() and \
                        "aide au numérique" not in event["titre"].lower() and \
                        "course à pied" not in event["titre"].lower() :
                        f.write(event["date"] + ";" + event["heure"] + ";" + event["titre"] + ";\n")
                        nbElement = nbElement + 1
    if args.option_download == "20evt" and nbElement >= 20 :
        break
    if dateDepasse == 1 :
        print("Date depasse")
        break

# On ajoute les champs a changer
f.write("\nChamps a changer dans le document :\n")
f.write("champs;valeur\n")
if args.option_download != "monthevt"  :
    f.write("<dateprogramme>;" + ' et '.join(listeMois).upper() + "\n")
else : 
    # On indique le nom du mois suivant avec la premiere lettre en majuscule
    f.write("<dateprogramme>;" + dateMin.strftime('%B')[0].upper() + dateMin.strftime('%B')[1:] + "\n")


f.close()

