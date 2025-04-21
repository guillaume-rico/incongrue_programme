#!/usr/bin/env python
# coding=utf-8
#
# Copyright (C) [YEAR] [YOUR NAME], [YOUR EMAIL]
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
"""
Description of this extension
"""

import inkex

class changeInlineTextBalise(inkex.EffectExtension):

    listeEvenement = []
    listeMotsCles = {}
            
    def add_arguments(self, pars):
        pars.add_argument("--nom_fichier_entree", type=str, default="")
        pars.add_argument("--couleur_fond", type=str, default="")

    def effect(self):
        # On ajoute le programme 
        # On analyse le fichier d'entrée
        f = open(self.options.nom_fichier_entree,"r+")
        inAgenda = 1
        for line in f: 
            # Si ce n'est pas le header
            if "date;heure;titre;soustitre" not in line and inAgenda == 1 and line != "":
                if len(line.split(";")) > 3 :
                    eventTemp = {}
                    eventTemp["date"] = line.split(";")[0]
                    eventTemp["heure"] = line.split(";")[1]
                    eventTemp["titre"] = line.split(";")[2]
                    eventTemp["soustitre"] = line.split(";")[3]
                    self.listeEvenement.append(eventTemp)
            if line.strip() == "" : 
                inAgenda = 0
            if inAgenda == 0 :
                if line != "" and "Champs a changer dans le document" not in line and "champs;valeur" not in line :
                    if len(line.split(";")) > 1 :
                        self.listeMotsCles[line.split(";")[0]] = line.split(";")[1]
        f.close()
        # On ajoute les éléments du calendrier
        layer = self.svg.add(inkex.Group.new('my_label', is_layer=True))
        offsetY = 600 / len(self.listeEvenement)
        yDate = 25
        yHeure = yDate + 12
        numElem = 0
        for elem in self.listeEvenement :
            if elem["date"] != "" :
                layer.append(self.add_texte(elem["date"], 430, yDate + offsetY * numElem, "large", 9))
            if elem["heure"] != "" :
                layer.append(self.add_texte(elem["heure"], 430, yHeure + offsetY * numElem, "normal", 9))                    
            if len(elem["titre"]) <= 35 :
                layer.append(self.add_texte(elem["titre"], 520, yDate + offsetY * numElem, "large", 33))
            else :
                # On cherche quand séparer le texte
                for numCar in range (35, 0, -1) :
                    if elem["titre"][numCar] == " " :
                        break
                layer.append(self.add_texte(elem["titre"][0:numCar], 540, yDate + offsetY * numElem, "large", 33))
                layer.append(self.add_texte(elem["titre"][numCar:], 540, yDate + 12 + offsetY * numElem, "large", 33))
            # On ajoute le sous titre 
            if elem["soustitre"] != "" :
                layer.append(self.add_texte(elem["soustitre"], 540, yHeure + offsetY * numElem, "normal", 33))
            # Si l'heure est vide, on se décale pour les suivants
            if elem["heure"] == "" :
                yHeure = yHeure - offsetY/2
                yDate = yDate - offsetY/2
            # On ajoute une ligne entre deux éléments
            pel = inkex.PathElement.new(path="m 410,0 L 760,0")
            pel.style = {
                "stroke" : '#000000',
                "stroke-width" : "0.2",
                "fill" : 'none',
            }
            pel.transform = inkex.Transform('translate(0, ' + str(yDate + 17 + offsetY * numElem) + ')')
            layer.append(pel)
            
            numElem = numElem + 1
            
        # On change le texte 
        # On se ballade sur tous les élments text
        for node in self.svg.xpath("//svg:text") :
            # Le texte est dans tspan 
            for item in node.xpath('./*') :
                for texteARemplacer in self.listeMotsCles :
                    if texteARemplacer in item.text :
                        item.text = self.listeMotsCles[texteARemplacer]
                        inkex.utils.debug(str(item.text))
                    
        # Changement de l couleur du fond 
        fond = "#f4900c"
        rayure = "#75924b"
        if self.options.couleur_fond == "f4900c" :
            fond = "#f4900c"
            rayure = "#75924b"
        elif self.options.couleur_fond == "456db8" :
            fond = "#456db8"
            rayure = "#f4900c"
        elif self.options.couleur_fond == "75924b" :
            fond = "#75924b"
            rayure = "#95bed5"
        self.svg.getElementById("path21430").style.set_color(fond, 'fill')
        self.svg.getElementById("path40836").style.set_color(fond, 'fill')
        self.svg.getElementById("path21434").style.set_color(rayure, 'fill')
        self.svg.getElementById("path21434-8").style.set_color(rayure, 'fill')
        self.svg.getElementById("path21434-8-3").style.set_color(rayure, 'fill')

    def add_texte(self, texte, x , y, size, nbcarmax):
        # On crée l'lément texte
        my_text = inkex.TextElement(x=str(0), y=str(0))
        # En fonction de size :
        policeweight = "bold"
        policesize = "9"
        multiplier = 3
        if size == "normal" :
            policeweight = "normal"
            policesize = "8"
            multiplier = 2
            
        my_text.text = str(texte)
        my_text.style = {
            "font-size": self.svg.unittouu(policesize + 'pt'),
            "font-style" : "normal",
            "font-variant" : "normal",
            "font-weight" : policeweight,
            "font-stretch" : "normal",
            "font-family" : 'Open Sans',
            "fill" : '#000000',
            "stroke" : '#000000',
            "stroke-width" : 0.0977328}
        # Décalage en fonction du nombre de lettre
        decalageX = (nbcarmax - len(texte)) * multiplier + x
        my_text.transform = inkex.Transform('translate(' + str(decalageX) + ', ' + str(y) + ')')
        return my_text

if __name__ == '__main__':
    changeInlineTextBalise().run()
