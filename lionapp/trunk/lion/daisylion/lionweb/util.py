#small and useful things...

import sys
import os
import datetime
import MySQLdb
import cherrypy
import daisylion.liondb.dbsession

def get_uuid():
    """Get a uuid from the os to act as a session id."""
    pipe = os.popen("uuidgen", "r")
    uuid = pipe.readline()
    pipe.close()
    return uuid.rstrip()

def login(username, password, session):
    """Try to login the user and return None on failure."""
    request = """
    SELECT * FROM users WHERE username="%(name)s" AND password="%(pwd)s" """ \
    % {"name": username, "pwd": password}
    session.execute_query(request)
    userinfo = session.cursor.fetchall()
    if userinfo != None and len(userinfo) > 0:
        now = datetime.datetime.now()
        sessionid = get_uuid()
        request = """
        UPDATE users SET sessionid="%(id)s", lastlogin="%(last)s" WHERE username="%(name)s" """ % \
        {"id": sessionid, "last": now.strftime("%Y-%m-%d %H:%M:%S"), "name": username}
        session.execute_query(request)
        set_cookie(username, sessionid)
        return userinfo
    else:
        return None
    

def get_user(session):
    """Check that the user's cookie to see if she's logged in and return her
    user info in a dictionary. If not logged in, return None."""
    username, sessionid = read_cookie()
    if username == "" or username == None: return None
    fields = ["users.username", "users.realname", "users.password", "users.email", "users.langid", \
    "users.lastactivity", "users.svnpath", "users.sessionid", "languages.langname", "languages.translate_for_keyboard"]
    request = """
    SELECT %s FROM users, languages WHERE users.username="%s" AND users.sessionid="%s" AND users.langid = languages.langid""" % \
        (",".join(fields), username, sessionid)
    session.execute_query(request)
    row = session.cursor.fetchone()
    if row == None: 
        return None
    else: 
        return dict(zip(fields, row))



def set_cookie(username, sessionid):
    """Set the login cookie."""
    cookie = cherrypy.response.cookie
    cookie['username'] = username
    cookie['sessionid'] = sessionid


def read_cookie():
    """Read user name and session id for the cookie. If there is an error, user
    name will be empty."""
    username = ""
    sessionid = ""
    cookie = cherrypy.request.cookie
    res = ""
    if cookie == None or len(cookie) == 0:
        return "", ""
    for name in cookie.keys():
        res += "name: %s, value: %s<br>" % (name, cookie[name].value) 
    username = cookie['username'].value
    sessionid = cookie['sessionid'].value
    return username, sessionid
