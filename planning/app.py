# -*- coding: utf-8 -*-

from flask import Flask, jsonify, render_template, request, send_file
from flask_cors import CORS

from planning.planning import *
from planning.excel import get_excel_file, get_color
from planning.conges import conges as get_liste_conges

import json


app = Flask(__name__)

CORS(app)

@app.route('/')
def home():
	return render_template('home.html')

@app.route('/form-planning', methods=['GET', 'POST'])
def planning():
	if request.method == 'POST':
		
		equipe_matin = request.form["equipe_matin"]
		equipe_aprem = request.form["equipe_aprem"]
		equipe_nuit  = request.form["equipe_nuit"]

		semaine = request.form["semaine"]

		try:
			changement_equipe = int(request.form["changement-equipe"])
		except :
			changement_equipe = 0


		jour  = int(request.form["jour"])
		mois  = int(request.form["mois"])
		annee = int(request.form["annee"])

		planning = get_planning(jour,mois,annee, semaine, 
								equipe_matin, equipe_aprem, equipe_nuit, 
								changement_equipe)

		data = []

		for i in range(3):
			periode = planning[i][0]

			postes_non_pourvus = [0,0,0]

			for machine in periode:
				for index, poste in enumerate(periode[machine]):
					if poste[1] == "Poste non affecté":
						postes_non_pourvus[index] += 1
			data.append(postes_non_pourvus)

			


		return render_template("planning.html", 
								planning=planning, 
								json_data=json.dumps([planning, [jour, mois, annee, semaine]]),
								data=data
								)

	else :
		return render_template("forms/form_planning.html")

@app.route("/conges", methods=["GET", "POST"])
def conges():
	if request.method == "POST":

		jour  = int(request.form["jour"])
		mois  = int(request.form["mois"])
		annee = int(request.form["annee"])

		liste_conges = get_liste_conges(jour,mois,annee)

		liste_conges_couleur = []

		for conge in liste_conges:
			liste_conges_couleur.append( (conge[0], conge[1], '#'+get_color(conge[0])[2:]) )

		return render_template("conges.html",
								conges=liste_conges_couleur,
								json_data=json.dumps(liste_conges),
								data={"annee": annee, "mois": mois, "jour": jour})

	else: 
		return render_template("forms/form_conges.html")

	
@app.route('/create-file', methods=['POST'])
def create_excel_file():
	
	dates  = request.json["dates"]



	liste_conges = get_liste_conges(dates[0],dates[1],dates[2])
	
	planning = request.json["planning"]

	path = get_excel_file(planning, liste_conges, dates)
	

	return send_file(path, as_attachment=True)



@app.errorhandler(500)
def internal_server_error(error):
	return render_template("500.html"), 500


if __name__ == '__main__':
	app.run()
