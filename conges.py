# -*- coding: utf-8 -*-


from datetime import date
from calendar import monthrange
from openpyxl import *
import json

date_courante = date.today()

annee_courante = date_courante.year
mois_courant = date_courante.month
jour_courant = date_courante.day



def conges(jour: int=jour_courant, mois: int=mois_courant, annee: int=annee_courante):
	
	# à terme, ouvrir la bonne page excle en fonciton de la date donnée en argument

	conges = load_workbook(f"../DOCS STAGE/nvx/{annee}.xlsx")
	
	# ws = conges.worksheets[mois-1]
	ws = conges.worksheets[0]
	
	dic_conges = dict()

	# nb_jours = monthrange(annee, mois)
	nb_jours = monthrange(2021, 2)[1]

	nb_ligne = ws.max_row
	
	liste_conges = []

	for i in range(8, nb_ligne): #on parcours les lignes (employes)
		nom = ws.cell(column=2, row=i).value
		
		if nom == None: 
			continue
		

		cellule = ws.cell(column=2+jour, row=i).value

		if (cellule != None):
			liste_conges.append(nom)

	return liste_conges


if __name__ == "__main__":
	
	print(conges())