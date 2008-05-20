import sys
import os
os.sys.path.append("./templates")
import MySQLdb
import cherrypy
import util
import translatestrings
import choosemnemonics
import chooseaccelerators
from templates import login, mainmenu, error, xhtml

class Login(login.login):
    """Things relating to logging in"""
    def index(self):
        """show the login form"""
        self.message = None
        return self.respond()
    index.exposed = True
    
    def process_login(self, username, password):
        if util.login(username, password) == None:
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
    def index(self):
        """Show the links for the main menu"""
        user = util.get_user()
        if user == None:
            return error.error().respond()
        else:
            self.user = user["users.realname"]
            self.language = user["languages.langname"]
            return self.respond()
    index.exposed = True

#set up cherrypy
root = Login()
root.MainMenu = MainMenu()
root.TranslateStrings = translatestrings.TranslateStrings()
root.ChooseMnemonics = choosemnemonics.ChooseMnemonics()
root.ChooseAccelerators = chooseaccelerators.ChooseAccelerators()
root.style = "./style/"
app = cherrypy.tree.mount(root, script_name='/')

if __name__ == '__main__':
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Set up site-wide config first so we get a log if errors occur.
    #'192.168.1.146'
    cherrypy.config.update({'environment': 'production',
        'log.error_file': 'site.log',
        'log.screen': True,
        'server.socket_host': '192.168.1.146',
        'server.socket_port': 8080,
        'server.thread_pool': 10})
    conf = {'/style': {'tools.staticdir.on': True,
                'tools.staticdir.dir': os.path.join(current_dir,'style')}}
    cherrypy.quickstart(root, '/', config=conf)
