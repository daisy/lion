import sys
import os
os.sys.path.append("./templates")
from optparse import OptionParser
from ConfigParser import ConfigParser
import MySQLdb
import cherrypy
import util
import translatestrings
import choosemnemonics
import chooseaccelerators
import record_all_prompts
import errorpage
from templates import login, mainmenu, xhtml
import daisylion.db.liondb
import keys

class Login(login.login):
    """The initial login page"""
    
    def __init__(self, session):
        self.session = session
        self.host = self.session.config["main"]["webhost"]
        self.port = self.session.config["main"]["webport"]
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
            t.body = "<p>Login successful!  <a href=\"MainMenu\">Start working</a>.</p>"
            t.redirect = "MainMenu"
            return t.respond()
    process_login.exposed = True


class MainMenu(mainmenu.mainmenu):
    """This menu gives the tasks for the translators"""
    
    def __init__(self, session):
        self.session = session
        self.application = self.session.config["main"]["target_app"]
        self.host = self.session.config["main"]["webhost"]
        self.port = self.session.config["main"]["webport"]
        self.audio_support = self.session.config["main"]["audio_support"]
        self.appname, self.appversion, self.appdesc, self.appsite, self.applogo = \
            util.get_application_data(self.session)
        mainmenu.mainmenu.__init__(self)
    
    def index(self):
        """Show the links for the main menu"""
        user = util.get_user(self.session)
        if user == None:
            self.session.warn("No user logged in for this session.")
            e = errorpage.ErrorPage(self.session, "Login error")
            return e.index()
        else:
            self.user = user["users.realname"]
            self.language = user["languages.langname"]
            self.session.execute_query("""SELECT addldocsuri, addldocsdesc FROM
                application WHERE name="%s" """ % self.application)
            self.addldocsuri, self.addldocsdesc = self.session.cursor.fetchone()
            self.translate_mnemonics, self.translate_accelerators = \
                keys.get_keyboard_translation_flags(self.session)
            return self.respond()
    index.exposed = True

def main():
    """The entry point for the web app"""
    
    usage = "usage: %prog [options] configFile"
    
    parser = OptionParser(usage=usage)
    parser.add_option("-t", "--trace", dest="trace", action="store_true",
                    default=False, help="Turn on program trace")
    (options, args) = parser.parse_args()
    if args == None or len(args) <= 0:
        print usage
        sys.exit(1)
    config_file = args[0]
    
    session = daisylion.db.liondb.LionDB(config_file, options.trace, None)
    session.trace_msg("Starting the Lion website")
    
    # initialize the object hierarchy that cherrypy will use
    root = Login(session)
    root.MainMenu = MainMenu(session)
    root.TranslateStrings = translatestrings.TranslateStrings(session)
    root.ChooseMnemonics = choosemnemonics.ChooseMnemonics(session)
    root.ChooseAccelerators = chooseaccelerators.ChooseAccelerators(session)
    root.RecordAllPrompts = record_all_prompts.RecordAllPrompts(session)
    root.RecordAllPrompts.UploadComplete = record_all_prompts.UploadComplete(session)
    root.style = "./style/"
    app = cherrypy.tree.mount(root, script_name='/')
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Set up site-wide config first so we get a log if errors occur.
    cherrypy.config.update({'environment': 'production',
        'log.error_file': 'site.log',
        'log.screen': True,
        'server.socket_host': '%s' % session.config["main"]["webhost"],
        'server.socket_port': session.config["main"]["webport"],
        'server.thread_pool': 10,
        'tools.encode.on':True,
        'tools.encode.encoding':'utf8'})
    conf = {'/style': {'tools.staticdir.on': True,
                'tools.staticdir.dir': os.path.join(current_dir,'style')},
            '/xslt': {'tools.staticdir.on': True,
                'tools.staticdir.dir': os.path.join(current_dir, 'xslt')}
            }
    cherrypy.quickstart(root, '/', config=conf)


if __name__ == '__main__': main()
    
