import sys
import os
os.sys.path.append("./templates")
os.sys.path.append("/home/daisyfor/src/CherryPy-3.0.3/")
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

app = cherrypy.tree.mount(root, script_name='/')

if __name__ == '__main__':
    import os.path
    cherrypy.config.update(os.path.join(os.path.dirname(__file__), 'cherrypy.conf'))
    cherrypy.server.quickstart()
    cherrypy.engine.start()
