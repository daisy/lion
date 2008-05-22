#small and useful things...

#import cgi
#import cgitb; cgitb.enable()
import sys
import os
import datetime
import MySQLdb
import cherrypy
sys.path.append("/home/marisa")
sys.path.append("../")
from DB.connect import *


def get_uuid():
    """Get a uuid from the os to act as a session id."""
    pipe = os.popen("uuidgen", "r")
    uuid = pipe.readline()
    pipe.close()
    return uuid.rstrip()

def login(username, password):
    """Try to login the user and return None on failure."""
    db = connect_to_lion_db("rw")
    cursor = db.cursor()
    request = """
    SELECT * FROM users WHERE username="%(name)s" AND password="%(pwd)s" """ \
    % {"name": username, "pwd": password}
    cursor.execute(request)
    userinfo = cursor.fetchall()
    if userinfo != None and len(userinfo) > 0:
        now = datetime.datetime.now()
        sessionid = get_uuid()
        request = """
        UPDATE users SET sessionid="%(id)s", lastlogin="%(last)s" WHERE username="%(name)s" """ % \
        {"id": sessionid, "last": now.strftime("%Y-%m-%d %H:%M:%S"), "name": username}
        cursor.execute(request)
        set_cookie(username, sessionid)
    else:
        return None
    
    cursor.close()
    db.close()
    return userinfo


def connect_to_lion_db(user):
    """connect to the database
       one day, this function should be replaced with the DBSession class.
    """
    db = db_connect(user)
    if db == None:
        print "Error connecting to the database"
        sys.exit()
    else:
        cursor = db.cursor()
        cursor.execute("SET collation_connection = utf8_unicode_ci")
        return db


def get_user():
    """Check that the user's cookie to see if she's logged in and return her
    user info in a dictionary. If not logged in, return None."""
    username, sessionid = read_cookie()
    if username == "" or username == None: return None
    db = connect_to_lion_db("ro")
    cursor = db.cursor()
    fields = ["users.username", "users.realname", "users.password", "users.email", "users.langid", \
    "users.lastactivity", "users.svnpath", "users.sessionid", "languages.langname", "languages.translate_for_keyboard"]
    request = """
    SELECT %s FROM users, languages WHERE users.username="%s" AND users.sessionid="%s" AND users.langid = languages.langid""" % \
        (",".join(fields), username, sessionid)
    cursor.execute(request)
    row = cursor.fetchone()
    if row == None: return None
    cursor.close()
    db.close()
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
