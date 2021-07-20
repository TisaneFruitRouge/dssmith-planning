from openpyxl import *
from openpyxl.styles import PatternFill

from competences import get_liste_machines

def get_periode(index):
	if index==0: return "Matin"
	elif index==1: return "Après-midi"
	else: return "Nuit" 

def get_excel_file(planning: list):
	
	wb = Workbook()
	ws = wb.active


	for (index, _periode) in enumerate(planning): #_periode = (periode, equipe)
		periode = _periode[0]
		equipe  = _periode[1]

		ws.cell(column=3+index, row=2, value=get_periode(index))

		current_row = 4

		for machine in get_liste_machines("Matrice de polyvalence.xlsx"):

			nombre_de_postes = int(machine[1])
			nom_machine = machine[4:].lower()

			ws.cell(column=2, row=current_row, value=nom_machine.upper())

			if nom_machine not in periode:
				current_row+=nombre_de_postes+1
				continue
			else: 
				for i in range(nombre_de_postes):
					postes = periode[nom_machine]
					poste=postes[i][1] 
					cellule = ws.cell(column=3+index, row=current_row, value=poste)
					current_row+=1

					if equipe == "ROUGE":
						color="FFFF6D6D"
					elif equipe == "BLEUE":
						color="FF00FFFF"
					elif equipe == "VERTE":
						color="FF99FF99"

					fill = PatternFill(fill_type='solid', start_color=color, end_color=color)
					cellule.fill=fill

			current_row+=1

	dest_filename = "/home/vincent/Travail/STAGE/programme/planning.xlsx"
	wb.save(filename = dest_filename)
	return dest_filename;