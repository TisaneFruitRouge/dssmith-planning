# -*- coding: utf-8 -*-


from conges import *
from competences import *
from ouvertures import *

import json
import datetime

chemin_ouverture = "../DOCS STAGE/nvx/ouvertures.xlsx"

def get_liste_employes_machine(employes, machine):
	"""
		Cette fonction prend un entrée un liste d'employés et une machine et renvoie la liste des employés
		pouvant tenir un poste sur cette machine
	"""
	l = []
	for e in employes:
		if e.possede_competence_machine(machine):
			l.append(e)

	return l

def classe_liste_employes(liste_employes):
	"""
		Cette fonction renvoie une liste composée des éléments de la list donnée en entrée, mais triés en
		fonction de leur niveau de compétence
	"""
	l_1 = []
	l_2 = []
	l_3 = []
	l_4 = []
	for e in liste_employes:
		if e[1] == 1:
			l_1.append(e)
		elif e[1] == 2:
			l_2.append(e)
		elif e[1] == 3:
			l_3.append(e)
		elif e[1] == 4:
			l_4.append(e)
			 
	return l_4+l_3+l_2+l_1


def get_classement_ouvriers(employes: list, ouvertures: dict):

	"""
		Cette fonction prend en entrée la liste des emplpyés et le dictionnaire des ouvertures
		et renvoie un classement des ouvriers par poste. Ce classement est un dictionnaire où pour
		chaque machine existe une clef à laquelle est associée des liste d'employés sachant tenir les postes
		de la dite machine, triés en fonction de leur niveau de compétence au dit poste. 
	"""

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

		#while [] in classement_poste_ouvrier[machine]: classement_poste_ouvrier[machine].remove([])
		
		for i in range(len(classement_poste_ouvrier[machine])):
			classement_poste_ouvrier[machine][i] = classe_liste_employes(classement_poste_ouvrier[machine][i])	

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

	return (poste, employe[0])

def trouver_remplaçant(employe, liste_employes_disponibles: list):

	"""
		Cette fonction prend un employé en entrée ainsi que la liste des employés n'ayant pas été afféctés à 
		un poste et essaye de trouver, parmi ces employés, un pouvant remplacer l'employé donné en entrée à son poste
	"""

	remplaçant = None

	for e in liste_employes_disponibles:
		
		machine = employe[0].poste_occupe[0]
		poste = employe[0].poste_occupe[1]

		if not e.possede_competence_machine(machine):
			continue
		else :
			competences = e.get_competences_machine(machine)
			for competence in competences:
				if poste == competence[1]:
				 	remplaçant = e

	return remplaçant

def planning_periode(employes: list, ouvertures: dict, equipe: str):

	"""
		Cette fonction créer le planning en prenant en compte les ouvertures et la liste des employés disponibles
	
		NOTE : Dans l'ensemble du programme, les poste pour une machine sont représenter par une liste, ou le 
		1er élément (0) est le conducteur, le deuxiemes (1) le sous-conducteur et le 3eme (2) le dernier poste 
		(préparateur, prérégleur, etc..)

	"""

	planning = {}

	classement_poste_ouvrier = get_classement_ouvriers(employes, ouvertures)	


	for machine in getkeys(ouvertures): # On place d'abord les ouvriers sur leur poste type (4)

		planning[machine] = [None, None, None]

		for poste in range(3):

			if (classement_poste_ouvrier[machine][poste] == [] or not planning[machine][poste] == None): 
				continue
			else: 
				employe = classement_poste_ouvrier[machine][poste][0] # le premier employe est celui
																	  # occupant le poste pour un planning
																	  # 'type'
				if employe[1] == 4:
					employe[0].est_disponible = False
					employe[0].poste_occupe = (machine, poste)
					planning[machine][poste] = (poste, employe[0])

	for poste in range(3):
		for machine in getkeys(ouvertures):
			if (planning[machine][poste] == None):
				try: 
					planning[machine][poste] = remplir_poste(classement_poste_ouvrier, machine, poste)
				except: 
					pass

	liste_employes_disponibles = []

	for e in employes: # on créer la liste des employes n'ayant pas été affecté à un poste
		if e.est_disponible:
			liste_employes_disponibles.append(e)

	for poste in range(3):
		for machine in getkeys(ouvertures): 
		# pour chaque machine on regarde si un poste est encore à pourvoir
			if planning[machine][poste] == None:
				classement_machine = classement_poste_ouvrier[machine]
				if classement_machine == [] : continue
				else :
					if poste==1 and len(classement_machine) <= 1:
						continue
					elif poste==2 and len(classement_machine) <= 2:
						continue 
					else :
						classement = classement_poste_ouvrier[machine][poste]
						# on prend le classement des ouvrier pour le poste de la machine actuelle
				remplaçant = None

				for e in classement :
					# on parcours l'ensemble des employés pouvant tenir le poste et on essaye, pour chacun de trouver un remplaçant à
					# son poste, pour qu'il puisse prendre celui vacant

					if (e[0].poste_occupe[1]==4): continue
					# si l'employe est à son poste type, on ne le remplace pas

					remplaçant = trouver_remplaçant(e, liste_employes_disponibles)
					if not remplaçant==None: 
						
						liste_employes_disponibles.remove(remplaçant)

						ancienne_machine = e[0].poste_occupe[0]
						ancien_poste     = e[0].poste_occupe[1]

						remplaçant.poste_occupe = (ancienne_machine, ancien_poste)
						remplaçant.est_disponible = False
						planning[ancienne_machine][ancien_poste] = (ancien_poste, remplaçant)


						e[0].poste_occupe = (machine, poste)	
						planning[machine][poste] = (poste, e[0])



	for machine in get_liste_machines("Matrice de polyvalence.xlsx"):

		# pour chaque machine, les postes vides sont affectés à des intérims ou non pourvus

		keys = getkeys(planning)

		nombre_de_poste = int(machine[1])
		nom_machine = machine[4:].lower()

		if nom_machine not in keys: 
			continue

		planning[nom_machine] = planning[nom_machine][:nombre_de_poste]

		for (index, poste) in enumerate(planning[nom_machine]):
			if poste == None:
				planning[nom_machine][index] = (None, "Poste non affecté")
			else :
				planning[nom_machine][index] = (index, poste[1].nom)

	planning["Employés disponibles"] = [] # on créer la liste pour les employés non afféctés
	
	return (planning, equipe)


def get_planning(jour: int, mois: int, annee: int, semaine: str ,matin: str, aprem: str, nuit: str):

	employes     = get_competences("Matrice de polyvalence.xlsx") # on créer la liste des employés
	liste_conges = conges(jour, mois, annee) # on créer la liste des congés
	ouvertures   = get_ouvertures(chemin_ouverture, semaine, annee) # on créer la liste des onvertures

	liste_jour = ["Lundi", "Mardi", "Mercredi","Jeudi", "Vendredi","Samedi"]

	journee = liste_jour[datetime.datetime(annee, mois, jour).weekday()]

	EQUIPE_MATIN = matin # on assigne à chaque période la bonne équipe
	EQUIPE_APREM = aprem
	EQUIPE_NUIT  = nuit

	employes_matin = list() # liste des employes présents le matin
	employes_aprem = list() # liste des employes présents l'apres-midi
	employes_nuit  = list() # liste des employes présents le soir


	for employe in employes:
		if employe_dans_liste_conge(employe, liste_conges):
			continue
		elif (employe.regime == "P"):
			if int(semaine)%2 == 0:
				employes_matin.append(employe)
				continue
			else :
				employes_aprem.append(employe)
				continue
		elif (employe.regime == "I"):
			if int(semaine)%2 == 1:
				employes_matin.append(employe)
				continue
			else :
				employes_aprem.append(employe)
				continue
		elif (employe.equipe==EQUIPE_MATIN):
			employes_matin.append(employe)
		elif (employe.equipe==EQUIPE_APREM):
			employes_aprem.append(employe)
		elif (employe.equipe==EQUIPE_NUIT):
			employes_nuit.append(employe)

	ouvertures_jour = ouvertures[journee] # ouvertures pour la journée
	planning = [] # planning (liste contenant le planning pour chaque période)

	planning.append(planning_periode(employes_matin, ouvertures_jour[0], EQUIPE_MATIN))
	planning.append(planning_periode(employes_aprem, ouvertures_jour[1], EQUIPE_APREM))
	planning.append(planning_periode(employes_nuit, ouvertures_jour[2], EQUIPE_NUIT))


	

	# planning[i] == (planning_periode, equipe)

	for e in employes_matin: 
		if e.est_disponible:
			planning[0][0]["Employés disponibles"].append(e.nom)

	for e in employes_aprem: 
		if e.est_disponible:
			planning[1][0]["Employés disponibles"].append(e.nom)

	for e in employes_nuit: 
		if e.est_disponible:
			planning[2][0]["Employés disponibles"].append(e.nom)


	return planning


if __name__ == "__main__":
	planning = get_planning(1, 2, 2021, 5, "ROUGE", "BLEUE", "VERTE")
	print(planning)