import os
from flask import Flask
import flask.ext.sqlalchemy
from flask.ext.restful import Api, Resource
from flask.ext.bower import Bower
from flask_admin import Admin
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.admin.contrib.sqla import ModelView


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

#app = CustomFlask(__name__)
app=Flask(__name__)
app.config.from_object('config.StagingConfig')
db = flask.ext.sqlalchemy.SQLAlchemy(app)
#api = Api(app)

Bower(app)

from models import Hitter, Team, Game
#from app import models
from views import *
from models import *
from adminviews import HitzAdminView, GameRuleView, HitterRuleView
admin = Admin(app, name='HitzSkill Admin')
#admin.add_view(HitzAdminView)
#admin.add_view()
admin.add_view(HitterRuleView(Hitter, db.session))
admin.add_view(GameRuleView(Game, db.session))

#api.add_resource(HitterListApi, '/api/hitters', methods=['GET', 'POST'])
#api.add_resource(HitterApi, 'api/hitters/<int:id>', methods=['GET', 'POST', 'PUT', 'DELETE'])

#api.add_resource(TeamListApi, '/api/teams', methods=['GET', 'POST'])
#api.add_resource(TeamApi, 'api/teams/<int:id>', methods=['GET', 'POST', 'PUT', 'DELETE'])

#api.add_resource(GameListApi, '/api/games', methods=['GET', 'POST'])
#api.add_resource(GameApi, 'api/games/<int:id>', methods=['GET', 'POST', 'PUT', 'DELETE'])

