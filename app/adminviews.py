from flask import Flask, Blueprint
from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.sqla import ModelView
from flask_admin.form import rules


from app import app, db
from models import *

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
	#inline_models=(Team,)
	from_create_rules = ('awayteam','awaypoints',rules.Text(' vs. '),'hometeam', 'homepoints', 'winner', 'date', 'event' )
	'''column_searchable_list = (
		'hometeam.containsplayers',
		'awayteam.containsplayers',
		)
	'''

class GameModelView(ModelView):
	column_display_all_relations=True
	column_list = ('awayteam', 'awaypoints','hometeam', 'homepoints', 'winner', 'date', 'event' )