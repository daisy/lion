from translationpage import *

class TranslateStrings(TranslationPage):
    """The page of all the strings (the main page)"""
    def __init__(self):
        self.section = "main"
        self.textbox_columns = 64
        self.textbox_rows = 3
        self.instructions = "Enter the translation:"
        self.about = "This is the main page.  All the strings to be translated\
         for the AMIS interface are on this page."
            
        # the other pages (mnemonics, accelerators) will need this sql:
        #"mnemonics": """ and %(table)s.role="MNEMONIC" """, 
        #"accelerators": """ and %(table)s.role="ACCELERATOR" """}

    def make_table(self, view_filter):
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
            xmlid=eng_US.xmlid AND (%(table)s.role="STRING" OR \
                    %(table)s.role="CONTROL" OR %(table)s.role="DIALOG" OR \
                    %(table)s.role="MENUITEM") %(where_flags)s""" % \
            {"fields": ",".join(dbfields), "table": table, 
                "where_flags": textflags_sql}

        db = connect_to_lion_db("ro")
        cursor=db.cursor()
        cursor.execute(request)
        rows = cursor.fetchall()
        cursor.close()
        db.close()

        
        form = "<table>"
        for r in rows:
            t = Template(file="./templates/tablerow.tmpl", 
                searchList=dict(zip(template_fields, r)))
            t.instructions = self.instructions
    	    t.width = self.textbox_columns
    	    t.height = self.textbox_rows
    	    t.langid = self.user["users.langid"]
    	    t.handler = self.handler
            form += str(t)
        form += "</table>"
        return form, len(rows)