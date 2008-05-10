from templates import *
from util import *

class TranslateStrings():
    def __init__(self):
        self.actions = separate(ACTIONS)
        self.description = "Viewing all items."
        self.about = "This is the main page.  All the strings to be translated\
         for the AMIS interface are on this page."
    
    def index(self, view):
        """Show the big table of translate-able items"""
        user = get_user()
        if user == None:
            return general_error()
        form, numrows = self.make_main_form_table(user, view)
        title = TITLE_TEMPLATE % {"lang": user["languages.langname"], "section": "main"}
        
        page_html = BODY_TEMPLATE_HTML % {"title": title, "message": self.description, 
            "about_section": self.about,"num_items": numrows, "warning": "", "form": form,
            "specialform": "", "actions": self.actions}
        
        return XHTML_TEMPLATE % {"TITLE": title, "BODY": page_html}
    index.exposed = True
    
    def save_string(self, translation, remarks, status, xmlid, dataprefix, langid):
        return "@TODO"
    
    save_string.exposed = True
        
    def make_main_form_table(self, user, view_filter):
        """Make the form for main page"""
        # get the xmlid, textstring, textflag, remarks from the localized table
        # get the textstring and remarks from the english table
        table = user["users.langid"].replace("-", "_")
        langid = user["users.langid"]
        roles_sql = ROLES_SQL["main"] % {"table": table}
        textflags_sql = TEXTFLAGS_SQL[view_filter] % {"table": table}
        request = """SELECT %(table)s.xmlid, %(table)s.textstring, \
            %(table)s.textflag, %(table)s.remarks, eng_US.textstring, \
            eng_US.remarks FROM %(table)s, eng_US WHERE \
            %(table)s.xmlid=eng_US.xmlid %(where_roles)s %(where_textflags)s"""\
             % {"table": table, "where_roles": roles_sql, \
                    "where_textflags": textflags_sql}
        
        db = connect_to_db("ro")
        cursor=db.cursor()
        cursor.execute(request)
        rows = cursor.fetchall()
        cursor.close()
        html_form = "<table>"
        for row in rows:
            html_form = html_form + \
                make_single_table_row(row, langid, \
                "Enter the translation:<br/>", "", "save_string", 64, 3)
        html_form = html_form + "</table>"
        db.close()
        return html_form, len(rows)