# -*- coding: utf-8 -*-


from planning.conges import *
from planning.competences import *
from planning.ouvertures import *

import json
import datetime


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
		
		for i in range(len(classement_poste_ouvrier[machine])):
			classement_poste_ouvrier[machine][i] = classe_liste_employes(classement_poste_ouvrier[machine][i])	

	return classement_poste_ouvrier

def remplir_poste(classement_ouvrier: dict, machine: str, poste: int):
	'''
		Cette fonction prend en entrée le classement des ouvriers, une machine et un poste et
		assigne à ce poste sur la machine un ouvrier en fonction du classement
	'''
	# 0 = conducteur
	# 1 = sous-conducteur
	# 2 = autre
	if (classement_ouvrier[machine][poste] == []): return None

	i = 0
	employe = classement_ouvrier[machine][poste][i] # employe = (<Object Employe>, competence: int)

	# on parcours le classement tant qu'un ouvrier n'a pas été trouvé et tant qu'on a pas atteint la fin de 
	# la liste des ouvrier dans le classement
	while not employe[0].est_disponible and i<len(classement_ouvrier[machine][poste]):
		i+=1
		employe = classement_ouvrier[machine][poste][i]
	employe[0].est_disponible = False
	employe[0].poste_occupe = (machine, poste)

	return (poste, employe[0], 0)

def trouver_remplaçant(employe, liste_employes_disponibles: list):

	"""
		Cette fonction prend un employé en entrée ainsi que la liste des employés n'ayant pas été afféctés à 
		un poste et essaye de trouver, parmi ces employés, un pouvant remplacer l'employé donné en entrée à son poste
	"""

	remplaçant = None

	for e in liste_employes_disponibles:
		
		machine = employe[0].poste_occupe[0]
		poste = employe[0].poste_occupe[1]

		if not e.tient_poste(machine, poste):
			continue
		else :
			remplaçant = e

	return remplaçant

def get_regime(employe):
	'''
		Cette fonction renvoie le regime de l'employé à mettre dans le planning 
	'''

	if employe.regime == "P" or employe.regime == "I":
		return 1
	elif employe.est_interimaire:
		return 2
	else: 
		return 0 

def remplacer_employes_par_nom(planning):
	'''
		Cette fonction parcours le planning et remplace chaque objet de type <Employe> par
		son nom et se permet de rajouter des intérimaire là où il pourrait y en avoir besoin
		et de signaler les postes non affectés
	'''
	for machine in get_liste_machines():

		# pour chaque machine, les postes vides sont affectés à des intérims ou non pourvus

		keys = getkeys(planning)

		nombre_de_poste = int(machine[1])
		nom_machine = machine[4:].lower()

		if nom_machine not in keys: 
			continue

		planning[nom_machine] = planning[nom_machine][:nombre_de_poste]

		for (index, poste) in enumerate(planning[nom_machine]):
			if poste == None:
				if index == 2 and not planning[nom_machine][1][0] == None and not planning[nom_machine][0][0] == None:
					planning[nom_machine][2] = (2, "Intérimaire", 0, 0)
				else :
					planning[nom_machine][index] = (None, "Poste non affecté", 0, 0)
			else :
				regime = get_regime(poste[1])
				planning[nom_machine][index] = (index, poste[1].nom, poste[2], regime)

	return planning

def planning_periode(employes: list, ouvertures: dict, equipe: str):

	"""
		Cette fonction créer le planning en prenant en compte les ouvertures et la liste des employés disponibles
	
		NOTE : Dans l'ensemble du programme, les poste pour une machine sont représenter par une liste, ou le 
		1er élément (0) est le conducteur, le deuxiemes (1) le sous-conducteur et le 3eme (2) le dernier poste 
		(préparateur, prérégleur, etc..)
		

		Le planning est un dictionnaire où chaque clef est associé à une liste comportant de 1 à 3 éléments
		chaqun de ces éléments est un tuple de la forme suivante: (poste, employé, info, regime)

		avec :
			poste: en entier compris entre 0 et 2 inclus
			l'employé: l'objet employé
			info: un entier compris entre 0 et 2 avec :
				- 0: pas d'info particulière
				- 1: il y a eu un changement d'équipe
			regime: 0 si normal, 1 si 2x8, 2 si intérim

	"""

	planning = {}

	classement_poste_ouvrier = get_classement_ouvriers(employes, ouvertures)	

	for machine in getkeys(ouvertures): # On place d'abord les ouvriers sur leur poste type (4)

		planning[machine] = [None, None, None]

		for poste in range(3):

			if (classement_poste_ouvrier[machine][poste] == [] or not planning[machine][poste] == None): 
				continue
			else: 
				employe = classement_poste_ouvrier[machine][poste][0] # le premier employe est souvent celui
																	  # occupant le poste pour un planning
																	  # 'type'
				if employe[1] == 4: # on test quand même si il a le niveau de compétence 4
					employe[0].est_disponible = False
					employe[0].poste_occupe = (machine, poste)
					planning[machine][poste] = (poste,
												employe[0],
												0)

	for poste in range(3): # on essaye de remplir chaque poste grâce au classement des ouvriers
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
			if not planning[machine][poste] == None:
				continue
			else:
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

					poste_occupe = e[0].poste_occupe
					if (e[0].get_competence_poste(poste_occupe[0], poste_occupe[1])==4):
						continue

					# si l'employe est à son poste type, on ne le remplace pas
					remplaçant = trouver_remplaçant(e, liste_employes_disponibles)
					if not remplaçant==None: 
						
						liste_employes_disponibles.remove(remplaçant)

						ancienne_machine = e[0].poste_occupe[0]
						ancien_poste     = e[0].poste_occupe[1]

						remplaçant.poste_occupe = (ancienne_machine, ancien_poste)
						remplaçant.est_disponible = False
						planning[ancienne_machine][ancien_poste] = (ancien_poste, remplaçant, 0)


						e[0].poste_occupe = (machine, poste)	
						planning[machine][poste] = (poste, e[0], 0)

	for poste in range(2):
		# on essaie de remplir les postes de conducteur snon pourvus grâce aux postes
		# sur la même machine ayant déjà été pourvus
		for machine in getkeys(ouvertures):
			if planning[machine][poste] == None:

				if (planning[machine][poste+1] == None): continue

				employe = planning[machine][poste+1][1]
				if employe.tient_poste(machine, poste):
					planning[machine][poste] = (poste, employe, 0)

					planning[machine][poste+1] = None


	liste_derniers_dispo = []			
	# on liste les employés sur une machine où il n'y a pas de conducteurs
	for machine in getkeys(ouvertures):

		if machine.lower() == "contremaîtres": continue # on ne fait psa cela si il s'agit des contremaîtres

		if planning[machine][0] == None:

			for poste in range(1,3):
				e = planning[machine][poste]	
				if not e == None:	
					e[1].est_disponible = False
					planning[machine][poste] = None
					liste_derniers_dispo.append(e[1])


	# on essaie de placer ces ouvriers sur une autre machine
	for e in liste_derniers_dispo:
		for machine in getkeys(ouvertures):
			if planning[machine][0] == None:
				if e.tient_poste(machine, 0):

					planning[e.poste_occupe[0]][e.poste_occupe[1]] = None
					
					planning[machine][0] = (0, e, 0)
					e.est_disponible = False
					e.poste = (machine, 0)

					liste_derniers_dispo.remove(e)

					break
				else: 
					continue
			else :
				if planning[machine][1] == None:
					if e.tient_poste(machine, 1):
						planning[e.poste_occupe[0]][e.poste_occupe[1]] = None

						planning[machine][1] = (1, e, 0)
						e.est_disponible = False
						e.poste_occupe = (machine, 1)

						liste_derniers_dispo.remove(e)

						break

				if planning[machine][2] == None:
					if e.tient_poste(machine, 2):
						planning[e.poste_occupe[0]][e.poste_occupe[1]] = None

						planning[machine][2] = (2, e, 0)
						e.est_disponible = False
						e.poste_occupe = (machine, 2)

						liste_derniers_dispo.remove(e)

						break

	for e in liste_derniers_dispo:
		e.poste_occupe = ()
		e.est_disponible = True

	planning["Employés disponibles"] = [] # on créer la liste pour les employés non afféctés
	
	return [planning, equipe]


def get_planning(jour: int, mois: int, annee: int, semaine: str ,matin: str, aprem: str, nuit: str, changement_equipe: int):

	employes     = get_competences() # on créer la liste des employés
	liste_conges = conges(jour, mois, annee) # on créer la liste des congés
	ouvertures   = get_ouvertures(semaine, annee) # on créer la liste des onvertures

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

	# on opère ici des changements d'équipe
	if changement_equipe:
		liste_employes_disponibles = []

		for e in employes_matin+employes_aprem+employes_nuit:
			if e.est_disponible:
				liste_employes_disponibles.append(e)


		for poste in range(3):
			for periode in planning:
				for machine in getkeys(periode[0]):

					if (machine == "Employés disponibles" or 
						not periode[0][machine][poste] == None or
						(poste>0 and periode[0][machine][0] == None) ): # si le poste de conducteur n'est pas pourvus pas la peine de chercher un ous conducteur etc..
						continue

					for e in liste_employes_disponibles:
						if e.tient_poste(machine, poste):
							e.est_disponible = False
							liste_employes_disponibles.remove(e)
							
							periode[0][machine][poste] = (poste, e, 1, get_regime(e))


	for e in employes_matin: 
		if e.est_disponible:
			planning[0][0]["Employés disponibles"].append(e.nom)

	for e in employes_aprem: 
		if e.est_disponible:
			planning[1][0]["Employés disponibles"].append(e.nom)

	for e in employes_nuit: 
		if e.est_disponible:
			planning[2][0]["Employés disponibles"].append(e.nom)


	for periode in planning:
		periode[0] = remplacer_employes_par_nom(periode[0])

	return planning


if __name__ == "__main__":
	planning = get_planning(1, 2, 2021, 5, "ROUGE", "BLEUE", "VERTE", 0)
	print(planning)
