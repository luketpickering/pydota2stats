#!/opt/local/bin/python2.7
from sqlalchemy import func
from settings import *
from models import *
session = init_session()
games_won = session.query(Play).filter(Play.upk == 1, Play.team_win == True).count()
games_lost = session.query(Play).filter(Play.upk == 1, Play.team_win == False).count()

games_won_by = session.query(Play.hpk, func.count(Play.hpk)).filter(Play.upk == 1, Play.team_win == True).group_by(Play.hpk).order_by(func.count(Play.hpk)).all()


print games_won, games_lost, games_won_by
print session.query(Hero.name).filter(Hero.pk == games_won_by[-1][1]).one()
