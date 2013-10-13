from urllib2 import urlopen
from json import load as jparse
from time import sleep

def req_wretry(url):
    trys = 0
    while( trys < num_retry ):
        trys += 1
        try:
            resp = urlopen(url)
        except Exception as e:
            print 'Request Error: %s, Retrying...' % e
            sleep(1)
        else:
            try:
                resp_dict = jparse(resp)
            except Exception as e:
                print 'Error parsing JSON: %s, re-requesting...' % e
            else:
                return resp_dict
    print "failed %s times, calling it a day." % trys
    exit()

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, create_engine
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from settings import *
Base = declarative_base()
Session = sessionmaker()
session = None

class Match(Base):
    __tablename__ = 'matches'
    pk = Column(Integer, primary_key=True)
    mid = Column(Integer, unique=True, nullable=False)
    start_date = Column(Integer, unique=True, nullable=False)
    got_details = False
    
    def __init__(self, mid, start_date):
        self.mid = mid
        self.start_date = start_date
    
    def get_details(self):
        match_dict = req_wretry(match_details_url % (self.mid, my_api_key) )[u'result']
        try:
            plays = filter(lambda x: x[u'account_id'] != dummy_sid32,
                           match_dict[u'players'])
        except Exception as e:
            print account_id, self.mid, match_dict, e
            return
        new_plays = []
        for p in plays:
            slot=p[u'player_slot']
            np = Play(  mpk=self.pk,
                      suid=p[u'account_id'],
                      hid=p[u'hero_id'],
                      kills=p[u'kills'],
                      deaths=p[u'deaths'],
                      assists=p[u'assists'],
                      last_hits=p[u'last_hits'],
                      denies=p[u'denies'],
                      team_win=((slot < 5) and \
                                (match_dict[u'radiant_win'] == True)) or \
                      ((slot > 5) and \
                       (match_dict[u'radiant_win'] == False)))
            new_plays.append(np)
        self.got_details = True
        return new_plays

class Hero(Base):
    __tablename__ = 'heros'
    pk = Column(Integer, primary_key=True)
    hid = Column(Integer, unique=True, nullable=False)
    name = Column(String, unique=True, nullable=False)
    
    def __init__(self, hid, name='unnamed'):
        self.hid = hid
        self.name=name

class User(Base):
    __tablename__ = 'users'
    pk = Column(Integer, primary_key=True)
    name = Column(String)
    steamid32 = Column(Integer, unique=True, nullable=False)
    
    def __init__(self, steamid32, name='unnamed'):
        self.steamid32 = steamid32
        self.name=name

    @staticmethod
    def sid64to32(sid64):
        return int(account_id64) - 76561197960265728

class Play(Base):
    __tablename__ = 'plays'
    pk = Column(Integer, primary_key=True)
    mpk = Column(Integer, ForeignKey('matches.pk'))
    match = relationship("Match", backref=backref('plays'))
    upk = Column(Integer, ForeignKey('users.pk'))
    user = relationship("User", backref=backref('plays'))
    hpk = Column(Integer, ForeignKey('heros.pk'))
    hero = relationship("Hero", backref=backref('plays'))
    last_hits = Column(Integer)
    denies = Column(Integer)
    team_win = Column(Boolean)
    kills = Column(Integer)
    deaths = Column(Integer)
    assists = Column(Integer)
    
    
    def __init__(self, **kwargs):
        mpk, suid, hid, = None, None, None
        
        try:
            mpk = kwargs['mpk']
            suid = kwargs['suid']
            hid = kwargs['hid']
        except KeyError as ke:
            print ke, kwargs
            exit()
        
        mpkq = session.query(Match).filter(Match.pk == mpk)
        if session.query(mpkq.exists()):
            match = mpkq.first()
        else:
            print 'Invalid Match id: ', mid
        suidq = session.query(User).filter(User.steamid32 == suid)
        if session.query(suidq.exists()):
            user = suidq.first()
        else:
            user = User(steamid3d=suid)
            session.add(user)
        hidq = session.query(Hero).filter(Hero.hid == hid)
        if session.query(hidq.exists()):
            hero = hidq.first()
        else:
            hero = Hero(hid=hid)
            session.add(hero)
        
        self.match = match
        self.user = user
        self.hero = hero
        try:
            self.last_hits=kwargs['last_hits']
            self.denies=kwargs['denies']
            self.kills=kwargs['kills']
            self.deaths=kwargs['deaths']
            self.assists=kwargs['assists']
            self.team_win=kwargs['team_win']
        except KeyError as ke:
            print ke
            exit()

def get_or_create(model, Qry, **kwargs):
    pass

engine = create_engine(sql_con_str)
Base.metadata.create_all(engine)
Session.configure(bind=engine)
session = Session()

