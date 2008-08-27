import sys
import os
os.sys.path.append("./templates")
from ConfigParser import ConfigParser
import MySQLdb
import cherrypy
import util
import translatestrings
import choosemnemonics
import chooseaccelerators
from templates import login, mainmenu, error, xhtml
import daisylion.liondb.dbsession

class Login(login.login):
    """Things relating to logging in"""
    def __init__(self, session):
        self.session = session
    
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
            return self.respond()
        else:
            t = xhtml.xhtml()
            t.title = "Logged in"
            t.body = "<p>Login successful!  <a href=\"MainMenu\">Start working.</a></p>"
            return t.respond()    
    process_login.exposed = True

class MainMenu(mainmenu.mainmenu):
    def __init__(self, session):
        self.session = session
    
    def index(self):
        """Show the links for the main menu"""
        user = util.get_user(self.session)
        if user == None:
            return error.error().respond()
        else:
            self.user = user["users.realname"]
            self.language = user["languages.langname"]
            self.translate_for_keyboard = user["languages.translate_for_keyboard"]
            return self.respond()
    index.exposed = True

#set up cherrypy
config = ConfigParser()
config.read("../lion.cfg")
trace = config.get("main", "trace")
force = config.get("main", "force")
session = daisylion.liondb.dbsession.DBSession(trace, force)
root = Login(session)
root.MainMenu = MainMenu(session)
root.TranslateStrings = translatestrings.TranslateStrings(session)
root.ChooseMnemonics = choosemnemonics.ChooseMnemonics(session)
root.ChooseAccelerators = chooseaccelerators.ChooseAccelerators(session)
root.style = "./style/"
app = cherrypy.tree.mount(root, script_name='/')

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Set up site-wide config first so we get a log if errors occur.
    cherrypy.config.update({'environment': 'production',
        'log.error_file': 'site.log',
        'log.screen': True,
        # use this instead for the server:
        #'server.socket_host': '92.243.13.151',
        'server.socket_host': 'localhost',
        'server.socket_port': 8080,
        'server.thread_pool': 10,
        'tools.encode.on':True,
        'tools.encode.encoding':'utf8'})
    conf = {'/style': {'tools.staticdir.on': True,
                'tools.staticdir.dir': os.path.join(current_dir,'style')}}
    cherrypy.quickstart(root, '/', config=conf)
    
if __name__ == '__main__': main()
    