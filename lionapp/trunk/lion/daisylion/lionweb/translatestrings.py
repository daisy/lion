from translationpage import *
from templates import tablerow
import util

class TranslateStrings(TranslationPage):
    """The page of all the strings (the main page)"""
    def __init__(self, session, config):
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
        #this is weird but necessary .. otherwise cheetah complains
        TranslationPage.__init__(self, session, config)
    
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
            search_list = dict(zip(template_fields, r))
            t = tablerow.tablerow(searchList=search_list)
            t.instructions = self.instructions
    	    t.width = self.textbox_columns
    	    t.height = self.textbox_rows
    	    t.langid = self.user["users.langid"]
    	    t.pagenum = pagenum
    	    # find out if there is an audiouri for this item in the tempaudio table
            audiouri = ""
            request = """SELECT audiouri FROM tempaudio WHERE xmlid="%s" and langid="%s" """ % \
                (search_list["xmlid"], self.user["users.langid"])
            self.session.execute_query(request)
            if self.session.cursor.rowcount > 0:
                audiouri = self.session.cursor.fetchone()[0]
            # otherwise use the audiouri from the language table
            else:
                # get the full path to the files' permanent directory.  we need it because audiouris from language
                # tables are relative
                request = """SELECT permanenturi, permanenturiparams FROM languages 
                    WHERE langid="%s" """ % self.user["users.langid"]
                self.session.execute_query(request)
                permanenturi, permanenturiparams = self.session.cursor.fetchone()
                # now select the audiouri itself
                request = """SELECT audiouri FROM %s WHERE xmlid="%s" """ % \
                    (self.make_table_name(self.user["users.langid"]), search_list["xmlid"])
                self.session.execute_query(request)
                audiouri = self.session.cursor.fetchone()[0]
                # concatenate the uri strings
                if permanenturi != "" and not permanenturi.endswith("/"):
                	permanenturi += "/"
                if audiouri.startswith("./"):
                	audiouri = audiouri[2:]
                audiouri = permanenturi + audiouri + permanenturiparams
            t.audiouri = audiouri
    	    form = form + t.respond()
        form = form + "</table>"
        return form, len(rows)