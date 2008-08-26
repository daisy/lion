import MySQLdb
import util
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
    def index(self, view, id_anchor = ""):
        """Show the big table of translate-able items"""
        self.last_view = view
        user = util.get_user()
        if user == None:
            return error.error().respond()
        self.user = user
        self.language = user["languages.langname"]
        self.translate_for_keyboard = user["languages.translate_for_keyboard"]
        self.view_description = VIEW_DESCRIPTIONS[view]
        self.form, self.count = self.make_table(view, self.pagenum)
        print "made table"
        self.targetid = id_anchor
        return self.respond()
    index.exposed = True
    
    def change_view(self, viewfilter):
        return self.index(viewfilter)
    change_view.exposed = True
    
    def save_string(self, translation, remarks, status, xmlid, langid):
        table = langid.replace("-", "_")
        db = util.connect_to_lion_db("rw")
        cursor = db.cursor()
        request = """UPDATE %(table)s SET textflag="%(status)s", \
            textstring="%(translation)s", remarks="%(remarks)s" WHERE \
            xmlid="%(xmlid)s" """ % \
            {"table": table, "status": status, "translation": MySQLdb.escape_string(translation), \
                "remarks": remarks, "xmlid": xmlid}
        cursor.execute(request)
        cursor.close()
        db.close()
        self.show_no_conflicts = False
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
    
    def make_fields(self, table):
        """format a list of fields, with or without the table prefix"""
        # get the xmlid, textstring, textflag, remarks from the localized table
        # get the textstring and remarks from the english table
        if table != "": table = "%s." % table
        return []
    
    def get_total_num_pages(self):
        total_num_pages = self.total_num_items/self.items_per_page
        # add another page for any remaining items
        if self.total_num_items % self.items_per_page != 0:
            total_num_pages += 1
        return total_num_pages
    
    def calculate_range(self, pagenum):
        """returns a start and inclusive end point"""
        total_num_pages = self.get_total_num_pages()    
        # make sure the page is in range
        if pagenum > 0 and pagenum <= total_num_pages:
            start = pagenum * self.items_per_page - self.items_per_page
            end = start + self.items_per_page - 1
            return start, end
        else:
            return 0, 0
    
    def next_page(self):
        print "next page"
        if self.pagenum + 1 > 0 and self.pagenum + 1 <= self.get_total_num_pages():
            self.pagenum += 1        
            return self.index(self.last_view)
        else:
            return None
    next_page.exposed = True
    
    def previous_page(self):
        print "previous page"
        if self.pagenum - 1 > 0 and self.pagenum - 1 <= self.get_total_num_pages():
            self.pagenum -= 1        
            return self.index(self.last_view)
        else:
            return None
    previous_page.exposed = True
    
    def change_page(self, pagenum):
        print "change page %d" % int(pagenum)
        if int(pagenum) > 0 and int(pagenum) <= self.get_total_num_pages():
            self.pagenum = int(pagenum)        
            return self.index(self.last_view)
        else:
            return None
    change_page.exposed = True