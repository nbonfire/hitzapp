from flask import Flask, Blueprint
from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.sqla import ModelView
from flask.admin.forms import rules

from app import app, db


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

class GameRuleView(ModelView):
	from_create_rules = ('awayteam','awaypoints',rules.Text(' vs. '),'hometeam', 'homepoints', 'winner', 'date', 'event' )

class GameModelView(ModelView):
	column_display_all_relations=True
	column_list = ('awayteam', 'awaypoints','hometeam', 'homepoints', 'winner', 'date', 'event' )