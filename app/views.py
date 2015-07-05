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
    return render_template('index.html')

@app.route('/players')
def players():
	playerObjects=db.session.query(Hitter).all()
	return render_template('players.html', players=playerObjects)

@app.route('/player/<player>')
def player(player):
	playerObject=get_or_create(db.session, Hitter, name=player)
	return render_template('player.html', player=playerObject)

@app.route('/games')
def games():
	return render_template('index.html')

@app.route('/backup')
def backupDBtoJSON():
	jsonbackup(session=db.session)
	return render_template('index.html')

@app.route('/restore')
def restoreDBfromJSON():
	jsonrestore(session=db.session)
	return render_template('index.html')

'''@app.route('/admin')
def admin():
	return render_template('index.html')'''