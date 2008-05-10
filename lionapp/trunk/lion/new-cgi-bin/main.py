import sys
import MySQLdb
import cherrypy
from templates import *
from util import *
import translatestrings
from Cheetah.Template import Template

ACTIONS = ("<a href=\"TranslateStrings?view=all\">Translate AMIS strings</a>",
    "Assign AMIS keyboard shortcuts",
    "Assign mnemonics (single-letter shortcuts)")

class Login:
    """Things relating to logging in"""
    def index(self):
        """show the login form"""
        return Template(file="login.tmpl")
    index.exposed = True
    
    def process_login(self, username, password):
        if login(username, password) == None:
            t = Template(file="login.tmpl")
            t.message = "There was an error logging in.  Try again?"
            t.title = "Login error -- try again" 
            return t
        else:
            t = Template(file="xhtml.tmpl")
            t.title = "Logged in"
            t.body = "<p>Login successful!  <a href=\"MainMenu\">Start working.</a></p>"
            return t
    process_login.exposed = True

class MainMenu():
    def index(self):
        """Show the links for the main menu"""
        user = get_user()
        if user == None:
            return Template(file="error.tmpl")
        else:
            user_info = user_information(get_user())
            t = Template(file="mainmenu.tmpl")
            t.user = user_info["users.realname"]
            t.language = user_info["languages.langname"]
            t.actions = ACTIONS
            return t
    
    index.exposed = True

#set up cherrypy
root = Login()
root.MainMenu = MainMenu()
root.MainMenu.TranslateStrings = translatestrings.TranslateStrings()

#root.show_mnemonics_page = show_mnemonics_page()
#root.show_accelerators_page = show_accelerators_page()

app = cherrypy.tree.mount(root, script_name='/')

if __name__ == '__main__':
    import os.path
    cherrypy.config.update(os.path.join(os.path.dirname(__file__), 'cherrypy.conf'))
    cherrypy.server.quickstart()
    cherrypy.engine.start()
