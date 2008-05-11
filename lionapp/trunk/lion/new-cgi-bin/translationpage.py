from util import *
from Cheetah.Template import Template
os.sys.path.append("./templates")
import translate

VIEW_DESCRIPTIONS = {"all": "all items", 
    "newtodo": "all items marked new or to-do", 
    "new": "all new items", 
    "todo": "all to-do items"}

#TODO: make this have "translate.tmpl" as its base class and avoid
#the redundant t.attribute value-setting
class TranslationPage():
    """The base class for a page of items to be translated"""
    handler = "save_string"
    view_description = None
    about = None
    title = None
    section = None
    language = None
    user = None
    textbox_columns = 0
    textbox_rows = 0
    instructions = None
    roles_sql = None
    last_view = None
    
    def index(self, view):
        """Show the big table of translate-able items"""
        self.last_view = view
        user = get_user()
        if user == None:
            return Template(file="error.tmpl")
        self.language = user["languages.langname"]
        self.user = user
        self.view_description = VIEW_DESCRIPTIONS[view]
        t = Template(file="./templates/translate.tmpl")
        t.actions = ("<a href=\"../TranslateStrings?view=all\">Translate AMIS strings</a>", 
            "Assign AMIS keyboard shortcuts",
            "<a href=\"../ChooseMnemonics?view=all\">Choose mnemonics</a> \
                (single-letter shortcuts)")
        t.about = self.about
        t.language = self.language
        t.form, t.count = self.make_table(view)
        t.view_description = self.view_description
        t.section = self.section
        return str(t)
    index.exposed = True
    
    def save_string(self, translation, remarks, status, xmlid, langid):
        table = langid.replace("-", "_")
        db = connect_to_lion_db("rw")
        cursor = db.cursor()
        request = """UPDATE %(table)s SET textflag="%(status)s", \
            textstring="%(translation)s", remarks="%(remarks)s" WHERE \
            xmlid="%(xmlid)s" """ % \
            {"table": table, "status": status, "translation": translation, \
                "remarks": remarks, "xmlid": xmlid}
        cursor.execute(request)
        cursor.close()
        db.close()
        return self.index(self.last_view)
    save_string.exposed = True
        
    def get_sql_for_view_filter(self, view_filter, table):
        sql = ""
        if view_filter == "new":
            sql = "and %s.textflag=3" % table 
        elif view_filter =="todo":
            sql = "and %s.textflag=2" % table
        elif view_filter == "newtodo":
            sql = "and (%s.textflag=2 or %s.textflag=3)" % table
        else:
            sql = ""
        return sql
    
    def make_fields(self, table):
        """format a list of fields, with or without the table prefix"""
        # get the xmlid, textstring, textflag, remarks from the localized table
        # get the textstring and remarks from the english table
        if table != "": table = "%s." % table
        return []
