from flask.ext.restful import Resource, abort, reqparse
from flask.ext import restful

from app import db
from Models import *

def is_authenticated(func):
	@wraps(func)
	def wrapper(*args, **kwargs):
		if not getattr(func, 'authenticated', True):
            return func(*args, **kwargs)

        acct = basic_authentication()  # custom account lookup function

        if acct:
            return func(*args, **kwargs)

        restful.abort(401)
    return wrapper

class AuthenticatedResource(Resource):
	method_decorators = [is_authenticated]

class HitterListAPI(AuthenticatedResource):
    def get(self):
        '''get list of all hitters'''
        hitters = Hitter.query.all()
        return jsonify({"hitters" : [h.to_json for h in hitters]})

    def put(self):
        '''create a new hitter'''
        parser = reqparse.RequestParser()
        parser.add_argument('hitter', type=dict, required=True)
        args = parser.parse_args()

        if args['hitter']['name']:
            hitter = Hitter(name=args['hitter']['name'])
            db.session.add(hitter)
            db.session.commit()
            return {'hitter' : hitter.to_json}

class HitterApi(AuthenticatedResource):
    def get(self, id):
        '''get a specific hitter'''
        hitter = Hitter.query.get(id)
        if not hitter:
            abort(404, message='Invalid hitter')
    def put(self, id):
        '''update a specific hitter'''
        hitter = hitter.query.get(id)

        if not hitter:
            abort(404, message='Invalid hitter')

        parser = reqparse.RequestParser()
        parser.add_argument('hitter', type=dict, required=True)
        args = parser.parse_args()

        try:
            hitter.name = args['hitter']['name']
            hitter.lastGamePlayed = args['hitter']['lastGamePlayed']
        except:
            restful.session.abort(400)

        db.session.add(hitter)
        db.session.commit()
        return {'hitter': hitter.to_json}

    def delete(self, id):
        '''Delete a hitter'''
        hitter = Hitter.query.get(id)
        if not hitter:
            hitter.abort(404, message='Invalid todo')

        db.session.delete(hitter)
        db.session.commit()
