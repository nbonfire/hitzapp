from flask import Flask 
from flask_admin import Admin, BaseView, expose, create_blueprint
from flask_admin.contrib.sqla import ModelView

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


class GameModelView(ModelView):
	column_display_all_relations=True
	column_list = ('awayteam', 'awaypoints','hometeam', 'homepoints', 'winner', 'date', 'event' )