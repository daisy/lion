import os
import os.path
import MySQLdb
import util
import daisylion.db.liondb
from templates import translate, error
import cherrypy
from cherrypy.lib import static
import keys
import inspect

VIEW_DESCRIPTIONS = {"all": "all items", 
    "newtodo": "all items marked new or to-do", 
    "new": "all new items", 
    "todo": "all to-do items", 
    "allok": "all completed items"}

class TranslationPage(translate.translate):
    """The base class for a page of items to be translated
    This class is not directly usable as a page; use a subclassed page instead"""
    last_view = None
    roles_sql = None
    user = None
    pagenum = 0
    items_per_page = 50
    total_num_items = 0
    session = None
    pagenum = 0
    url = None
    
    def __init__(self, session):
        self.session = session
        self.appid = self.session.config["main"]["target_app"]
        self.host = self.session.config["main"]["webhost"]
        self.port = self.session.config["main"]["webport"]
        self.masterlang = self.session.config["main"]["masterlang"]
        self.audio_support = self.session.config["main"]["audio_support"]
        session.execute_query("""SELECT langname from languages WHERE langid="%s" """ \
            % self.masterlang)
        self.masterlangname = session.cursor.fetchone()[0]
        self.temp_audio_dir = self.session.config["main"]["temp_audio_dir"]
        self.temp_audio_uri = self.session.config["main"]["temp_audio_uri"]
        self.error = ""
        self.error_id = ""
        self.warnings = ""
        self.appname, self.appversion, self.appdesc, self.appsite, self.applogo, \
            self.comments = util.get_application_data(self.session)
    
        self.url_string = "../%s?view=%s&id_anchor=%s"
        
        translate.translate.__init__(self)
    
    def index(self, view, id_anchor = ""):
        """Show the big table of translate-able items"""
        self.last_view = view
        user = util.get_user(self.session)
        if user == None:
            e = errorpage.ErrorPage(self.session, "Login error")
            return e.index()
        self.user = user
        self.language = user["languages.langname"]
        self.view_description = VIEW_DESCRIPTIONS[view]
        self.form, self.count = self.make_table(view, self.pagenum)
        self.targetid = id_anchor
        # calculate the num pages for the base class
        self.total_num_pages = self.get_total_num_pages()
        self.warnings = self.get_all_warnings()
        self.translate_mnemonics, self.translate_accelerators = \
            keys.get_keyboard_translation_flags(self.session)
        
        return self.respond()
    index.exposed = True
    
    def change_view(self, viewfilter):
        # reset the page number when switching the view
        if self.last_view != None:
            if self.last_view != viewfilter:
                self.pagenum = 0
        
        self.last_view = viewfilter
        self.redirect()
    change_view.exposed = True
    
    def save_data(self, translation, remarks, xmlid, langid, pagenum, audiofile, status=1):
        table = langid.replace("-", "_")
        is_valid, msg = self.validate_single_item(translation, xmlid, langid)
        self.error, self.error_id = msg, xmlid
        if is_valid:
            request = """UPDATE %(table)s SET status="%(status)s", \
                textstring="%(translation)s", remarks="%(remarks)s" WHERE \
                xmlid="%(xmlid)s" """ % \
                {"table": table, "status": status, "translation": MySQLdb.escape_string(translation.strip()), \
                    "remarks": MySQLdb.escape_string(remarks), "xmlid": xmlid}
            self.session.execute_query(request)
            if audiofile != None and audiofile != "" and audiofile.filename != "": 
                self.save_audio(audiofile, langid, xmlid)
        self.pagenum = int(pagenum)
        self.redirect(xmlid)
    save_data.exposed = True
    
    def save_audio(self, infile, langid, xmlid):
        infilename = os.path.basename(infile.filename.replace("\\", "/"))
        self.session.trace_msg("infile = %s" % infile)
        self.session.trace_msg("type of infile %s" % type(infile))
        size = 0
        
        save_dir, www_dir = self.session.get_tempaudio_paths(langid)
        if not os.path.exists(save_dir) or not os.path.isdir(save_dir):
            os.mkdir(save_dir)
        
        outfilename = os.path.join(save_dir, infilename)
        self.session.trace_msg("Going to save to %s" % outfilename)
        outfile = file (outfilename, 'wb')
        www_filename = www_dir + infilename
        
        while 1:
            data = infile.file.read(8192)
            if not data: break
            else: outfile.write(data)
            size += len(data)
        
        if size == 0:
            self.session.warn("Uploaded file size is 0")
        else:
            self.session.trace_msg("Uploaded file %s, %d bytes" % (outfile.name, size))
            self.session.write_tempaudio(xmlid, langid, www_filename)
    
    def get_sql_for_view_filter(self, view_filter, table):
        sql = ""
        if view_filter == "new":
            sql = "and %s.status=3" % table 
        elif view_filter =="todo":
            sql = "and %s.status=2" % table
        elif view_filter == "newtodo":
            sql = "and (%(table)s.status=2 or %(table)s.status=3)" % \
                {"table": table}
        elif view_filter == "allok":
            sql = "and (%s.status=1)" % table
        else:
            sql = ""
        return sql
    
    def get_total_num_pages(self):
        total_num_pages = self.total_num_items/self.items_per_page
        # add another page for any remaining items
        if self.total_num_items % self.items_per_page != 0:
            total_num_pages += 1
        return total_num_pages
    
    def calculate_range(self, pagenum):
        """returns a start and end point.  everything is 0-based."""
        total_num_pages = self.get_total_num_pages()    
        # make sure the page is in range
        if pagenum >= 0 and pagenum < total_num_pages:
            start = (pagenum + 1) * self.items_per_page - self.items_per_page
            if pagenum == total_num_pages - 1 and \
                self.total_num_items % self.items_per_page != 0:
                    end = start + (self.total_num_items % self.items_per_page)
            else:
                end = start + self.items_per_page
            return start, end
        else:
            return 0, 0
    
    def next_page(self):
        if self.pagenum + 1 >= 0 and self.pagenum + 1 < self.get_total_num_pages():
            self.pagenum += 1        
            self.session.trace_msg("Going to the next page (%d)" % self.pagenum)
            self.redirect()
        else:
            return None
    next_page.exposed = True
    
    def previous_page(self):
        if self.pagenum - 1 >= 0 and self.pagenum - 1 < self.get_total_num_pages():
            self.pagenum -= 1        
            self.session.trace_msg("Going to the previous page (%d)" % self.pagenum)
            self.redirect()
        else:
            return None
    previous_page.exposed = True
    
    def change_page(self, pagenum):
        self.session.trace_msg("Change page to %d" % int(pagenum))
        if int(pagenum) >= 0 and int(pagenum) < self.get_total_num_pages():
            self.pagenum = int(pagenum)        
            self.redirect()
        else:
            return None
    change_page.exposed = True
        
    def get_current_audio_uri(self, xmlid, langid):
        """utility function to build the most current audio uri
           if there is anything in the tempaudio table, it is considered the most current.
           otherwise the audiouri from the specified language table is used, and constructed as a uri
           using the permanenturi + filename + permanenturiparams format
           e.g. http://stuff.com/file.mp3?format=raw
           where permanenturi and permanenturiparams come from the db's languages overview table
        """
        if self.audio_support == False: return ""
        
        # find out if there is an audiouri for this item in the tempaudio table
        audiouri = ""
        request = """SELECT audiouri FROM tempaudio WHERE xmlid="%s" and langid="%s" """ % \
            (xmlid, langid)
        self.session.execute_query(request)
        if self.session.cursor.rowcount > 0:
            audiouri = self.session.cursor.fetchone()[0]
        # otherwise use the audiouri from the language table
        else:
            # get the full path to the files' permanent directory.  we need it because audiouris from language
            # tables are relative
            # This is split in two: the directory/param part is from
            # the application table, plus a language-specific directory part.
            request = """SELECT audiodir FROM languages WHERE langid="%s" """ %\
                self.user["users.langid"]
            self.session.execute_query(request)
            audiodir, = self.session.cursor.fetchone()
            # there might not be any permanent audio repository
            if audiodir != None:
                request = """SELECT permanenturi, permanenturiparams FROM
                application WHERE appid="%s" """ % self.appid
                self.session.execute_query(request)
                permanenturi, permanenturiparams = self.session.cursor.fetchone()
                # now select the audiouri itself
                request = """SELECT audiouri FROM %s WHERE xmlid="%s" """ % \
                    (self.session.make_table_name(langid), xmlid)
                self.session.execute_query(request)
                audiouri = self.session.cursor.fetchone()[0]
                if audiouri != None and audiouri != "":
                    # concatenate the uri strings
                    if permanenturi != "" and not permanenturi.endswith("/"):
                	    permanenturi += "/"
                    if audiouri.startswith("./"):
                	    audiouri = audiouri[2:]
                    if audiodir != "" and not audiodir.endswith("/"):
                        audiodir += "/"
                    audiouri = permanenturi + audiodir + audiouri + permanenturiparams
        return audiouri
    
    def make_table(self, view, page_number):
        """The subclasses must override this function"""
        return NotImplemented
    
    def validate_single_item(self, data, xmlid, langid):
        """The subclass must override this function, which returns a value and a message.
        Validation can include checking characters and data length, and also
        reporting on valid but conflicting data.
        This function is called before the data is stored"""
        return (NotImplemented, "Not implemented")
    
    def get_all_warnings(self):
        """This function generates a summary of warnings for the section.
        It uses data that has already been saved.
        It returns a string"""
        return "BASE CLASS"

    def redirect(self, id=""):
        raise cherrypy.InternalRedirect(self.url_string % (self.url, self.last_view, id))
