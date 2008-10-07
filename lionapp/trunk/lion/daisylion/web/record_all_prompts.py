import os
import daisylion.db.liondb
import util
from templates import batchofprompts, error

class RecordAllPrompts(batchofprompts.batchofprompts):
    user = None
    session = None
    
    def __init__(self, session):
        self.session = session
        self.host = self.session.config["main"]["webhost"]
        self.port = self.session.config["main"]["webport"]
        self.error = ""
        self.error_id = ""
        self.warnings = ""
        batchofprompts.batchofprompts.__init__(self)
    
    def index(self):
        """Show the page"""
        user = util.get_user(self.session)
        if user == None:
            return error.error().respond()
        self.user = user
        self.language = user["languages.langname"]
        return self.respond()
    index.exposed = True
    
    def generate_prompts_as_xhtml(self):
        """Generate an XHTML file of all the prompts and offer it to the user for download"""
        strings_xml = self.session.all_strings(self.user["users.langid"])
        tmpfile = "/tmp/" + self.user["users.langid"] + "-strings"
        file = open(tmpfile, "w")
        file.write(strings_xml)
        file.close()
        xslt = "http://" + self.host + ":" + str(self.port) + "/xslt/obi_xhtml.xslt"
        strings_xhtml = ""
        for i in os.popen("xsltproc %s %s" % (xslt, tmpfile)):
            strings_xhtml += i
        return strings_xhtml
    generate_prompts_as_xhtml.exposed = True
    
    def upload_zipfile_of_prompts(self, zipfile):
        """Accept a zipfile of the prompts + ncx file."""
        return """<h1>O HAI!</h1> <p><a href="../MainMenu">Back to the main menu</a></p>"""
    upload_zipfile_of_prompts.exposed = True
