#!/usr/bin/env python
# coding=utf-8
# python "C:\SLF\Perso\Tiers Lieu\programme\template_effect\getEvent.py"
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
    dateMin = dateMin.replace(day=1)
    dateMax = datetime.datetime.today() + datetime.timedelta(days=2 * 365/12) 
    dateMax = dateMax.replace(day=1)

listeMois = []

dateDepasse = 0
nbElement = 0

for numPage in range(1, 10):
    url = "https://lincongrue.fr/events/liste/page/" + str(numPage) + "/"
    r = requests.get(url)
    nl = 0
    for line in r.text.split("\n") :
        if "tribe-event-date-start" in line :
            cleanLine = line.replace('<span class="tribe-event-date-start">',"").replace('</span> à <span class="tribe-event-time">',"-").strip()
            event = {}
            jourEvenement = datetime.datetime.strptime(cleanLine[0:5] + ' ' + str(anneeActuelle),'%d %m %Y')
            jourTemp = jourEvenement.strftime('%A')
            jour = jourTemp[0].upper() + jourTemp[1:]
            event["dateHard"] = jourEvenement
            event["date"] = jour + " " + datetime.datetime.strptime(cleanLine[0:5] + ' ' + str(anneeActuelle),'%d %m %Y').strftime('%d').lstrip("0")
            event["heure"] = ""
            event["titre"] = ""
            if "de" in cleanLine[0:20] :
                #18h00-21h00
                heuredepart = cleanLine[9:11]
                minutedepart = cleanLine[12:14]
                heurefin = cleanLine[15:17]
                minutefin = cleanLine[18:20]
                if minutedepart == "00" :
                    minutedepart = ""
                if minutefin == "00" :
                    minutefin = ""
                event["heure"] = heuredepart + "h" + minutedepart + "-" + heurefin + "h" + minutefin
            else : 
                tclean = cleanLine.replace('</span> à <span class="tribe-event-date-end">'," ")
                event["date"] = "Du " + tclean[0:2] + " au " + tclean[6:8]
                
            nomMois = datetime.datetime.strptime(cleanLine[0:5] + ' ' + str(anneeActuelle),'%d %m %Y').strftime('%B')
            print(nomMois)
            if nomMois not in listeMois :
                if listeMois != [] :
                    f.write(nomMois + ";;;\n")
                listeMois.append(nomMois)
                
        if 'class="tribe-events-calendar-list__event-title-link tribe-common-anchor-thin"' in line :
            #print(line.replace('<span class="tribe-event-date-start">',""))
            nl = 1
        if nl >= 1 :
            nl = nl + 1
            if nl == 4 :
                event["titre"] = html.unescape(line.replace('</a>',"").replace("\xa0"," ").strip())
                #print(line.replace('</a>',"").strip())
                print(event)
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
                    if "Atelier Couture et/ou Tricot" not in event["titre"] and \
                        "aide au numérique" not in event["titre"] and \
                        "Courses à pied" not in event["titre"] :
                        f.write(event["date"] + ";" + event["heure"] + ";" + event["titre"] + ";\n")
                        nbElement = nbElement + 1
    if args.option_download == "20evt" and nbElement >= 20 :
        break
    if dateDepasse == 1 :
        break

# On ajoute les champs a changer
f.write("\nChamps a changer dans le document :\n")
f.write("champs;valeur\n")
f.write("<dateprogramme>;" + ' et '.join(listeMois).upper() + "\n")

f.close()

