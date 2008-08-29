import MySQLdb
import util
import daisylion.liondb.dbsession
from templates import translate, error

VIEW_DESCRIPTIONS = {"all": "all items", 
    "newtodo": "all items marked new or to-do", 
    "new": "all new items", 
    "todo": "all to-do items"}

class TranslationPage(translate.translate):
    """The base class for a page of items to be translated"""
    last_view = None
    roles_sql = None
    user = None
    warning_links = None
    warning_message = ""
    check_conflict = False
    show_no_conflicts = False
    pagenum = 0
    items_per_page = 50
    total_num_items = 0
    session = None
    pagenum = 0
    
    def __init__(self, session, host, port, masterlang):
        self.session = session
        self.host = host
        self.port = port
        self.masterlang = masterlang
        session.execute_query("""SELECT langname from languages WHERE langid="%s" """ \
            % masterlang)
        self.masterlangname = session.cursor.fetchone()[0]
        translate.translate.__init__(self)
    
    def index(self, view, id_anchor = ""):
        """Show the big table of translate-able items"""
        self.last_view = view
        user = util.get_user(self.session)
        if user == None:
            return error.error().respond()
        self.user = user
        self.language = user["languages.langname"]
        self.translate_for_keyboard = user["languages.translate_for_keyboard"]
        self.view_description = VIEW_DESCRIPTIONS[view]
        self.form, self.count = self.make_table(view, self.pagenum)
        self.targetid = id_anchor
        # calculate the num pages for the base class
        self.total_num_pages = self.get_total_num_pages()
            
        return self.respond()
    index.exposed = True
    
    def change_view(self, viewfilter):
        return self.index(viewfilter)
    change_view.exposed = True
    
    def save_string(self, translation, remarks, status, xmlid, langid, pagenum):
        table = langid.replace("-", "_")
        request = """UPDATE %(table)s SET textflag="%(status)s", \
            textstring="%(translation)s", remarks="%(remarks)s" WHERE \
            xmlid="%(xmlid)s" """ % \
            {"table": table, "status": status, "translation": MySQLdb.escape_string(translation), \
                "remarks": MySQLdb.escape_string(remarks), "xmlid": xmlid}
        self.session.execute_query(request)
        self.show_no_conflicts = False
        self.pagenum = int(pagenum)
        self.session.trace_msg("On page %d" % self.pagenum)
        return self.index(self.last_view, xmlid)
    save_string.exposed = True
        
    def get_sql_for_view_filter(self, view_filter, table):
        sql = ""
        if view_filter == "new":
            sql = "and %s.textflag=3" % table 
        elif view_filter =="todo":
            sql = "and %s.textflag=2" % table
        elif view_filter == "newtodo":
            sql = "and (%(table)s.textflag=2 or %(table)s.textflag=3)" % \
                {"table": table}
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
            return self.index(self.last_view)
        else:
            return None
    next_page.exposed = True
    
    def previous_page(self):
        if self.pagenum - 1 >= 0 and self.pagenum - 1 < self.get_total_num_pages():
            self.pagenum -= 1        
            self.session.trace_msg("Going to the previous page (%d)" % self.pagenum)
            return self.index(self.last_view)
        else:
            return None
    previous_page.exposed = True
    
    def change_page(self, pagenum):
        self.session.trace_msg("Change page to %d" % int(pagenum))
        if int(pagenum) >= 0 and int(pagenum) < self.get_total_num_pages():
            self.pagenum = int(pagenum)        
            return self.index(self.last_view)
        else:
            return None
    change_page.exposed = True
    
    def make_table_name(self, langid):
        """This is a duplicate of the liondb/liondb.py function.  It will disappear soon as integration improves. """
        return langid.replace("-", "_")

        