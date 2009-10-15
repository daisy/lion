import os
import cherrypy
import daisylion.db.liondb
import util
import math
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
        self.prompts_uri = ""
        batchofprompts.batchofprompts.__init__(self)
    
    def index(self):
        """Show the page"""
        user = util.get_user(self.session)
        if user == None:
            e = errorpage.ErrorPage(self.session, "Login error")
            return e.index()
        self.user = user
        self.language = user["languages.langname"]
        self.prompts_uri = self.generate_prompts_zipfile()
        return self.respond()
    index.exposed = True
    
    def generate_prompts_zipfile(self):
        """Generate a zipfile of all the prompts and offer it to the user for download
        return the uri of the zipfile"""
        strings_length = self.session.all_strings_length(self.user["users.langid"])
        midpoint = int(math.floor(strings_length/2))
        
        strings_xml_part_one = \
            self.__generate_prompts_as_xhtml(self.user["users.langid"], 0, midpoint)
        strings_xml_part_two = \
            self.__generate_prompts_as_xhtml(self.user["users.langid"], midpoint+1, strings_length-1)
        
        # put in the temp_audio_dir, which should actually be called the "temp_anything_dir"
        if not self.temp_audio_dir.endswith("/"): self.temp_audio_dir += "/"
        tempdir = self.temp_audio_dir + self.user["users.langid"] + "/"
        if not os.path.exists(tempdir) or not os.path.isdir(tempdir):
            os.mkdir(tempdir)
            os.popen("chmod o+r %s" % tempdir)
        outfilename_one = os.path.join(tempdir, "amis_prompts_part_one.html")
        file = open(outfilename_one, "w")
        file.write(strings_xml_part_one)
        file.close()
        
        outfilename_two = os.path.join(tempdir, "amis_prompts_part_two.html")
        file = open(outfilename_two, "w")
        file.write(strings_xml_part_two)
        file.close()
        
        zipfilename = "%s_prompts.zip" % self.user["users.langid"]
        zipfilepath = os.path.join(tempdir, zipfilename)
        zipfileuri = "%s/%s/%s" % (self.session.config["main"]["temp_audio_uri"], \
            self.user["users.langid"], zipfilename)
        os.popen("zip -j %s %s %s" % (zipfilepath, outfilename_one, outfilename_two))
        return zipfileuri
      
    generate_prompts_zipfile.exposed = True
    
    def __generate_prompts_as_xhtml(self, langid, start_index, end_index):
        strings_xml = self.session.all_strings(langid, start_index, end_index)
        tmpfile = "/tmp/" + self.user["users.langid"] + "-strings"
        file = open(tmpfile, "w")
        file.write(strings_xml)
        file.close()
        xslt = "http://" + self.host + ":" + str(self.port) + "/xslt/obi_xhtml.xslt"
        strings_xhtml = ""
        for i in os.popen("xsltproc %s %s" % (xslt, tmpfile)):
            strings_xhtml += i
        return strings_xhtml
    
    def upload_zipfiles_of_prompts(self, infile1, infile2):
        """Accept two zipfiles of prompts + ncx file"""
        self.__upload_zipfile_of_prompts(infile1)
        self.__upload_zipfile_of_prompts(infile2)
        raise cherrypy.InternalRedirect("UploadComplete")
    
    upload_zipfiles_of_prompts.exposed = True
        
    def __upload_zipfile_of_prompts(self, infile):
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
        
        self.process_upload(outfilename, tempdir)
    
    
    def process_upload(self, zipfile, tempdir):
        """Import their prompts book into the system"""
        # unzip into a directory of the same name
        os.popen("unzip -o -j \"%s\" -d \"%s\"" % (zipfile, os.path.splitext(zipfile)[0]))
        
        # get ('/blah/blah/file', '.ext')
        a, b = os.path.splitext(zipfile)
        ncx = os.path.join(a, "obi_dtb.ncx")
        # run the db import script
        self.session.import_audio_prompts(self.user["users.langid"], ncx, True)
        # move all the mp3 files into the language directory
        os.popen("mv \"%s/*.mp3\" \"%s\"" % (a, tempdir))
        self.session.trace_msg("Uploaded file processed")

        
class UploadComplete(uploadcomplete.uploadcomplete):
    """This is shown when the zipfile upload has completed"""
    def __init__(self, session):
        self.session = session
        self.appid = self.session.config["main"]["target_app"]
        self.host = self.session.config["main"]["webhost"]
        self.port = self.session.config["main"]["webport"]
        self.appname, self.appversion, self.appdesc, self.appsite, self.applogo, \
            self.comments = util.get_application_data(self.session)
        uploadcomplete.uploadcomplete.__init__(self)

    def index(self):
        return self.respond()
    index.exposed = True
