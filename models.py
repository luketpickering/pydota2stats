from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
import settings as st
import common as cm

Base = declarative_base()

class Match(Base):
    __tablename__ = 'matches'
    pk = Column(Integer, primary_key=True)
    mid = Column(Integer, unique=True, nullable=False)
    start_date = Column(Integer, unique=True, nullable=False)
    got_details = Column(Boolean)
    radiant_win = Column(Boolean)
    duration = Column(Integer)
    lobby_type = Column(Integer)
    game_mode = Column(Integer)
    
    def __init__(self, mid, start_date):
        self.mid = mid
        self.start_date = start_date
        self.got_details = False
    
    
class Hero(Base):
    __tablename__ = 'heroes'
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
    
    @classmethod
    def named_players(cls):
        return cm.session.query(cls)\
                        .filter(User.name != 'unnamed').all()

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
    hpk = Column(Integer, ForeignKey('heroes.pk'))
    hero = relationship("Hero", backref=backref('plays'))
    last_hits = Column(Integer)
    denies = Column(Integer)
    team_win = Column(Boolean)
    kills = Column(Integer)
    deaths = Column(Integer)
    assists = Column(Integer)
    match_type = Column(Integer)
    play_key = Column(Integer, nullable=False, unique=True)
    xpm = Column(Integer)
    gpm = Column(Integer)
    hdmg = Column(Integer)
    tdmg = Column(Integer)
    
    def __getitem__(self,itm):
        return getattr(self, itm)
    
    def __init__(self, **kwargs):
        try:
            self.match = kwargs['match']
            self.user = kwargs['user']
            self.hero = kwargs['hero']
            self.kills = kwargs['kills']
            self.deaths = kwargs['deaths']
            self.assists = kwargs['assists']
            self.last_hits = kwargs['last_hits']
            self.denies = kwargs['denies']
            self.team_win = kwargs['team_win']
            self.match_type = kwargs['match_type']
            self.play_key = int(str(self.match.mid) + str(self.hero.hid))
            self.xpm = kwargs['xp_per_min']
            self.gpm = kwargs['gold_per_min']
            self.hdmg = kwargs['hero_damage']
            self.tdmg = kwargs['tower_damage']
        except KeyError as ke:
            print "key error", ke
            cm.session.close()
            exit()
        except Exception as e:
            print "Exception during Play __init__ %s Ex:" % kwargs,  e
            cm.session.close()
            exit()


