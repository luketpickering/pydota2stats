#!/opt/local/bin/python2.7
from settings import *
from common import *
from models import *
from time import ctime, time
from sqlalchemy import exc

##############Data Import Utility Functions#############
def new_play(mpk, play_dict, rad_win):
    match, hero, user = None, None, None
    
    try:
        match = session.query(Match).filter(Match.pk == mpk).one()
    except Exception as e:
        print "Error retrieving correct match", e
        raise e
    try:
        hero = session.query(Hero).filter(Hero.hid == play_dict[u'hero_id'])\
                .one()
    except Exception as e:
        print "Error retrieving correct hero", e
        raise e
    try:
        user = session.query(User)\
            .filter(User.steamid32 == play_dict[u'account_id']).one()
    except Exception as e:
        print "Haven't found a valid User. Creating"
        user = User(play_dict[u'account_id'])
        session.add(user)
    #except Exception as e:
     #   print "Error retrieving correct hero", e
      #  exit()
       # raise e

    pd = play_dict
    slot=pd[u'player_slot']
    np = Play( match=match,
                  user=user,
                  hero=hero,
                  kills=pd[u'kills'],
                  deaths=pd[u'deaths'],
                  assists=pd[u'assists'],
                  last_hits=pd[u'last_hits'],
                  denies=pd[u'denies'],
                  team_win=((slot < 5) and \
                            (rad_win == True)) or \
                           ((slot > 5) and \
                            (rad_win == False))
                )
    return np

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
            np = new_play(match.pk,p,match_dict[u'radiant_win'])
            new_plays.append(np)
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

un_ret_matches = session.query(Match).filter(Match.got_details == False)\
    .all()

print "Need data on %s Matches" % len(un_ret_matches)
for m in un_ret_matches:
    nps = get_details(m)
    try:
        session.add_all(nps)
        session.commit()
    except Exception as e:
        print e
        session.close()
        exit()

session.close()
