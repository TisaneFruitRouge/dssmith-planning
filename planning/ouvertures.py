# -*- coding: utf-8 -*-

from openpyxl import *
import json

debut_lundi    = ["Lundi","F"] # colonne du tableau excel sur laquelle débute chaque jour
debut_mardi    = ["Mardi","I"]
debut_mercredi = ["Mercredi","L"]
debut_jeudi    = ["Jeudi","O"]
debut_vendredi = ["Vendredi","R"]

liste_machine_a_ne_pas_considerer = ["contremaitre","manutention","préparateur","centre-pose","presse à balle"]

liste_jours = [debut_lundi, debut_mardi, debut_mercredi, debut_jeudi, debut_vendredi]

CHEMIN_OUVERTURES = "/transfert/ouvertures.xlsx"

def get_ouvertures(semaine, annee, chemin_ouvertures=CHEMIN_OUVERTURES):
	'''
		Cette fonction renvoie un dictionnaire des ouverture pour un semaine et année données en
		entrée 
	'''
	ouvertures = load_workbook(chemin_ouvertures)

	if (int(semaine) < 10):
		semaine = f"0{semaine}" # si semaine = "9" alors on transforme semaine en "09"

	titre_feuille = f"SEM {semaine}-{annee}"

	recap = None

	for ws in ouvertures.worksheets:
		if ws.title == titre_feuille: 
			recap = ws
			break

	ouvertures_dict = dict() # dictionnaire contenant les ouvertures

	for jour in liste_jours:

		ouvertures_dict[jour[0]] = [0,0,0]

		for i in range(3):
			ouvertures_dict[jour[0]][i] = dict()
			for j in range(1, 26):

				case = str(chr(ord(jour[1])+i) + str(j+3)) # On détermine ici la case que l'on veut vérifier
				valeur = recap[case].value

				if (valeur == 1 or valeur == "arrêt maint" or valeur == "arrêt nett"): # Dans le cas ou la machine est ouverte
					nom_de_la_machine = recap["A"+str(j+3)].value.lower(  )

					if (nom_de_la_machine not in liste_machine_a_ne_pas_considerer):
						ouvertures_dict[jour[0]][i][nom_de_la_machine] = "1"

						
			ouvertures_dict[jour[0]][i]["presse à balle"] = "1"
			ouvertures_dict[jour[0]][i]["centre-pose"] = "1"
			ouvertures_dict[jour[0]][i]["préparateur"] = "1"
			ouvertures_dict[jour[0]][i]["manutention lourd"] = "1"
			ouvertures_dict[jour[0]][i]["manutention intégré"] = "1"
				
	return ouvertures_dict


if __name__ == "__main__":

	ouv = get_ouvertures(1, 2021)
	print(ouv)
