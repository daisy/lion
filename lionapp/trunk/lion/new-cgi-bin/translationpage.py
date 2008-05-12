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
    
    def index(self, view):
        """Show the big table of translate-able items"""
        self.last_view = view
        user = util.get_user()
        if user == None:
            return error.error().respond()
        self.user = user
        self.language = user["languages.langname"]
        print "view " + str(view)
        self.view_description = VIEW_DESCRIPTIONS[view]
        self.form, self.count = self.make_table(view)
        return self.respond()
    index.exposed = True
    
    def change_view(self, viewfilter):
        return self.index(viewfilter)
    change_view.exposed = True
    
    def save_string(self, translation, remarks, status, xmlid, langid, prefix):
        table = langid.replace("-", "_")
        db = util.connect_to_lion_db("rw")
        cursor = db.cursor()
        request = """UPDATE %(table)s SET textflag="%(status)s", \
            textstring="%(translation)s", remarks="%(remarks)s" WHERE \
            xmlid="%(xmlid)s" """ % \
            {"table": table, "status": status, "translation": prefix + translation, \
                "remarks": remarks, "xmlid": xmlid}
        cursor.execute(request)
        cursor.close()
        db.close()
        self.show_no_conflicts = False
        return self.index(self.last_view)
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
