from translationpage import *
from templates import tablerow
import util

class TranslateStrings(TranslationPage):
    """The page of all the strings (the main page)"""
    def __init__(self, session):
        self.section = "main"
        self.textbox_columns = 64
        self.textbox_rows = 3
        self.instructions = "Enter the translation below."
        self.about = "This is the main page.  All the strings to be translated\
         for the AMIS interface are on this page."
        self.warning_links = None
        self.check_conflict = False
        self.warning_message = None
        self.usepages = True
        TranslationPage.__init__(self, session)
    
    def make_table(self, view_filter, pagenum):
        """Make the form for main page"""
        table = self.make_table_name(self.user["users.langid"])
        mtable = self.make_table_name(self.masterlang)
        langid = self.user["users.langid"]
        textflags_sql = self.get_sql_for_view_filter(view_filter, table)
        template_fields = ["xmlid", "textstring", "textflag", "remarks", 
            "ref_string", "our_remarks"]
        
        dbfields = ["%s.xmlid" % table, "%s.textstring" % table, 
            "%s.textflag" % table, "%s.remarks" % table, "%s.textstring" % mtable, 
            "%s.remarks" % mtable]
        
        request = """SELECT %(fields)s FROM %(table)s, %(mastertable)s WHERE %(table)s.\
            xmlid=%(mastertable)s.xmlid AND %(table)s.translate=1 AND \
            (%(table)s.role="STRING" OR %(table)s.role="CONTROL" OR \
            %(table)s.role="DIALOG" OR %(table)s.role="MENUITEM") \
            %(where_flags)s""" % \
            {"fields": ",".join(dbfields), "table": table, 
                "where_flags": textflags_sql, "mastertable": mtable}
        self.session.execute_query(request)
        rows = self.session.cursor.fetchall()
        self.total_num_items = len(rows)
        start, end = self.calculate_range(pagenum)
        self.session.trace_msg("Range for page %d: %d, %d" % (pagenum, start, end))
        form = "<table>"
        for i in range(start, end):
            r = rows[i]
            data = dict(zip(template_fields, r))
            t = tablerow.tablerow(searchList=data)
            t.instructions = self.instructions
    	    t.width = self.textbox_columns
    	    t.height = self.textbox_rows
    	    t.langid = self.user["users.langid"]
    	    t.pagenum = pagenum
    	    t.audiouri = self.get_current_audio_uri(data["xmlid"], self.user["users.langid"])
            form = form + t.respond()
        form = form + "</table>"
        return form, len(rows)