#!/opt/local/bin/python2.7
from sqlalchemy import func
from settings import *
from models import *
session = init_session()

num_games_won = session.query(Play).filter(Play.upk == 1, Play.team_win == True).count()

num_games_lost = session.query(Play).filter(Play.upk == 1, Play.team_win == False).count()

games_won_by = session.query(Play.pk).filter(Play.upk == 1, Play.team_win == True).order_by(Play.pk).all()

print "won %s" % num_games_won, "lost %s" % num_games_lost
print "won %s: %s" % (len(games_won_by), games_won_by)
#print session.query(Hero.name).filter(Hero.pk == games_won_by[-1][1]).one()
