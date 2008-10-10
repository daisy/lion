import os
import cherrypy
import daisylion.db.liondb
import util
from templates import batchofprompts, error, uploadcomplete

class RecordAllPrompts(batchofprompts.batchofprompts):
    user = None
    session = None
    
    def __init__(self, session):
        self.session = session
        self.host = self.session.config["main"]["webhost"]
        self.port = self.session.config["main"]["webport"]
        self.temp_audio_dir = self.session.config["main"]["temp_audio_dir"]
        self.error = ""
        self.error_id = ""
        self.warnings = ""
        batchofprompts.batchofprompts.__init__(self)
    
    def index(self):
        """Show the page"""
        user = util.get_user(self.session)
        if user == None:
            e = errorpage.ErrorPage(self.session, "Login error")
            return e.index()
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
    
    def upload_zipfile_of_prompts(self, infile):
        """Accept a zipfile of the prompts + ncx file."""
        self.session.trace_msg("Zipfile upload = %s" % infile.filename)
        self.session.trace_msg("type of file %s" % type(infile.filename))
        size = 0
        # calculate the filesystem path to the temporary file storage
        if not self.temp_audio_dir.endswith("/"): self.temp_audio_dir += "/"
        tempdir = self.temp_audio_dir + self.user["users.langid"] + "/"
        if not os.path.exists(tempdir) or not os.path.isdir(tempdir):
            os.mkdir(tempdir)
            os.popen("chmod o+r %s" % tempdir)
        outfilename = os.path.join(tempdir, infile.filename)
        self.session.trace_msg("Going to save to %s" % outfilename)
        outfile = file (outfilename, 'wb')
        
        while 1:
            data = infile.file.read(8192)
            if not data: break
            else: outfile.write(data)
            size += len(data)
        
        if size == 0:
            self.session.warn("Uploaded file size is 0")
        else:
            self.session.trace_msg("Uploaded file %s, %d bytes" % (outfile.name, size))
        outfile.close()
        
        # TODO: show a "processing..." page
        
        self.process_upload(outfilename, tempdir)
        raise cherrypy.InternalRedirect("UploadComplete")
    upload_zipfile_of_prompts.exposed = True
    
    def process_upload(self, zipfile, tempdir):
        """Import their prompts book into the system"""
        # unzip into a directory of the same name
        os.popen("unzip -o %s -d %s" % (zipfile, os.path.dirname(zipfile)))
        
        # get ('/blah/blah/file', '.ext')
        a, b = os.path.splitext(zipfile)
        ncx = os.path.join(a, "obi_dtb.ncx")
        # run the db import script
        self.session.import_audio_prompts(self.user["users.langid"], ncx, True)
        # move all the mp3 files into the language directory
        os.popen("mv %s/*.mp3 %s" % (a, tempdir))
        self.session.trace_msg("Uploaded file processed")

        
class UploadComplete(uploadcomplete.uploadcomplete):
    """This menu gives the tasks for the translators"""
    def __init__(self, session):
        self.session = session
        self.application = self.session.config["main"]["target_app"]
        self.host = self.session.config["main"]["webhost"]
        self.port = self.session.config["main"]["webport"]
        self.appname, self.appversion, self.appdesc, self.appsite, self.applogo = \
            util.get_application_data(self.session)
        uploadcomplete.uploadcomplete.__init__(self)

    def index(self):
        return self.respond()
    index.exposed = True
