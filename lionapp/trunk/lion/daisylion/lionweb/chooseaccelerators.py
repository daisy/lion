import MySQLdb
from translationpage import *
from templates import tablerow, acceltablerow
import util
import re

class ChooseAccelerators(TranslationPage):
    """The page of all the strings (the main page)"""
    
    def __init__(self, session, host, port, masterlang):
        self.section = "accelerators"
        self.textbox_columns = 20
        self.textbox_rows = 1
        self.instructions = "Enter a key combination (A-Z/+/-/Up/Down/Left/Right/Esc) below."
        self.about = "This is the accelerators page. Accelerators are keyboard shortcuts for program actions. \
            You may use A-Z (U.S. Ascii characters), plus (+), minus (-), Up, Down, Left, Right, or Esc \
            for your custom shortcuts."
        self.check_conflict = True
        #this is weird but necessary .. otherwise cheetah complains
        TranslationPage.__init__(self, session, host, port, masterlang)    

    def make_table(self, view_filter, pagenum):
        """Make the form for main page"""
        table = self.make_table_name(self.user["users.langid"])
        mtable = self.make_table_name(self.masterlang)
        langid = self.user["users.langid"]
        textflags_sql = self.get_sql_for_view_filter(view_filter, table)
        template_fields = ["xmlid", "textstring", "textflag", "remarks", 
            "target", "actualkeys", "ref_string", "role"]
        dbfields = ["%s.xmlid" % table, "%s.textstring" % table, 
            "%s.textflag" % table, "%s.remarks" % table, "%s.target" % table,
            "%s.actualkeys" % table, "%s.textstring" % mtable, "%s.role" % mtable]
        
        request = """SELECT %(fields)s FROM %(table)s, %(mastertable)s WHERE %(table)s.\
            xmlid=%(mastertable)s.xmlid AND %(table)s.role="ACCELERATOR" \
            %(where_flags)s""" % \
            {"fields": ",".join(dbfields), "table": table, 
                "where_flags": textflags_sql, "mastertable": mtable}
        
        self.session.execute_query(request)
        rows = self.session.cursor.fetchall()
        
        form = "<table>"
        for r in rows:
            data = dict(zip(template_fields, r))
            if self.is_excluded(data["actualkeys"]) == True:
                continue
            locallang_ref = self.build_accelerator_string(table,
                    data["target"], data["textstring"])
            masterlang_ref = self.build_accelerator_string(mtable, 
                    data["target"], data["ref_string"])
            # override some values
            data["ref_string"] = locallang_ref
            data["our_remarks"] = "In %s, the accelerator is %s" % (self.masterlangname, masterlang_ref)
            key_mask, letter = self.parse_key_masks(data["actualkeys"])
            data["thekeys"] = letter
            data["keymask"] = key_mask
            t = acceltablerow.acceltablerow(searchList=data)
            t.instructions = self.instructions
            t.langid = self.user["users.langid"]
            form += t.respond()
        #end for
        form += "</table>"
        return form, len(rows)
    
    def build_accelerator_string(self, table, target_id, textstring):
        """build a string that looks like this: Ctrl + O (Open)"""
        request = "SELECT textstring FROM %s WHERE xmlid=\"%s\" " % (table, target_id)
        self.session.execute_query(request)
        row = self.session.cursor.fetchone()
        if row == None:
            self.session.warn("Invalid accelerator")
            return ""
        accel_string = "%s (%s)" % (textstring, row[0])
        return accel_string
    
    def parse_key_masks(self, keys):
        """Take something like 'Ctrl+0' and isolate 'Ctrl+' and 'O'.  Return both parts.  Account for 'Ctrl++' and Space
        (in AMIS, you can't change Space, so we can treat it like a keymask) """
        if keys == "Space":
            return keys, ""
        
        last_part=""
        if keys.endswith("+") == True:
            # reverse the string, replace the last '+' with another letter, but remember what we did
            keys = keys[::-1]
            keys = keys.replace("+", "x", 1)
            last_part = "+"
            keys = keys[::-1]
        pos = keys.rfind("+")
        if pos == -1:
            return "", keys
        else:
            if last_part == "":
                last_part = keys[pos+1:len(keys)]
            return keys[0:pos+1], last_part
    
    def check_conflicts(self):
        """Look for accelerator key conflicts.  This function checks all accelerators, not just the ones from the form, and
        it ignores Space because that one is used twice (play/pause) and is not allowed to be changed by the user."""
        conflict_found = False
        table = self.user["users.langid"].replace("-", "_")
        request = "SELECT DISTINCT actualkeys FROM %s WHERE role=\"ACCELERATOR\" and actualkeys != \"Space\"" % table
        self.session.execute_query(request)
        first_count = self.session.cursor.rowcount
        request = "SELECT id FROM %s WHERE role=\"ACCELERATOR\" and actualkeys != \"Space\"" % table
        self.session.execute_query(request)
        second_count = self.session.cursor.rowcount
        msg = "Checking for conflicts. Found %d distinct items versus %d total items in the table %s" \
            % (first_count, second_count, table)
        self.session.trace_msg(msg)
        if first_count != second_count:
            self.warning_message = "There is a conflict because two commands are using the same keyboard shortcut."
            conflict_found = True
            self.session.warn(self.warning_message)
        else:
            conflict_found = False
            self.warning_message = ""
        self.show_no_conflicts = not conflict_found
        
        return self.index(self.last_view)
    check_conflicts.exposed = True
    
    def is_excluded(self, actualkeys):
        """True if keys contains Alt or F-anything. """
        # excluded patterns are Alt+__, F__
        p1 = re.compile("Alt+.*")
        p2 = re.compile("F.*")
        if p1.match(actualkeys) or p2.match(actualkeys): #or actualkeys == "Space":
            return True
        else:
            return False
    
    def save_string(self, remarks, status, xmlid, langid, keymask, translation, thekeys):
        if thekeys == None or len(thekeys) == 0:
            return ("""Field cannot be empty.  Press the back button to try again.""")
        
        table = langid.replace("-", "_")
        if thekeys != "XXXX":
            actualkeys = keymask + thekeys
        else:
            actualkeys = keymask
        
        request = """UPDATE %(table)s SET textflag="%(status)s", \
            textstring="%(textstring)s", remarks="%(remarks)s", actualkeys="%(actualkeys)s" WHERE \
            xmlid="%(xmlid)s" """ % \
            {"table": table, "status": status, "actualkeys": MySQLdb.escape_string(actualkeys), \
                "remarks": MySQLdb.escape_string(remarks), "xmlid": xmlid, "textstring": MySQLdb.escape_string(translation)}
        self.session.execute_query(request)
        self.show_no_conflicts = False
        return self.index(self.last_view)
    save_string.exposed = True
        
