import os
from flask import Flask
import flask.ext.sqlalchemy
import flask.ext.restless

app = Flask(__name__)
app.config.from_object('config.StagingConfig')
db = flask.exst.sqlalchemy.SQLAlchemy(app)

from models import Hitter, Team, Game

restless_manager = flask.ext.restless.APIManager(app, flask_sqlalchemy_db=db)
restless_manager.create_api(Hitter, methods=['GET', 'POST', 'DELETE'])
restless_manager.create_api(Game, methods=['GET', 'POST', 'DELETE'])

@app.route('/')
def hello():
    return 'Hello World!'

@app.route('/<name>')
def hello_name(name):
    return "Hello {}!".format(name)