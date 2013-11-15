#!/opt/local/bin/python2.7
from __future__ import print_function
from models import *
from time import ctime, time
from sqlalchemy import exc
from sqlalchemy.orm import exc as oexc
import common as cm
import settings as st
import argparse
import sys

api_key = ''
current_user_accountid32 = 0
verbose = False
def vprint(tp):
    if verbose:
        print(tp)

def main():
    parser = argparse.ArgumentParser(description="""Tool for importing DOTA2 match data.""")
    
    parser.add_argument('--key', nargs=1, help='your steamAPI key')
    parser.add_argument('--new-user', nargs=2, action='append', help='New to add as --named-user NAME STEAMID32')
    parser.add_argument('--init-db', action='store_true', help='initialise the database')
    parser.add_argument('--get-heroes', action='store_true', help='get an up to date list of the heroes available')
    parser.add_argument('--current-user-name', nargs=1, help='name of the current user. Must exist in the db')
    parser.add_argument('--current-user-pk', nargs=1, help='pk of a user in the db.')
    parser.add_argument('--get-matches', action='store_true',help='get/update the match list for the current user')
    parser.add_argument('--list-users', action='store_true', help='lists all named users currently in the database')
    parser.add_argument('--get-details', action='store_true',help='get the details for any matches currently not specified in the db')
    parser.add_argument('--self-update', action='store_true',help="Ignores all other options except --key and fully updates all named user's data.")
    parser.add_argument('--verbose', action='store_true', help="Enable verbose mode.")

    args = parser.parse_args()
    
    global api_key
    global current_user_accountid32
    
    if args.verbose:
        global verbose
        verbose = True
    
    cm.session = cm.init_session(bool(args.init_db))
    
    if args.list_users:
        print("Current Named Users:")
        for un in User.named_players():
            print("\tpk:%s - %s - id: %s" % (un.pk, un.name, un.steamid32))
        cm.session.close()
        return
    
    err = 0
    if not args.key:
        print("Error: No steamAPI key given. Invoke like --key AAAAAAAAAAA")
        err ^= 1
    else:
        api_key = args.key[0]

    if not err and args.self_update:
        print("Self updating...\n")
        for un in User.named_players():
            print("Updating %s" % un.name)
            current_user_accountid32 = un.steamid32
            get_matches()
        get_new_match_details()
        print("Done.")
        exit(0)

    if not err and args.get_heroes:
        get_heroes()
        
    if not err and args.current_user_name:
        try:
            cu = cm.session.query(User)\
                    .filter(User.name == args.current_user_name[0]).one()
        except oexc.NoResultFound as nrf:
            print("Error: Invalid user name: %s. Invoke with --list-users to get a list of known users")
            err ^=4
        else:
            current_user_accountid32 = cu.steamid32

    if args.new_user:
        new_user = args.new_user[0]
        try:
            ou = cm.session.query(User)\
                    .filter(User.steamid32 == new_user[1]).one()
        except oexc.NoResultFound:
            vprint("--Steamid32 not found, creating new user.")
            nu = User(steamid32=new_user[1],name=new_user[0])
            cm.session.add(nu)
            try:
                cm.session.commit()
            except exc.IntegrityError as ie:
                print("Error: Cannot create a new user: %s" % ie)
                cm.session.rollback()
                err ^= 8
        else:
            vprint("--Steamid32 found, naming user %s" % args.new_user[0])
            ou.name=new_user[0]
            cm.session.add(ou)
            try:
                cm.session.commit()
            except Exception as e:
                print("Error: Couldn't name existing user. %s" % e)
                cm.session.rollback()
                return
            

    if not err and args.new_user and not args.current_user_name:
        current_user_accountid32 = args.new_user[0][1]
    if not err and current_user_accountid32 and args.get_matches:
        get_matches()
    if not err and args.get_details:
        get_new_match_details()

    cm.session.close()

##############Data Import Utility Functions#############
def new_play(mpk, play_dict, rad_win, lobby_type):
    match, hero, user = None, None, None
    
    try:
        match = cm.session.query(Match).filter(Match.pk == mpk).one()
    except Exception as e:
        print("Error retrieving correct match", e)
        raise e
    try:
        hero = cm.session.query(Hero)\
            .filter(Hero.hid == play_dict[u'hero_id']).one()
    except Exception as e:
        print("Error retrieving correct hero", e)
        raise e
    try:
        user = cm.session.query(User)\
             .filter(User.steamid32 == play_dict[u'account_id']).one()
    except oexc.NoResultFound as nrf:
        vprint("--Haven't found a valid User. Creating")
        user = User(play_dict[u'account_id'])
        cm.session.add(user)
        cm.session.commit()
    except Exception as e:
        print("Error retrieving correct user", e)
        raise e

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
                            (rad_win == False)),
                  match_type=lobby_type,
                  xp_per_min=pd[u'xp_per_min'],
                  gold_per_min=pd[u'gold_per_min'],
                  hero_damage=pd[u'hero_damage'],
                  tower_damage=pd[u'tower_damage']
                )
    return np

#Requests the matches details
def get_details(match):
    global api_key

    def filter_me(x):
        try:
            return x[u'account_id'] != st.dummy_sid32
        except KeyError as ke:
            vprint(ke)
            return False
    match_dict = cm.req_wretry(st.match_details_url % (match.mid, api_key))
    try:
        plays = filter(filter_me,
                       match_dict[u'players'])
    except KeyError as ke:
        import pprint
        rdp = pprint.PrettyPrinter(indent=2)
        rdp.pprint(match_dict)
        print(match.mid,  ke)
        return []
    except Exception as e:
        print("big bad error on match(%s): %s" % (match.mid,  e))
        cm.session.close()
        exit()
    new_plays = []
    try:
        match.radiant_win = match_dict[u'radiant_win']
        match.lobby_type = match_dict[u'lobby_type']
        match.duration = match_dict[u'duration']
        match.game_mode = match_dict[u'game_mode']
        cm.session.commit()
    except exc.IntegrityError as ie:
        print("Cannot update match details.")
        cm.session.rollback()
    try:
        for p in plays:
            np = new_play(match.pk, p, match_dict[u'radiant_win'], match_dict[u'lobby_type'])
            new_plays.append(np)
    except exc.IntegrityError as ie:
        print("func:get_details:caught ie %s" % ie)
        cm.session.rollback()
        return []
    else:
        return new_plays

def req_matches(older_than=0):
    global current_user_accountid32, api_key
    older_than = older_than if older_than else time()
    try:
        req = cm.req_wretry(st.matches_d_sum_url %
                            (current_user_accountid32, older_than, 0, api_key)
                            )
        matches = req[u'matches']
    except KeyError as ke:
        vprint("--Error retreiving matches: %s\n%s" % (ke, req))
        try:
            status = req[u'status']
        except KeyError as ke2:
            print("I don't know how to handle this response -> bail: %s" % ke2)
            exit()
        else:
            vprint("--Error Code: %s skipping..." % status) 
            return []
    else:
        new_matches = []
        for m in matches:
            nm = Match(m[u'match_id'], m[u'start_time'])
            new_matches.append(nm)
        return new_matches

#If the heroes need getting again
def get_heroes():
    heroes = cm.req_wretry(st.hero_data_url % api_key)[u'heroes']
    try:
        new_heroes = 0
        for hero in heroes:
            nh = Hero(hid=hero[u'id'], name=hero[u'localized_name'])
            try:
                cm.session.add(nh)
                cm.session.commit()
            except exc.IntegrityError as ie:
                print("Hero ie")
                cm.session.rollback()
            else:
                new_heroes += 1
    except Exception as e:
        print(e)
        cm.session.close()
        exit()
    else:
        print("Added %s new Heroes." % new_heroes)

def add_new_user(name, steamid32):
    nu = User(steamid32=new_user_steamid,name=new_user_name)
    try:
        cm.session.add(nu)
        cm.session.commit()
    except exc.IntegrityError as ie:
        print("IE: in add_new_user: %s" % ie)
        cm.session.rollback()
    except Exception as e:
        print(e)
        cm.session.close()
        exit()

def get_matches(max_reqs=-1):
    older_than = time()
    ctr = 0
    tnm = 0
    while ctr != max_reqs:
        ctr += 1
        nm = 0
        prev_older_than = older_than
        matches = req_matches(older_than)
        try:
            vprint("--Fetched %s matches between %s and %s" % \
                (len(matches), ctime(matches[0].start_date), ctime(matches[-1].start_date)))
        except IndexError as ie:
            vprint("--Didn't find any matches - Probably a skipped error. %s" % ie)
            return
        vprint("Adding matches...")

        for m in matches:
            try:
                cm.session.add(m)
                cm.session.commit()
            except exc.IntegrityError as ie:
                #print "caught IE"
                cm.session.rollback()
                older_than = m.start_date - 1
            except Exception as e:
                print(e)
                cm.session.close()
                exit()
            else:
                nm += 1
                older_than = m.start_date - 1
        #bail condition if no new ones were added
        if nm:
            print("\tAdded %s new matches" % nm)
        tnm += nm
        if prev_older_than == older_than:
            ctr = max_reqs
    return tnm

def get_new_match_details():
    un_ret_matches = cm.session.query(Match)\
                        .filter(Match.got_details == False).all()
    num_matches = len(un_ret_matches)
    print("Need data on %s Matches" % num_matches)
    for i,m in enumerate(un_ret_matches):
        nps = get_details(m)
        print("\r\tHandled %s/%s" % (i+1, num_matches), end='')
        sys.stdout.flush()
        try:
            for np in nps:
                try:
                    cm.session.add(np)
                    cm.session.flush()
                except exc.IntegrityError as ie:
                    print("ADD:caught ie %s" % ie)
                    cm.session.rollback()
                else:
                    m.got_details = True
                    cm.session.commit()
        except Exception as e:
            print(e)
            cm.session.close()
            exit()
    print("")

##################Main##################
main()
