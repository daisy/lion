from translationpage import *
from templates import tablerow
import util
import re

class ChooseAccelerators(TranslationPage):
    """The page of all the strings (the main page)"""
    
    def __init__(self):
        self.section = "accelerators"
        self.textbox_columns = 20
        self.textbox_rows = 1
        self.instructions = "Enter a key combination (A-Z/+/-/Up/Down/Left/Right/Esc) below."
        self.about = "This is the accelerators page. Accelerators are keyboard shortcuts for program actions. \
            You may use A-Z (U.S. Ascii characters), plus (+), minus (-), Up, Down, Left, Right, or Esc \
            for your custom shortcuts."
        self.check_conflict = True
        #this is weird but necessary .. otherwise cheetah complains
        TranslationPage.__init__(self)    

    def make_table(self, view_filter):
        """Make the form for main page"""
        table = self.user["users.langid"].replace("-", "_")
        langid = self.user["users.langid"]
        textflags_sql = self.get_sql_for_view_filter(view_filter, table)
        
        template_fields = ["xmlid", "textstring", "textflag", "remarks", 
            "target", "actualkeys", "ref_string", "role"]
        dbfields = ["%s.xmlid" % table, "%s.textstring" % table, 
            "%s.textflag" % table, "%s.remarks" % table, "%s.target" % table,
            "%s.actualkeys" % table, "eng_US.textstring", "eng_US.role"]
        
        request = """SELECT %(fields)s FROM %(table)s, eng_US WHERE %(table)s.\
            xmlid=eng_US.xmlid AND %(table)s.role="ACCELERATOR" \
            %(where_flags)s""" % \
            {"fields": ",".join(dbfields), "table": table, 
                "where_flags": textflags_sql}
    
        db = util.connect_to_lion_db("ro")
        cursor = db.cursor()
        cursor.execute(request)
        rows = cursor.fetchall()
        
        form = "<table>"
        for r in rows:
            data = dict(zip(template_fields, r))
            if self.is_excluded(data["actualkeys"]) == True:
                continue
            local_ref = self.build_accelerator_string(cursor, table,
                    data["target"], data["textstring"])
            eng_ref = self.build_accelerator_string(cursor, "eng_US", 
                    data["target"], data["ref_string"])
            # override some values
            data["ref_string"] = local_ref
            data["our_remarks"] = "In English, the accelerator is %s" % eng_ref
            key_mask, letter = self.parse_key_masks(data["textstring"])
            data["textstring"] = letter
            t = tablerow.tablerow(searchList=data)
            t.prefix = key_mask
            t.instructions = self.instructions
            t.width = self.textbox_columns
            t.height = self.textbox_rows
            t.langid = self.user["users.langid"]
            form += t.respond()
        #end for
        form += "</table>"
        cursor.close()
        db.close()        
        return form, len(rows)
    
    def build_accelerator_string(self, cursor, table, target_id, textstring):
        """build a string that looks like this: Ctrl + O (Open)"""
        cursor.execute("SELECT textstring FROM %s WHERE xmlid=\"%s\" " % (table, target_id))
        row = cursor.fetchone()
        if row == None:
            print "Warning! Invalid accelerator"
            return ""
        accel_string = "%s (%s)" % (textstring, row[0])
        return accel_string
    
    def parse_key_masks(self, keys):
        """Take something like 'Ctrl+0' and isolate 'Ctrl+' and 'O'.  Return both parts.  Account for 'Ctrl++' """
        last_part=""
        if keys.endswith("+") == True:
            # reverse the string, replace the last '+' with another letter, but remember what we did
            keys = keys[::-1]
            keys.replace("+", "x", 1)
            last_part = "+"
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
        request = "SELECT DISTINCT actualkeys FROM %s WHERE role=\"ACCELERATOR\" and textstring != \"Space\"" % table
        db = util.connect_to_lion_db("ro")
        cursor = db.cursor()
        cursor.execute(request)
        first_count = cursor.rowcount
        request = "SELECT id FROM %s WHERE role=\"ACCELERATOR\" and textstring != \"Space\"" % table
        cursor.execute(request)
        second_count = cursor.rowcount
        cursor.close()
        db.close()
        print "distinct = %d, ours = %d" % (first_count, second_count)
        if first_count != second_count:
            self.warning_message = "There is a conflict because two commands are using the same keyboard shortcut."
            conflict_found = True
            print "CONFLICT!"
        self.show_no_conflicts = not conflict_found
        return self.index(self.last_view)
    check_conflicts.exposed = True
    
    def is_excluded(self, actualkeys):
        """True if keys contains Alt, Space, or F-anything. """
        # excluded patterns are Alt+__, F__, and Space
        p1 = re.compile("Alt+.*")
        p2 = re.compile("F.*")
        if p1.match(actualkeys) or p2.match(actualkeys) or actualkeys == "Space":
            return True
        else:
            return False
    
    def save_string(self, translation, remarks, status, xmlid, langid, prefix):
        table = langid.replace("-", "_")
        db = util.connect_to_lion_db("rw")
        cursor = db.cursor()
        keys = prefix + translation
        request = """UPDATE %(table)s SET textflag="%(status)s", \
            textstring="%(keys)s", remarks="%(remarks)s", actualkeys="%(keys)s" WHERE \
            xmlid="%(xmlid)s" """ % \
            {"table": table, "status": status, "keys": keys, \
                "remarks": remarks, "xmlid": xmlid}
        cursor.execute(request)
        cursor.close()
        db.close()
        return self.index(self.last_view)
    save_string.exposed = True