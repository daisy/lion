import sys
import MySQLdb
import cherrypy
from util import *
os.sys.path.append("./templates")
from translatestrings import *
from Cheetah.Template import Template



class Login:
    """Things relating to logging in"""
    def index(self):
        """show the login form"""
        t = Template(file="./templates/login.tmpl")
        t.message = None
        return str(t)
    index.exposed = True
    
    def process_login(self, username, password):
        if login(username, password) == None:
            t = Template(file="./templates/login.tmpl")
            t.message = "There was an error logging in.  Try again?"
            t.title = "Login error -- try again" 
            return str(t)
        else:
            t = Template(file="./templates/xhtml.tmpl")
            t.title = "Logged in"
            t.body = "<p>Login successful!  <a href=\"MainMenu\">Start working.</a></p>"
            return str(t)    
    process_login.exposed = True

class MainMenu():
    def index(self):
        """Show the links for the main menu"""
        user = get_user()
        if user == None:
            return str(Template(file="./templates/error.tmpl"))
        else:
            t = Template(file="./templates/mainmenu.tmpl")
            t.user = user["users.realname"]
            t.language = user["languages.langname"]
            t.actions = ("<a href=\"TranslateStrings?view=all\">Translate AMIS strings</a>",
                "Assign AMIS keyboard shortcuts",
                "Assign mnemonics (single-letter shortcuts)")
            return str(t)
    index.exposed = True

#set up cherrypy
root = Login()
root.MainMenu = MainMenu()
root.MainMenu.TranslateStrings = TranslateStrings()

#root.show_mnemonics_page = show_mnemonics_page()
#root.show_accelerators_page = show_accelerators_page()

app = cherrypy.tree.mount(root, script_name='/')

if __name__ == '__main__':
    import os.path
    cherrypy.config.update(os.path.join(os.path.dirname(__file__), 'cherrypy.conf'))
    cherrypy.server.quickstart()
    cherrypy.engine.start()
