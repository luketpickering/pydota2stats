#!/opt/local/bin/python2.7
from settings import *
from common import *
from models import *
from time import ctime, time
from sqlalchemy import exc

##############Data Import Utility Functions#############
def new_play(play_dict):
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

        slot=p[u'player_slot']

        Play( mpk=self.pk,
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

#Requests the matches details
def get_details(match):
    match_dict = req_wretry(match_details_url % (match.mid, api_key))
    try:
        plays = filter(lambda x: x[u'account_id'] != dummy_sid32,
                       match_dict[u'players'])
    except Exception as e:
        print account_id, self.mid, match_dict, e
        session.close()
        exit()
    new_plays = []
    try:
        for p in plays:
            new_plays.append(p)
    except Exception as e:
        print e
        session.close()
        exit()
    else:
        return new_plays

def get_matches(newer_than=0, older_than=0):
    older_than = older_than if older_than else time()
    try:
        matches = req_wretry(matches_d_sum_url %
                            (account_id, older_than, newer_than, api_key)
                      )[u'matches']
    except KeyError as ke:
        print ke
        exit()
    else:
        print len(matches)
        new_matches = []
        for m in matches:
            nm = Match(m[u'match_id'], m[u'start_time'])
            new_matches.append(nm)
        return new_matches

def get_current_match_time_range():
    matches_count = session.query(Match).count()
    if matches_count:
        m_sd_q = session.query(Match.start_date)
        oldest = m_sd_q.order_by(Match.start_date).first()[0]
        recent = m_sd_q.order_by(Match.start_date.desc()).first()[0]
        return [oldest-1,recent+1]
    else:
        return [0,0]


##################Main##################
session = init_session()

#If the heroes need getting again
if get_heroes:
    heroes = req_wretry(hero_data_url % api_key)[u'heroes']
    try:
        for hero in heroes:
            nh = Hero(hid=hero[u'id'], name=hero[u'localized_name'])
            session.add(nh)
    except Exception as e:
        print e
        session.close()
        exit()
    else:
        print "Added %s Heroes." % len(heroes)

#If a new user has been added
if add_user:
    nu = User(steamid32=new_user_steamid,name=new_user_name)
    try:
        session.add(nu)
    except Exception as e:
        print e
        session.close()
        exit()
    else:
        session.commit()

#Get some matches
time_range = get_current_match_time_range()

print "Currently have matches between %s and %s'" % \
            (ctime(time_range[0]),ctime(time_range[1]))

matches = get_matches(0, time_range[0])
print "Fetched %s matches between %s and %s" % \
    (len(matches), ctime(matches[0].start_date), ctime(matches[-1].start_date))
print "Adding matches..."

for m in matches:
    try:
        session.add(m)
        session.commit()
    except exc.IntegrityError as ie:
        print "caught IE"
        session.rollback()
    except Exception as e:
        print e
        session.close()
        exit()

session.close()
