from urllib2 import urlopen
from json import load as jparse
from time import sleep
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import settings as st
import models as mdls

session = None

def req_wretry(url):
    trys = 0
    while( trys < st.num_retry ):
        trys += 1
        try:
            sleep(1)
            resp = urlopen(url)
        except Exception as e:
            sleep(1)
        else:
            try:
                resp_dict = jparse(resp)
            except Exception as e:
                print 'Error parsing JSON: %s, re-requesting...' % e
            else:
                return resp_dict[u'result']
    print "Request failed %s times, calling it a day." % trys
    session.close()
    exit()

def check_exists(cls, pred):
    q = session.query(cls).filter(pred)
    return session.query(q.exists()).first()[0]

def init_session(init_db=False):
    Session = sessionmaker()
    engine = create_engine(st.sql_con_str)
    Session.configure(bind=engine)
    if init_db:
        mdls.Base.metadata.create_all(engine)
    return Session()