from app import app, db #, lm, oid, admin
from flask import render_template, flash, redirect, session, url_for, request, g
#from flask.ext.login import login_user, logout_user, current_user, login_required
#from flask.ext.admin import Admin, BaseView, expose
#from flask.ext.admin.contrib.sqla import ModelView
#from flask.ext.admin.contrib.fileadmin import FileAdmin

#from forms import LoginForm, EditForm
from models import *
from datetime import datetime, timedelta
#from wtforms.fields import SelectField
from Queue import Queue

'''
@app.before_request
def before_request():
	g.user = current_user
	if g.user.is_authenticated():
		g.user.last_seen = datetime.utcnow()
		db.session.add(g.user)
		db.session.commit()
		'''

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/players')
def players():
	return render_template('index.html')

@app.route('/games')
def games():
	return render_template('index.html')

@app.route('/admin')
def admin():
	return render_template('index.html')