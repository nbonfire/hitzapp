from flask import Flask, Blueprint
from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.fileadmin import FileAdmin
from flask_admin.form import rules

from app import app, db
from models import Hitter, Game, get_or_create, completeGame

import io

import json
from datetime import datetime
class HitzAdminView(BaseView):
    '''def is_accessible(self):
        return login.current_user.is_authenticated()
    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            return redirect(url_for('login', next=request.url))
    '''
    @expose('/')
    def index(self):
        return self.render('index.html')

class HitterRuleView(ModelView):
    column_formatters=dict(overallrating=lambda v, c, m, p: m.overallrating.mu - (m.overallrating.sigma * 3), rating=lambda v, c, m, p: m.rating.mu - (m.rating.sigma * 3))

class GameRuleView(ModelView):
    from_create_rules = ('awayteam','awaypoints',rules.Text(' vs. '),'hometeam', 'homepoints', 'winner', 'date', 'event' )

class GameModelView(ModelView):
    column_display_all_relations=True
    column_list = ('awayteam', 'awaypoints','hometeam', 'homepoints', 'winner', 'date', 'event' )

class HitterFileAdmin(FileAdmin):
    #allowed_extensions=('txt')
    def on_file_upload(self, directory, path, filename):
        names=[]
        with io.open(filename, 'r', encoding='utf-8') as fn:
            names=json.loads(fn.read())

        for name in names:
            get_or_create(db.session, Hitter, name=name)

class GameFileAdmin(FileAdmin):
    #allowed_extensions=('txt')
    def on_file_upload(self, directory, path, filename):
        results=[]
        with io.open(filename, 'r', encoding='utf-8') as fg:
            results=json.loads(fg.read())

        for game in results:
            completeGame(db.session, game['home'], game['away'], game['winner'], game['score']['away'], game['score']['home'], datetime.strptime(game['date'], '%Y-%m-%d'))