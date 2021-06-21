from datetime import date
from calendar import monthrange
from openpyxl import *
import json

date_courante = date.today()

annee_courante = date_courante.year
mois_courant = date_courante.month
jour_courant = date_courante.day



def conges(annee: int=annee_courante, mois: int=mois_courant, jour: int=jour_courant):
	
	# à terme, ouvrir la bonne page excle en fonciton de la date donnée en argument

	conges = load_workbook("../DOCS STAGE/nvx/CongВs 02 21 au 05 21.xlsx")
	ws = conges.worksheets[0]
	
	dic_conges = dict()

	# nb_jours = monthrange(annee, mois)
	nb_jours = monthrange(2021, 2)[1]

	nb_ligne = ws.max_row
	print(nb_ligne)
	for i in range(8, nb_ligne):
		nom = ws.cell(column=2, row=i).value
		
		if nom == None: 
			continue
		
		liste_conges = []

		for j in range(3, 3+nb_jours): # a changer
			cellule = ws.cell(column=j, row=i).value
			if (cellule != None):
				liste_conges.append((f"{j-2}/{2}/{2021}", cellule)) # a changer

		if (liste_conges != []):
			dic_conges[nom] = liste_conges

	return json.dumps(dic_conges)

print(conges())