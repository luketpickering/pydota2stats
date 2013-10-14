from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from settings import *
from common import *

Base = declarative_base()

class Match(Base):
    __tablename__ = 'matches'
    pk = Column(Integer, primary_key=True)
    mid = Column(Integer, unique=True, nullable=False)
    start_date = Column(Integer, unique=True, nullable=False)
    got_details = False
    
    def __init__(self, mid, start_date):
        self.mid = mid
        self.start_date = start_date
    
    
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
        pass

def get_or_create(model, Qry, **kwargs):
    pass

