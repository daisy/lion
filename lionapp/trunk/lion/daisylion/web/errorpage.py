from templates import error

class ErrorPage(error.error):
    """General error"""
    def __init__(self, session, title):
        self.session = session
        self.host = self.session.config["main"]["webhost"]
        self.port = self.session.config["main"]["webport"]
        self.title = title
        error.error.__init__(self)
    
    def index(self):
        """Show the links for the main menu"""
        return self.respond()
    index.exposed = True

