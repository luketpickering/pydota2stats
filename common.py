from urllib2 import urlopen
from json import load as jparse
from time import sleep
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from settings import *
from models import Base

session = None

def req_wretry(url):
    trys = 0
    while( trys < num_retry ):
        trys += 1
        try:
            print "requesting..."
            sleep(1)
            resp = urlopen(url)
        except Exception as e:
            print 'Request Error: %s, Retrying...' % e
            sleep(5)
        else:
            try:
                resp_dict = jparse(resp)
            except Exception as e:
                print 'Error parsing JSON: %s, re-requesting...' % e
            else:
                return resp_dict[u'result']
    print "failed %s times, calling it a day." % trys
    exit()

def check_exists(cls, pred):
    q = session.query(cls).filter(pred)
    return session.query(q.exists()).first()[0]

def init_session():
    Session = sessionmaker()
    engine = create_engine(sql_con_str)
    Session.configure(bind=engine)
    if init_db:
        Base.metadata.create_all(engine)
    return Session()