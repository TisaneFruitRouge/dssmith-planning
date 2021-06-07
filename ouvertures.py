from openpyxl import *
import json

debut_lundi    = ["Lundi","F"]
debut_mardi    = ["Mardi","I"]
debut_mercredi = ["Mercredi","L"]
debut_jeudi    = ["Jeudi","O"]
debut_vendredi = ["Vendredi","R"]

liste_machine_a_ne_pas_considerer = ["contremaitre","manutention","préparateur","centre-pose","presse à balle"]

liste_jours = [debut_lundi, debut_mardi, debut_mercredi, debut_jeudi, debut_vendredi]

ouvertures = load_workbook("../DOCS STAGE/nvx/ouvertures.xlsx")

recap = ouvertures.worksheets[0]

ouvertures_dict = dict() # dictionnaire contenant les ouvertures

for jour in liste_jours:

	ouvertures_dict[jour[0]] = [0,0,0]

	for i in range(3):
		ouvertures_dict[jour[0]][i] = dict()
		for j in range(1, 26):

			case = str(chr(ord(jour[1])+i) + str(j+3)) # On détermine ici la case que l'on veut vérifier
			valeur = recap[case].value

			if (valeur == 1): # Dans le cas ou la machine est ouverte
				nom_de_la_machine = recap["A"+str(j+3)].value

				if (nom_de_la_machine not in liste_machine_a_ne_pas_considerer):
					ouvertures_dict[jour[0]][i][nom_de_la_machine] = "1"


final_dict = json.dumps(ouvertures_dict, sort_keys=False, indent=4)

print(final_dict)