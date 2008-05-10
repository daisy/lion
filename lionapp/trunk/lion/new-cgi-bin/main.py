import sys
import MySQLdb
import cherrypy
from templates import *
from util import *
import translatestrings

class Login:
    """Things relating to logging in"""
    def index(self):
        """show the login form"""
        return XHTML_TEMPLATE % {"TITLE": "Login", "BODY": LOGIN_FORM}
    index.exposed = True
    
    def process_login(self, username, password):
        if login(username, password) == None:
            body = "<p>There was an error logging in.  Try again?</p>" + LOGIN_FORM
            return XHTML_TEMPLATE % {"TITLE": "Login error -- try again", "BODY": body}
        else:
            body = "<p>Login successful!  <a href=\"MainMenu\">Start working.</a></p>"
            return XHTML_TEMPLATE % {"TITLE": "Logged in", "BODY": body}
    
    process_login.exposed = True

class MainMenu():
    def index(self):
        """Show the links for the main menu"""
        user = get_user()
        if user == None:
            return general_error()
        else:
            user_info = user_information(get_user())
            body = """
            <h1>Welcome!</h1>
            %(user_info)s
            <h1>Actions</h1>
            <ul>
            %(list)s
            </ul>
            """ % {"user_info": user_info, "list": listize(ACTIONS)}
            return XHTML_TEMPLATE % {"TITLE": "Main Menu", "BODY": body}
    
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
