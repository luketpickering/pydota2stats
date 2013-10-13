#!/opt/local/bin/python2.7
from settings import *
from models import *
from time import ctime

#fetching heros

if get_heros:
    heroes = req_wretry(hero_data_url % my_api_key)[u'result'][u'heroes']
    for hero in heroes:
        nh = Hero(hid=hero[u'id'], name=hero[u'localized_name'])
        session.add(nh)
        print "Adding Hero:%s" % hero[u'localized_name']
if add_user:
    nu = User(steamid32=account_id32,name='Hannah Montanha')
    session.add(nu)
session.commit()

cnt = session.query(Match).count()
if cnt:
    latestm = session.query(Match).order_by(Match.start_date).first()
    matches_before = latestm.start_date - 1
    resp_dict = req_wretry(matches_d_sum_url % (account_id, matches_before, my_api_key))
else:
    resp_dict = req_wretry(matches_sum_url % (account_id,my_api_key))

matches = resp_dict[u'result'][u'matches']
print "Epoch calibration %s" % ctime(0)
print "Fetched %s matches between %s and %s" % \
    (len(matches), ctime(matches[0][u'start_time']), ctime(matches[-1][u'start_time']))


def check_exists(cls, pred):
    q = session.query(cls).filter(pred)
    return session.query(q.exists()).first()[0]
ctr = 0
tot = len(matches)
for x in matches:
    try:
        if not check_exists(Match, Match.mid == x[u'match_id']):
            m = Match(x[u'match_id'], x[u'start_time'])
            session.add(m)
        else:
            m = session.query(Match).filter(Match.mid == x[u'match_id']).one()
    except KeyError as ke:
        print 'key error %s' % ke
        exit()
    else:
        if not m.got_details:
            print "Fetching match(id:%s). %s/%s" % (m.mid, ctr, tot)
            ctr += 1
            nps = m.get_details()
            session.add_all(nps)
            session.commit()
