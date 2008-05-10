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
        return login_form()
    index.exposed = True
    
    def process_login(self, username, password):
        if login(username, password) == None:
            return login_error()
        else:
            return login_success()
    
    process_login.exposed = True

class MainMenu():
    def index(self):
        """Show the links for the main menu"""
        user = get_user()
        if user == None:
            return general_error()
        else:
            return main_menu_links(get_user())
    
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
