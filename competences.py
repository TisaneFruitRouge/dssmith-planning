# -*- coding: utf-8 -*-

from openpyxl import *
from openpyxl.styles import PatternFill
import json


class Employe(object):

	def __init__(self, nom: str, equipe: str, competences: list,regime: int = 3):


			self.nom = nom
			self.equipe = equipe

			self.regime = regime

			self.est_disponible = True
			self.poste_occupe = None


			self.competences = competences # (machine, poste, niveau)

	def __str__(self):
		string = "########################\n"
		string += f"{self.nom} / {self.equipe} / {self.regime}\n"
		string += "Compétences : \n"
		for competence in self.competences:
			string += f" * {competence}\n"
		string+="########################\n"	

		return string

	def nb_competences(self):
		return len(self.competences)

	def get_competences_machine(self, machine):
		l = []
		for c in self.competences:
			if c[0] == machine:
				l.append(c)
		return l

	def possede_competence_machine(self, machine):
		for c in self.competences:
			if c[0] == machine:
				return True
		return False 


def old_get_competences(chemin_tab_excel):
	
	matrice_de_polyvalence = load_workbook(chemin_tab_excel)

	equipe_bleue = matrice_de_polyvalence.worksheets[1] # matrice de l'equipe bleue
	equipe_verte = matrice_de_polyvalence.worksheets[2] # matrice de l'equipe verte
	equipe_rouge = matrice_de_polyvalence.worksheets[3] # matrice de l'equipe rouge

	liste_equipes = [equipe_bleue, equipe_verte, equipe_rouge]

	competences = [None,None,None] # liste regroupant les compétences des employes sur les machines

	for index, equipe in enumerate(liste_equipes):

		ligne_courante = 2 # ligne courante du tableau excel

		competences[index] = dict() # index represent la n-ième équipe (0=bleue, 1=verte, 2=rouge)

		dict_equipe = competences[index]

		nom_machine_prefixe = equipe["A"+str(ligne_courante)].value # case sur la premiere colonne contenant le nom de la
																	# machine et le prefixe (X, 1, 2 ou 3)
		
		# tant que le texte sur la premiere colonne est rempli, on continue (si c'est vide, cela signifie qu'on a atteint la fin du tableau)
		while nom_machine_prefixe != None:
			nom_machine_prefixe = equipe["A"+str(ligne_courante)].value
			prefixe = nom_machine_prefixe[1] # préfixe
			nom_machine = nom_machine_prefixe[4:] # nom de la machine

			if (prefixe=="X"): 
				ligne_courante+=1
				continue # si le prefixe est "X", on passe

			dict_equipe[nom_machine] = dict() # on créer le dictionnaire des compétences pour cette machine

			competences_machine = dict_equipe[nom_machine]

			for i in range(int(prefixe)):

				nom_poste = equipe["B"+str(ligne_courante)].value
				competences_machine[nom_poste] = list()
				for j in range(11):

					employe = equipe[str(chr(ord("C")+j))+str(ligne_courante)].value

					if employe==None : # il n'y a plus d'employé maitrisant cette machine
						break

					competences_machine[nom_poste].append(employe)

				ligne_courante+=1

			nom_machine_prefixe = equipe["A"+str(ligne_courante)].value

	#final_dict = json.dumps(competences, sort_keys=False, indent=4)

	#print(final_dict)
	#return final_dict

	return competences


def get_nom_machine(poste):
	
	titre_poste = ["palettiseur ", "sous conducteur ", "conducteur ", "prérégleur "]

	for p in titre_poste:
		poste = poste.replace(p, "")

	return poste.strip()

def new_get_competences(chemin_tab_excel):

	matrice_de_polyvalence = load_workbook(chemin_tab_excel) # on ouvre le tableau excel
	liste_employes = list() # liste des employés



	for (index, equipe) in enumerate(matrice_de_polyvalence.worksheets): # on parcours chaque equipe

		ws = matrice_de_polyvalence.worksheets[index]
		
		equipe = ws.title.split(' ')[1] # on recupere le nom de l'equipe (verte, bleue ou rouge)

		for r in range(3, ws.max_row):	# on parcours toutes les lignes
			employe = ws.cell(column=1, row=r).value
			if (employe==None): continue # si la case est vide
			competences = list()
			for c in range(1, ws.max_column): # on parcours toutes les colonnes
				niveau_compétence = ws.cell(column=c, row=r).value
				if (niveau_compétence in [1,2,3]): # si la case [c,r] à la valeur 1 alors l'emploé sait conduire ce poste
					
					poste = ws.cell(column=c, row=2).value.lower()
					machine = get_nom_machine(poste)
					poste = poste.replace(machine, "").strip()
					if poste == "conducteur":
						poste = 0
					elif poste == "sous conducteur":
						poste = 1
					else : 
						poste = 2
					competences.append((machine, poste, niveau_compétence))
				


			e = Employe(employe, equipe, competences) # on créer l'employe et on l'ajoute à la liste
			liste_employes.append(e)

	return liste_employes



def nouvelle_matrice_polyvalence():
	'''
		Cette fonction permet de créer la nouvelle matrice de polyvalence à partir des compétences des employés,
		issues de l'ancienne matrice
	'''
	c = old_get_competences("../DOCS STAGE/nvx/Matrice de polyvalence des equipes.xlsx")
	
	wb = Workbook()

	wb.create_sheet()
	wb.create_sheet()

	wb.worksheets[0].title = "EQ BLEUE"  #On sépare les équipes
	wb.worksheets[1].title = "EQ VERTE"
	wb.worksheets[2].title = "EQ ROUGE"


	for (index, equipe) in enumerate(wb.worksheets):
		competences_equipe = c[index] # c est une liste de 3 éléments, chacun étant un dictionnaire des compétences des employés 
									  # de l'equipe

		machines = list() # liste comportant les machines
		employes = set()  # ensemble comportant les noms des employés

		for (key, values) in competences_equipe.items(): # on parcours le dictionnaire pour avoir le nom des machines
			l = [key]
			nb_poste = len(competences_equipe[key])
			l.append([])
			# on créer une liste de la forme [machine, [poste1, poste2,...., posteN]]
			for poste in getkeys(competences_equipe[key]):
				l[1].append(poste)

				for employe in competences_equipe[key][poste]:
					employes.add(employe)

			machines.append(l)


		ws = wb.worksheets[index]

		current_col = 2

		for machine in machines: # sur la 1ere ligne du tableau excel, on met les machines, et sur la deuxiemes les postes
			ws.cell(column=current_col, row=1, value=machine[0])
			nb_postes = len(machine[1])
			for i in range(nb_postes):
				ws.cell(column=current_col, row=2, value=machine[1][i]) 
				current_col += 1


		for (index, employe) in enumerate(employes): # on rentre sur la 1ere colonne les noms des employés
			current_col = 2	

			for machine in machines: # pour chaque machine, on prend charque poste
				for poste in machine[1]:
					postes_machine = competences_equipe[machine[0]] 
					if employe in postes_machine[poste]: # si l'employ sait être à se poste alors:
						value = 1
						fill = PatternFill(fill_type='solid', start_color='FF00FF00', end_color='FF00FF00')
						# on met 1 dans la case + couleur verte
					else: # sinon
						# on met 0 dans la case + couleur rouge
						value = 0
						fill = PatternFill(fill_type='solid', start_color='FFFF0000', end_color='FFFF0000')

					cell = ws.cell(column=current_col, row=index+3, value=value)
					cell.fill = fill

					current_col += 1


			ws.cell(column=1, row=index+3, value=employe)

	wb.save("test.xlsx")

def getkeys(dic):

	l = []
	
	for key in dic.keys():
		l.append(key)
	return l

if __name__ == '__main__':

	employes = new_get_competences("Matrice de polyvalence.xlsx")

	for e in employes: 
		print(e)
