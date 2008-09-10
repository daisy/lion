import sys
import os
os.sys.path.append("./templates")
import getopt
from ConfigParser import ConfigParser
import MySQLdb
import cherrypy
import util
import translatestrings
import choosemnemonics
import chooseaccelerators
from templates import login, mainmenu, error, xhtml
import daisylion.liondb.dbsession
from daisylion.config_parser import *

class Login(login.login):
    """Things relating to logging in"""
    
    def __init__(self, session, config):
        self.session = session
        self.host = config["webhost"]
        self.port = config["webport"]
        login.login.__init__(self)
    
    def index(self):
        """show the login form"""
        self.message = None
        return self.respond()
    index.exposed = True
    
    def process_login(self, username, password):
        if util.login(username, password, self.session) == None:
            self.message = "There was an error logging in.  Try again?"
            self.title = "Login error -- try again" 
            self.targetid = ""
            self.session.trace_msg("Login error for user %s" % username)
            return self.respond()
        else:
            t = xhtml.xhtml()
            t.port = self.port
            t.host = self.host
            t.title = "Logged in"
            self.session.trace_msg("User %s sucessfully logged in." % username)
            t.body = "<p>Login successful!  <a href=\"MainMenu\">Start working.</a></p>"
            return t.respond()    
    process_login.exposed = True


class MainMenu(mainmenu.mainmenu):
    """This menu gives the tasks for the translators"""
    
    def __init__(self, session, config):
        self.session = session
        self.host = config["webhost"]
        self.port = config["webport"]
        mainmenu.mainmenu.__init__(self)
    
    def index(self):
        """Show the links for the main menu"""
        user = util.get_user(self.session)
        if user == None:
            self.session.warn("No user logged in for this session.")
            return error.error().respond()
        else:
            self.user = user["users.realname"]
            self.language = user["languages.langname"]
            self.translate_for_keyboard = user["languages.translate_for_keyboard"]
            return self.respond()
    index.exposed = True


def main():
    """The entry point for the web app"""
    # read the command line arguments
    try:
        opts, args = getopt.getopt(os.sys.argv[1:], "c", ["config=", "force", "trace"])
    
    except getopt.GetoptError, e:
        os.sys.stderr.write("Error: %s" % e.msg)
        exit(1)
    
    config_file = None
    trace = False
    force = False
    for opt, arg in opts:
        if opt in ("-c", "--config"): config_file = arg
        if opt in ("--trace"): trace = True
        if opt in ("--force"): force = True
    
    config = parse_config_section(config_file, "main")
    
    # for trace and force, read the values from the config file
    # override if they were turned on via the command line
    trace = config["trace"] | trace
    force = config["force"] | force
    dbhost = config["dbhost"]
    dbname = config["dbname"]
    
    session = daisylion.liondb.dbsession.DBSession(dbhost, dbname, trace, force)
    session.trace_msg("Starting the Lion website")

    # initialize the object hierarchy that cherrypy will use
    root = Login(session, config)
    root.MainMenu = MainMenu(session, config)
    root.TranslateStrings = translatestrings.TranslateStrings(session, config)
    root.ChooseMnemonics = choosemnemonics.ChooseMnemonics(session, config)
    root.ChooseAccelerators = chooseaccelerators.ChooseAccelerators(session, config)
    root.style = "./style/"
    app = cherrypy.tree.mount(root, script_name='/')
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Set up site-wide config first so we get a log if errors occur.
    cherrypy.config.update({'environment': 'production',
        'log.error_file': 'site.log',
        'log.screen': True,
        'server.socket_host': '%s' % config["webhost"],
        'server.socket_port': config["webport"],
        'server.thread_pool': 10,
        'tools.encode.on':True,
        'tools.encode.encoding':'utf8'})
    conf = {'/style': {'tools.staticdir.on': True,
                'tools.staticdir.dir': os.path.join(current_dir,'style')}}
    cherrypy.quickstart(root, '/', config=conf)


if __name__ == '__main__': main()
    