from app import db
from sqlalchemy.dialects.postgresql import JSON
from flask.ext.restful import Resource, abort
from flask.ext import restful
from flask.ext.restful import reqparse

import json, io, pickle, itertools, pprint, os

from sortedcollection import *
from trueskill import *
from math import sqrt
from datetime import datetime


env=TrueSkill() # current season
overallenv=TrueSkill()
teamenv=TrueSkill() #current season
overallteamenv=TrueSkill()

currentseasonstartdate=datetime(2013,4,21)


RESET=0
SIGMA_CUTOFF=5.0

'''
class Result(db.Model):
    __tablename__ = 'results'

    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String())
    result_all = db.Column(JSON)
    result_no_stop_words = db.Column(JSON)

    def __init__(self, url, result_all, result_no_stop_words):
        self.url = url
        self.result_all = result_all
        self.result_no_stop_words = result_no_stop_words

    def __repr__(self):
        return '<id {}>'.format(self.id)
'''



class Hitter(db.Model):
    __tablename__='hitters'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    #teams = db.relationship("Team", backref="hitter")
    overallrating = db.Column(db.PickleType)
    rating = db.Column(db.PickleType) # current season rating
    lastGamePlayed = db.Column(db.DateTime)
    def __init__(self, name='test',lastGamePlayed = datetime(2013,7,1),rating = env.Rating()):
        self.name = name
        self.lastGamePlayed = lastGamePlayed
        self.rating = rating
        self.overallrating=rating
    def hitzskill(self):
        return float(int((self.rating.mu - 3.0*self.rating.sigma)*100))/100.0
    def overallhitzskill(self):
        return float(int((self.overallrating.mu - 3.0*self.overallrating.sigma)*100))/100.0
    def recordString(self, date=currentseasonstartdate):
        winninggames=0
        totalgames=0
        for team in self.teams:
            totalgames=totalgames+len(team.homegames)+len(team.awaygames)
            winninggames=winninggames+len(team.winninggames)
        return "%d - %d" %(winninggames, (totalgames-winninggames))
    def __repr__(self):
        return "<%s, %s, %s>" % (self.name, self.lastGamePlayed, str(self.rating.mu - 3.0*self.rating.sigma))
    def shortdict(self):
        return {
            'name':self.name,
            'record':self.recordString(),
            'skill':self.hitzskill(),
            'overallskill':self.overallhitzskill()
        }
    @property
    def to_json(self):
        return {
            'name':self.name,
            'record':self.recordString(),
            'skill':self.hitzskill(),
            'overallskill':self.overallhitzskill()
        }
    




hitter_team_table = db.Table('hitter_team', db.Model.metadata,
    db.Column('team_id', db.Integer, db.ForeignKey('teams.id')),
    db.Column('hitter_id', db.Integer, db.ForeignKey('hitters.id'))

)

class Team(db.Model):
    __tablename__='teams'
    id = db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String)
    teamrating = db.Column(db.PickleType)
    overallteamrating = db.Column(db.PickleType)
    hitters = db.relationship("Hitter", secondary=hitter_team_table, backref='teams')

    def __init__(self):
        self.teamrating = teamenv.Rating()
        self.overallteamrating = overallteamenv.Rating()
    def __repr__(self):
        return "<%s, %s, %s last played: %s team rating: %s>" % (self.hitters[0].name, self.hitters[1].name, self.hitters[2].name, self.getdatelastplayed(),str(self.teamrating.mu - 3.0*self.teamrating.sigma))

    def tupleratings(self):
        ratingslist=[]
        for player in self.hitters:
            ratingslist.append(player.rating)

        return tuple(ratingslist)
    def tupleoverallratings(self):
        ratingslist=[]
        for player in self.hitters:
            ratingslist.append(player.overallrating)

        return tuple(ratingslist)
    def teamskill(self):
        return (self.teamrating.mu - 3.0*self.teamrating.sigma)
    def overallteamskill(self):
        return (self.overallteamrating.mu - 3.0*self.overallteamrating.sigma)
    def setdatelastplayed(self, datePlayed=datetime.today()):
        
        for player in self.hitters:
            if datePlayed > player.lastGamePlayed:
                player.lastGamePlayed =datePlayed
        
    def getdatelastplayed(self):
        comparedate=datetime.today()
        for player in self.hitters:
            if player.lastGamePlayed < comparedate:
                comparedate=player.lastGamePlayed
        return comparedate
    def listnames(self):
        return "%s, %s, %s"% (self.hitters[0].name, self.hitters[1].name, self.hitters[2].name)
    def listofnames(self):
        return [self.hitters[0].name, self.hitters[1].name, self.hitters[2].name]
    def getteamrating(self):
        sumindividual=0.0
        for player in self.hitters:
            sumindividual=sumindividual+player.hitzskill()
        avgindividual= sumindividual/len(self.hitters)
        
        if avgindividual>self.teamskill():
            return avgindividual
        else:
            return self.teamskill()
    def getoverallteamrating(self):
        sumindividual=0.0
        for player in self.hitters:
            sumindividual=sumindividual+player.overallhitzskill()
        avgindividual= sumindividual/len(self.hitters)
        
        if avgindividual>self.overallteamskill():
            return avgindividual
        else:
            return self.overallteamskill()
    @property
    def to_json(self):
        return {
                "name" : self.name,
                "teamrating": self.getteamrating(),
                "overallteamrating" : self.getoverallteamrating(),
                "hitters" : [hitter.to_json for hitter in self.hitters],
        }
    


    

class Game(db.Model):
    __tablename__='games'
    id = db.Column(db.Integer, primary_key=True)
    #hometeam = ManyToOne('Teams', inverse='homegames')
    hometeam_id = db.Column(db.Integer, db.ForeignKey('teams.id'))
    hometeam = db.relationship("Team",
        primaryjoin=('games.c.hometeam_id==teams.c.id'),
        remote_side='Team.id',
        backref=db.backref('homegames', order_by=id))
    
    #awayteam = ManyToOne('Teams', inverse='awaygames')
    awayteam_id = db.Column(db.Integer, db.ForeignKey('teams.id'))
    awayteam = db.relationship("Team", 
        primaryjoin=('games.c.awayteam_id==teams.c.id'),
        remote_side='Team.id',
        backref=db.backref('awaygames', order_by=id))
    
    #winner = ManyToOne('Teams', inverse = 'winner')
    winner_id = db.Column(db.Integer, db.ForeignKey('teams.id'))
    winner = db.relationship('Team',
        primaryjoin=('games.c.winner_id==teams.c.id'),
        remote_side='Team.id', 
        backref=db.backref('winninggames', order_by=id))
    
    awaypoints = db.Column(db.Integer)
    homepoints = db.Column(db.Integer)
    #date = Field(db.DateTime, default=db.DateTime.db.DateTime.now())
    date = db.Column(db.DateTime)
    #event = Field(UnicodeText)
    event = db.Column(db.String)
    #gameNumber = Field(db.Integer)
    gameNumber = db.Column(db.Integer)
    def __init__(self, hometeam, awayteam, winner, homepoints=0,awaypoints=0, date = datetime.now() ):
        self.date = date
        self.hometeam = hometeam
        self.awayteam = awayteam
        self.winner = winner
        self.awaypoints = awaypoints
        self.homepoints = homepoints
    def winposition(self):
        if self.winner_id == self.hometeam_id:
            return "home"
        elif self.winner_id == self.awayteam_id:
            return "away"
        else:
            return "can't tell - winner: %s, home: %s, away: %s, names: %s" % (self.winner_id, self.hometeam_id, self.awayteam_id, self.winner.names())
    def __repr__(self):
        return "<%s -  %s vs %s - %s won>" %(self.date, self.awayteam, self.hometeam, self.winner)
    def _asdict(self):
        return {
            'id':self.id,
            'away':self.awayteam.listofnames(),
            'home':self.hometeam.listofnames(),
            'winner':self.winposition(),
            'date':datetime.strftime(self.date,'%Y-%m-%d'),
            'score':{
                        'home':self.homepoints,
                        'away':self.awaypoints
                    }
        }

def standaloneSetup():
    engine = create_engine('sqlite:///hitz.sqlite')
    

    Session = sessionmaker(bind=engine)

    session = Session()
    db.Model.metadata.create_all(engine)
    return session

def jsonbackup(session):
    results = []
    names = []
    allgames = session.query(Game).all()
    allhitters=session.query(Hitter).all()
    for hitter in allhitters:
        names.append(hitter.name)

    for game in allgames:
        results.append(game._asdict())

    with io.open('playersbackup-%s.txt'% str(datetime.today()), 'w', encoding='utf-8') as fn:
        fn.write(unicode(json.dumps(names, ensure_ascii=False)))
    with io.open('gamesbackup-%s.txt'% str(datetime.today()), 'w', encoding='utf-8') as fg:
        fg.write(unicode(json.dumps(results, ensure_ascii=False)))
    return json.dumps(results)

def jsonrestore(session):
    namefile='playersbackup.txt'
    gamefile='gamesbackup.txt'
    
        
    results=[]
    names=[]

    with io.open(namefile, 'r', encoding='utf-8') as fn:
        names=json.loads(fn.read())
    with io.open(gamefile, 'r', encoding='utf-8') as fg:
        results=json.loads(fg.read())
    #pprint.pprint(names)
    #pprint.pprint( results)
        
    for name in names:
        get_or_create(session, Hitter, name=name)
    for game in results:
        completeGame(session,game['home'], game['away'], game['winner'], game['score']['away'], game['score']['home'], datetime.strptime(game['date'], '%Y-%m-%d %H:%M:%S'))
    session.close()
    

def get_or_create(session, model, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        session.add(instance)
        session.commit()
        return instance
    # myHitter = get_or_create(session, Hitter, name=hitterName)
def get_or_create_team(session, findplayers):
    #print findplayers
    create_team = session.query(Team).filter(Team.hitters.any(Hitter.name==findplayers[0])).filter(Team.hitters.any(Hitter.name==findplayers[1])).filter(Team.hitters.any(Hitter.name==findplayers[2])).first()
    #session.query(Team).filter(Team.players.in_()) session.query(Hitter).name.in_(session)
    if not create_team:
        #create_team = Team()
        hittersforthisteam = []
        for newplayer in findplayers:
            hittersforthisteam.append(session.query(Hitter).filter_by(name=newplayer).first())
        if len(hittersforthisteam)<3:
            print "invalid player in list: %s" % findplayers
            return False
        else:
            create_team = Team()
            create_team.hitters = hittersforthisteam
            session.add(create_team)
            session.commit()
    return create_team

def completeGame(session,homeTeam,awayTeam,winner,awaypoints=0,homepoints=0,datePlayed=datetime.today()):
    homers=get_or_create_team(session, homeTeam)
    awayers=get_or_create_team(session, awayTeam)
    homers.setdatelastplayed(datePlayed)
    awayers.setdatelastplayed(datePlayed)

    #print "\n----------\n%s vs %s  " % (awayers, homers)
    
    if winner=='home':
        winningteam=get_or_create_team(session, homeTeam)
        #team rating
        if (datePlayed>currentseasonstartdate):
            homers.teamrating,awayers.teamrating = rate_1vs1(homers.teamrating, awayers.teamrating)
            #individual ratings
            (awayers.hitters[0].rating, awayers.hitters[1].rating, awayers.hitters[2].rating),(homers.hitters[0].rating, homers.hitters[1].rating, homers.hitters[2].rating) = rate([[awayers.hitters[0].rating, awayers.hitters[1].rating, awayers.hitters[2].rating],[homers.hitters[0].rating, homers.hitters[1].rating, homers.hitters[2].rating]], ranks=[1,0])
        homers.overallteamrating,awayers.overallteamrating = rate_1vs1(homers.overallteamrating, awayers.overallteamrating)
        (awayers.hitters[0].overallrating, awayers.hitters[1].overallrating, awayers.hitters[2].overallrating),(homers.hitters[0].overallrating, homers.hitters[1].overallrating, homers.hitters[2].overallrating) = rate([[awayers.hitters[0].overallrating, awayers.hitters[1].overallrating, awayers.hitters[2].overallrating],[homers.hitters[0].overallrating, homers.hitters[1].overallrating, homers.hitters[2].overallrating]], ranks=[1,0])

            
    else:
        winningteam=get_or_create_team(session, awayTeam)
        

        if (datePlayed>currentseasonstartdate):
            #team ratings
        
            awayers.teamrating,homers.teamrating = rate_1vs1(awayers.teamrating, homers.teamrating)
            #individual ratings
            (awayers.hitters[0].rating, awayers.hitters[1].rating, awayers.hitters[2].rating),(homers.hitters[0].rating, homers.hitters[1].rating, homers.hitters[2].rating) = rate([[awayers.hitters[0].rating, awayers.hitters[1].rating, awayers.hitters[2].rating],[homers.hitters[0].rating, homers.hitters[1].rating, homers.hitters[2].rating]], ranks=[0,1])
        awayers.overallteamrating,homers.overallteamrating = rate_1vs1(awayers.overallteamrating, homers.overallteamrating)
            #individual ratings
        (awayers.hitters[0].overallrating, awayers.hitters[1].overallrating, awayers.hitters[2].overallrating),(homers.hitters[0].overallrating, homers.hitters[1].overallrating, homers.hitters[2].overallrating) = rate([[awayers.hitters[0].overallrating, awayers.hitters[1].overallrating, awayers.hitters[2].overallrating],[homers.hitters[0].overallrating, homers.hitters[1].overallrating, homers.hitters[2].overallrating]], ranks=[0,1])

    newgame = Game(hometeam=homers, awayteam=awayers, homepoints=homepoints, awaypoints=awaypoints, winner=winningteam,date=datePlayed)
    session.add(newgame)
    session.commit()
