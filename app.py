# -*- coding: utf-8 -*-

from flask import Flask, jsonify, render_template, request, send_file
from flask_cors import CORS

from planning import *
from excel import get_excel_file

import json

app = Flask(__name__)

CORS(app)

@app.route('/', methods=['GET', 'POST'])
def planning():
	if request.method == 'POST':
		
		equipe_matin = request.form["equipe_matin"]
		equipe_aprem = request.form["equipe_aprem"]
		equipe_nuit  = request.form["equipe_nuit"]

		semaine = request.form["semaine"]

		jour  = int(request.form["jour"])
		mois  = int(request.form["mois"])
		annee = int(request.form["annee"])

		planning = get_planning(jour,mois,annee, semaine, equipe_matin, equipe_aprem, equipe_nuit)

		return render_template("planning.html", planning=planning, json_data=json.dumps(planning))

	else :
		return render_template("form_planning.html")
	
@app.route('/create-file', methods=['POST'])
def create_excel_file():
	

	planning = request.json
	path = get_excel_file(planning)
	

	return send_file(path, as_attachment=True)



if __name__ == '__main__':
	app.run()