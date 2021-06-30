# -*- coding: utf-8 -*-

from flask import Flask, jsonify, render_template, request
from planning import *

app =  Flask(__name__)


@app.route('/')
def hello_world():
	return "<p>Hello World</p>"

@app.route('/planning/', methods=['GET', 'POST'])
def planning():
	if request.method == 'POST':
		
		equipe_matin = request.form["equipe_matin"]
		equipe_aprem = request.form["equipe_aprem"]
		equipe_nuit  = request.form["equipe_nuit"]

		nom_jour = request.form["nom_jour"]

		jour  = int(request.form["jour"])
		mois  = int(request.form["mois"])
		annee = int(request.form["annee"])

		return jsonify(get_planning(jour,mois,annee, nom_jour, equipe_matin, equipe_aprem, equipe_nuit))
	else :
		return render_template("form_planning.html")
	


if __name__ == '__main__':
	app.run()