from translationpage import *
from templates import tablerow
import util

class TranslateStrings(TranslationPage):
    """The page of all the strings (the main page)"""
    def __init__(self):
        self.section = "main"
        self.textbox_columns = 64
        self.textbox_rows = 3
        self.instructions = "Enter the translation below."
        self.about = "This is the main page.  All the strings to be translated\
         for the AMIS interface are on this page."
        self.warning_links = None
        self.check_conflict = False
        self.warning_message = None
        self.pagenum = 1
        self.usepages = True
        #this is weird but necessary .. otherwise cheetah complains
        TranslationPage.__init__(self)
    
    def make_table(self, view_filter, pagenum):
        """Make the form for main page"""
        table = self.user["users.langid"].replace("-", "_")
        langid = self.user["users.langid"]
        textflags_sql = self.get_sql_for_view_filter(view_filter, table)
        template_fields = ["xmlid", "textstring", "textflag", "remarks", 
            "ref_string", "our_remarks"]
        dbfields = ["%s.xmlid" % table, "%s.textstring" % table, 
            "%s.textflag" % table, "%s.remarks" % table, "eng_US.textstring", 
            "eng_US.remarks"]
        
        request = """SELECT %(fields)s FROM %(table)s, eng_US WHERE %(table)s.\
            xmlid=eng_US.xmlid AND %(table)s.translate=1 AND \
            (%(table)s.role="STRING" OR %(table)s.role="CONTROL" OR \
            %(table)s.role="DIALOG" OR %(table)s.role="MENUITEM") \
            %(where_flags)s""" % \
            {"fields": ",".join(dbfields), "table": table, 
                "where_flags": textflags_sql}
        print request
        db = util.connect_to_lion_db("ro")
        cursor=db.cursor()
        cursor.execute(request)
        rows = cursor.fetchall()
        cursor.close()
        db.close()
        
        form = "<table>"
        start = 0
        end = 0
        count = 0
        if pagenum == 1:
            start = 0
            end = len(rows) / 2
        else:
            start = len(rows) / 2 + 1
            end = len(rows)
        for r in rows:
            if count >= start and count <= end:
                t = tablerow.tablerow(searchList=dict(zip(template_fields, r)))
                t.instructions = self.instructions
    	        t.width = self.textbox_columns
    	        t.height = self.textbox_rows
    	        t.langid = self.user["users.langid"]
                form += t.respond()
                count += 1
        form += "</table>"
        return form, count