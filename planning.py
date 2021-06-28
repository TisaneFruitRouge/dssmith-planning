from conges import *
from competences import *
from ouvertures import *

chemin_ouverture = "../DOCS STAGE/nvx/ouvertures.xlsx"

def get_liste_employes_machine(employes, machine):
	l = []
	for e in employes:
		if e.possede_competence_machine(machine):
			l.append(e)

	return l

def planning_periode(employes: list, ouvertures: dict):

	planning = {}

	for machine in getkeys(ouvertures):

		liste_employes_machine = get_liste_employes_machine(employes, machine)
		postes_machine = [None,None,None]

		for e in liste_employes_machine:

			if e.est_disponible:
				competences = e.get_competence_machine(machine) # competence de l'employé sur la machine
				if competences[1] == 'conducteur':
					postes_machine[0] = e
					e.disponible = False

				elif competences[1] == 'sous conducteur':
					postes_machine[1] = e
					e.disponible = False

				elif competences[1] == 'prérégleur' or competences[1] == 'préparateur':
					postes_machine[2] = e
					e.disponible = False
		planning[machine] = postes_machine
	
	return planning


def planning(jour: int, mois: int, annee: int, journee: str, matin: str, aprem: str, nuit: str):

	employes     = new_get_competences("Matrice de polyvalence.xlsx") # on créer la liste des employés
	liste_conges = conges(jour, mois, annee) # on créer la liste des congés
	ouvertures   = get_ouvertures(chemin_ouverture) # on créer la liste des onvertures


	EQUIPE_MATIN = matin # on assigne à chaque période la bonne équipe
	EQUIPE_APREM = aprem
	EQUIPE_NUIT  = nuit

	employes_matin = list() # liste des employes présents le matin
	employes_aprem = list() # liste des employes présents l'apres-midi
	employes_nuit  = list() # liste des employes présents le soir

	liste_employes_par_periode = list()

	for employe in employes:
		if (employe.nom in liste_conges):
			employes.remove(employe)
		elif (employe.equipe==EQUIPE_MATIN):
			employes_matin.append(employe)
		elif (employe.equipe==EQUIPE_APREM):
			employes_aprem.append(employe)
		elif (employe.equipe==EQUIPE_NUIT):
			employes_nuit.append(employe)

	liste_employes_par_periode.append(employes_matin)
	liste_employes_par_periode.append(employes_aprem)
	liste_employes_par_periode.append(employes_nuit)

	ouvertures_jour = ouvertures[journee] # ouvertures pour la journée
	
	planning = [] # planning (liste contenant le planning pour chaque période)

	for i in range(3):

		planning.append(planning_periode(liste_employes_par_periode[i], ouvertures_jour[i]))

	return planning
	


if __name__ == "__main__":
	planning = planning(1,2,2021, "Lundi", "ROUGE", "VERTE", "BLEUE")
	print(planning)