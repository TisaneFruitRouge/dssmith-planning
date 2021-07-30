from flask import request, render_template

#rest of the code goes here

@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html'), 500