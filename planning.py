# -*- coding: utf-8 -*-


from conges import *
from competences import *
from ouvertures import *
import json
chemin_ouverture = "../DOCS STAGE/nvx/ouvertures.xlsx"

def get_liste_employes_machine(employes, machine):
	l = []
	for e in employes:
		if e.possede_competence_machine(machine):
			l.append(e)

	return l

def classe_liste_employes(liste_employes):

	l_1 = []
	l_2 = []
	l_3 = []
	for e in liste_employes:
		if e[1] == 1:
			l_1.append(e, 1)
		elif e[1] == 2:
			l_2.append(e, 2)
		elif e[1] == 3:
			l_3.append(e, 3)

	return l_3+l_2+l_1

def get_classement_ouvriers(employes: list, ouvertures: dict):

	classement_poste_ouvrier = dict()

	for machine in getkeys(ouvertures):

		classement_poste_ouvrier[machine] = [list(), list(), list()]

		employes_machine = get_liste_employes_machine(employes, machine)

		for e in employes_machine:

			competences = e.get_competences_machine(machine)
			for competence in competences:
				if (competence[1] == 0):
					classement_poste_ouvrier[machine][0].append((e, competence[2]))
				if (competence[1] == 1):
					classement_poste_ouvrier[machine][1].append((e, competence[2]))
				if (competence[1] == 2):
					classement_poste_ouvrier[machine][2].append((e, competence[2]))

		while [] in classement_poste_ouvrier[machine]: classement_poste_ouvrier[machine].remove([])
	
	return classement_poste_ouvrier

def remplir_poste(classement_ouvrier: dict, machine: str, poste: int):
	# 0 = conducteur
	# 1 = sous-conducteur
	# 2 = autre
	if (classement_ouvrier[machine][poste] == []): return None

	i = 0
	employe = classement_ouvrier[machine][poste][i] # employe = (<Object Employe>, competence: int)
	while not employe[0].est_disponible and i<len(classement_ouvrier[machine][poste]):
		i+=1
		employe = classement_ouvrier[machine][poste][i]
	employe[0].est_disponible = False
	employe[0].poste_occupe = (machine, poste)

	return (poste, employe[0].nom)

def trouver_remplaçant(employe, liste_employes_disponibles: list):

	for e in liste_employes_disponibles:
		
		machine = employe[0].poste_occupe[0]
		poste = employe[0].poste_occupe[1]

		if not e.possede_competence_machine(machine):
			continue
		else :
			competences = e.get_competences_machine(machine)
			for competence in competences:
				if poste == competence[1]:
				 	return e

	return None

def planning_periode(employes: list, ouvertures: dict):

	planning = {}

	classement_poste_ouvrier = get_classement_ouvriers(employes, ouvertures)	
	# print(classement_poste_ouvrier)

	for machine in getkeys(ouvertures):

		planning[machine] = [None, None, None] # on essaye de remplir chaque poste de la machine
		try: 
			planning[machine][0] = remplir_poste(classement_poste_ouvrier, machine, 0)
		except: 
			pass
		try: 
			planning[machine][1] = remplir_poste(classement_poste_ouvrier, machine, 1)
		except: 
			pass
		try: 
			planning[machine][2] = remplir_poste(classement_poste_ouvrier, machine, 2)
		except: 
			pass


	liste_employes_disponibles = []

	for e in employes:
		if e.est_disponible:
			liste_employes_disponibles.append(e)

	for machine in getkeys(ouvertures):
		for poste in range(2):
			if planning[machine][poste] == None:
				classement_machine = classement_poste_ouvrier[machine]
				if classement_machine == [] : continue
				else :
					if poste==1 and len(classement_machine) == 1:
						continue 
					else :
						classement = classement_poste_ouvrier[machine][poste]

				remplaçant = None

				for e in classement :

					remplaçant = trouver_remplaçant(e, liste_employes_disponibles)
					if not remplaçant==None: 
						
						liste_employes_disponibles.remove(remplaçant)

						ancienne_machine = e[0].poste_occupe[0]
						ancien_poste     = e[0].poste_occupe[1]

						remplaçant.poste_occupe = (ancienne_machine, ancien_poste)
						planning[ancienne_machine][ancien_poste] = (remplaçant.nom, ancien_poste)

						print(ancienne_machine)
						print(ancien_poste)
						print(remplaçant)

						e[0].poste_occupe = (machine, poste)	
						planning[machine][poste] = (e[0].nom, poste)



	return planning


def get_planning(jour: int, mois: int, annee: int, journee: str, matin: str, aprem: str, nuit: str):

	employes     = new_get_competences("Matrice de polyvalence1.xlsx") # on créer la liste des employés
	liste_conges = conges(jour, mois, annee) # on créer la liste des congés
	ouvertures   = get_ouvertures(chemin_ouverture) # on créer la liste des onvertures


	EQUIPE_MATIN = matin # on assigne à chaque période la bonne équipe
	EQUIPE_APREM = aprem
	EQUIPE_NUIT  = nuit

	employes_matin = list() # liste des employes présents le matin
	employes_aprem = list() # liste des employes présents l'apres-midi
	employes_nuit  = list() # liste des employes présents le soir

	for employe in employes:
		if (employe.nom in liste_conges):
			employes.remove(employe)
		elif (employe.equipe==EQUIPE_MATIN):
			employes_matin.append(employe)
		elif (employe.equipe==EQUIPE_APREM):
			employes_aprem.append(employe)
		elif (employe.equipe==EQUIPE_NUIT):
			employes_nuit.append(employe)

	ouvertures_jour = ouvertures[journee] # ouvertures pour la journée
		
	print(ouvertures_jour)

	planning = [] # planning (liste contenant le planning pour chaque période)

	planning.append(planning_periode(employes_matin, ouvertures_jour[0]))
	planning.append(planning_periode(employes_aprem, ouvertures_jour[1]))
	planning.append(planning_periode(employes_nuit, ouvertures_jour[2]))

	i = 0

	for e in employes_nuit+employes_matin+employes_aprem:
		if e.est_disponible: i+=1

	print(i)

	return planning


if __name__ == "__main__":
	planning = get_planning(1,2,2021, "Lundi", "ROUGE", "VERTE", "BLEUE")
	print(planning)