#!/opt/local/bin/python2.7
from sqlalchemy import func
from settings import *
from models import *
import argparse
from time import ctime, time, mktime, gmtime
from sqlalchemy import exc
from sqlalchemy.orm import exc as oexc
from math import floor

current_user = None
session = cm.init_session()

def main():
    parser = argparse.ArgumentParser(description="""Tool for running stats on DOTA2 match data.""")
    parser.add_argument('--current-user-name', nargs=1, help='name of the current user. Must exist in the db')
    parser.add_argument('--list-users', action='store_true', help='lists all named users currently in the database')

    args = parser.parse_args()

    if args.list_users:
        named_users = session.query(User.pk, User.name,User.steamid32)\
                        .filter(User.name != 'unnamed').all()
        print "Current Named Users:"
        for un in named_users:
            print "\tpk:%s - %s - id: %s" % un
        session.close()
        exit()

    if args.current_user_name:
        try:
            cu = session.query(User)\
                    .filter(User.name == args.current_user_name[0]).one()
        except oexc.NoResultFound as nrf:
            print "Error: Invalid user name: %s. Invoke with --list-users to get a list of known users"
            err ^=1
        else:
            global current_user
            current_user = cu
    else:
        print "Must specify a user... try invoking with --list-users to see available users."
        session.close()
        exit()

    print_basic_stats()
    win_corr_table()

def hero_name(hpk):
    return session.query(Hero.name).filter(Hero.pk == hpk).scalar()

def get_week_ranges(oldest,most_recent):
    a = oldest
    mr = most_recent
    aweek = 60*60*24*7
    while(a < mr):
        a += aweek
        print(ctime(a))

def win_corr_table():
    named_players = session.query(User).filter(User.name != 'unnamed').all()
    rat_matrix = []
    for u in named_players:
        aup = session.query(Play).filter(Play.upk == u.pk).all()
        aum = [ x.mpk for x in aup ]
        u_row = []
        for ou in named_players:
            if ou == u:
                u_row.append((u,reduce(lambda x,y: x + int(y.team_win),aup,0)/float(len(aup))))
                continue
            aoup = session.query(Play).filter(Play.upk == ou.pk).all()
            common_p = [ x for x in aoup if x.mpk in aum ]
            cp_win = reduce(lambda x,y: x + int(y.team_win),common_p,0)
            win_rat = cp_win/float(len(common_p))
            u_row.append((ou,win_rat))
        rat_matrix.append(u_row)
    
    print "\t",
    for np in named_players:
        print "%s " % np.name,
    print ""
    for i, row in enumerate(rat_matrix):
        print named_players[i].name,
        for j, field in enumerate(rat_matrix[i]):
            print " %.2f " % (field[1]),
        print ""

def print_basic_stats():

    cupk = current_user.pk
    baseq = session.query(Play).filter(Play.upk == cupk)

    win_loss = (baseq.filter(Play.team_win == True).count(),
                    baseq.filter(Play.team_win == False).count())

    games_won_by = session.query(Play.hpk, func.count(Play.hpk)).filter(Play.upk == cupk, Play.team_win == True).group_by(Play.hpk).order_by(func.count(Play.hpk))
    games_lost_by = session.query(Play.hpk, func.count(Play.hpk)).filter(Play.upk == cupk, Play.team_win == False).group_by(Play.hpk).order_by(func.count(Play.hpk))
    t_games = baseq.count()

    recent_g = session.query(Match.start_date).join(Match.plays).filter(Play.upk == cupk).order_by(Match.start_date)
    print "DOTA2 Match Stats:"
    print "%s Games between %s and %s" % (t_games, ctime(recent_g[0][0]), ctime(recent_g[-1][0]))
    print "\tGames Won: %s Lost: %s" % win_loss
    print "\tMost Wins: %s with %s, Most Losses: %s with %s" % (hero_name(games_won_by[-1][0]),games_won_by[-1][1], hero_name(games_lost_by[-1][0]),games_lost_by[-1][1])

    plays = baseq.all()
    
    
    kda = [reduce(lambda x, y: x + y[A], plays,0) for A in ['kills','deaths','assists']]
    
    print "Totals:\n\tKills %s, Deaths %s, Assists %s, KDA = %.2f" %(kda[0],kda[1],kda[2], 
        (kda[0] + kda[2])/float(kda[1]))
        
    tot_t = reduce(lambda x, y: x + y.match.duration, plays, 0)
    gpm = reduce(lambda x, y: x + y.gpm, plays, 0)
    
    
    print "\nKPM: %.2f, DPM: %.2f, GPM %.0f, Total Time in game: %sm%ss\nAvg match duration: %s" % \
            (kda[0]/float(tot_t/60),kda[1]/float(tot_t/60),gpm/float(t_games), tot_t/60, tot_t % 60, '%sm %ss' % (floor((tot_t/float(t_games))/60), 
                                floor((tot_t/float(t_games))%60)) )
    
    """
    get_week_ranges(recent_g[0][0],recent_g[-1][0])    
    sniperpk = session.query(Hero.pk).filter(Hero.name == 'Lifestealer').scalar()
    baseq = session.query(Play).filter(Play.hpk == sniperpk)
    s_w = baseq.filter(Play.team_win == True).count()
    s_l = baseq.filter(Play.team_win == False).count()
    s_t = baseq.count()
    
    print "Sniper W/L: %s/%s %s/%s" % (s_w,s_t,s_l,s_t)
    print "Total games known about %s" % session.query(Match).filter(Match.got_details == True).count()"""

main()
