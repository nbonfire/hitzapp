import os
from flask import Flask
import flask.ext.sqlalchemy
from flask.ext.restful import Api, Resource
from flask.ext.bower import Bower


class CustomFlask(Flask):
    jinja_options = Flask.jinja_options.copy()
    jinja_options.update(dict(
        block_start_string='<%',
        block_end_string='%>',
        variable_start_string='%%',
        variable_end_string='%%',
        comment_start_string='<#',
        comment_end_string='#>',
    ))

app = CustomFlask(__name__)
app.config.from_object('config.StagingConfig')
db = flask.exst.sqlalchemy.SQLAlchemy(app)
#api = Api(app)

bow = Bower(App)
from models import Hitter, Team, Game
from app import views, models

#api.add_resource(HitterListApi, '/api/hitters', methods=['GET', 'POST'])
#api.add_resource(HitterApi, 'api/hitters/<int:id>', methods=['GET', 'POST', 'PUT', 'DELETE'])

#api.add_resource(TeamListApi, '/api/teams', methods=['GET', 'POST'])
#api.add_resource(TeamApi, 'api/teams/<int:id>', methods=['GET', 'POST', 'PUT', 'DELETE'])

#api.add_resource(GameListApi, '/api/games', methods=['GET', 'POST'])
#api.add_resource(GameApi, 'api/games/<int:id>', methods=['GET', 'POST', 'PUT', 'DELETE'])

@app.route('/hello')
def hello():
    return 'Hello World!'

@app.route('/<name>')
def hello_name(name):
    return "Hello {}!".format(name)