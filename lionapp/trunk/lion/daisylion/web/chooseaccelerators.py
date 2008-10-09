import MySQLdb
from translationpage import *
from templates import tablerow, acceltablerow, warnings
import util
import re
from keys import *

class ChooseAccelerators(TranslationPage):
    """The page for accelerators"""
    
    def __init__(self, session):
        self.section = "accelerators"
        self.textbox_columns = 20
        self.textbox_rows = 1
        self.instructions = "Enter a key combination (A-Z/+/-/Up/Down/Left/Right/Esc) below."
        self.about = "This is the accelerators page. Accelerators are keyboard shortcuts for program actions. \
            You may use A-Z (U.S. Ascii characters), plus (+), minus (-), Up, Down, Left, Right, or Esc \
            for your custom shortcuts."
        self.check_conflict = True
        self.url = "ChooseAccelerators"
        TranslationPage.__init__(self, session)    

    def make_table(self, view_filter, pagenum):
        """Make the form for main page"""
        table = self.session.make_table_name(self.user["users.langid"])
        mtable = self.session.get_masterlang_table()
        langid = self.user["users.langid"]
        status_sql = self.get_sql_for_view_filter(view_filter, table)
        template_fields = ["xmlid", "textstring", "status", "remarks", 
            "target", "actualkeys", "ref_string", "role"]
        dbfields = ["%s.xmlid" % table, "%s.textstring" % table, 
            "%s.status" % table, "%s.remarks" % table, "%s.target" % table,
            "%s.actualkeys" % table, "%s.textstring" % mtable, "%s.role" % mtable]
        
        request = """SELECT %(fields)s FROM %(table)s, %(mastertable)s WHERE %(table)s.\
            xmlid=%(mastertable)s.xmlid AND %(table)s.role="ACCELERATOR" \
            %(where_flags)s""" % \
            {"fields": ",".join(dbfields), "table": table, 
                "where_flags": status_sql, "mastertable": mtable}
        
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
            t.audiouri = self.get_current_audio_uri(data["xmlid"], self.user["users.langid"])
            t.audio_support = self.audio_support
            if self.error != "" and self.error_id == data["xmlid"]:
    	        t.error = self.error
    	    else:
    	        t.error = ""
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
    
    def is_excluded(self, actualkeys):
        """True if keys contains Alt or F-anything. """
        # excluded patterns are Alt+__, F__
        p1 = re.compile("Alt+.*")
        p2 = re.compile("F.*")
        if p1.match(actualkeys) or p2.match(actualkeys): #or actualkeys == "Space":
            return True
        else:
            return False
    
    def save_data(self, remarks, xmlid, langid, keymask, translation, thekeys, audiofile, status=1):
        if thekeys == None or len(thekeys) == 0:
            return ("""Field cannot be empty.  Press the back button to try again.""")
        
        table = langid.replace("-", "_")
        if thekeys != "XXXX":
            # force single characters to be upper-case
            if len(thekeys) == 1:
                actualkeys = keymask + thekeys.upper()
            else:
                actualkeys = keymask + thekeys
        else:
            actualkeys = keymask
        (is_valid, msg) = self.validate_single_item(actualkeys, xmlid, langid)
        self.error, self.error_id = msg, xmlid
        if is_valid:
            request = """UPDATE %(table)s SET status="%(status)s",
                textstring="%(textstring)s", remarks="%(remarks)s", 
                actualkeys="%(actualkeys)s" WHERE xmlid="%(xmlid)s" """ % \
                    {"table": table, "status": status, "actualkeys": 
                        MySQLdb.escape_string(actualkeys),"remarks": MySQLdb.escape_string(remarks), 
                        "xmlid": xmlid, "textstring": MySQLdb.escape_string(translation)}
            self.session.execute_query(request)
            self.show_no_conflicts = False
            if audiofile != None and audiofile !="" and audiofile.filename != "": 
                self.save_audio(audiofile, langid, xmlid)
        self.redirect(xmlid)
    save_data.exposed = True
    
    def get_all_warnings(self):
        """Look for accelerator key conflicts.  This function checks all accelerators, not just the ones from the form, and
        it ignores Space because that one is used twice (play/pause) and is not allowed to be changed by the user."""
        table = self.user["users.langid"].replace("-", "_")
        expr1 = "SELECT count(DISTINCT actualkeys) FROM %s WHERE role=\"ACCELERATOR\" and actualkeys != \"Space\"" % table
        expr2 = "SELECT count(*) FROM %s WHERE role=\"ACCELERATOR\" and actualkeys != \"Space\"" % table
        request = "SELECT (%s) - (%s) AS diff_rows" % (expr1, expr2)
        self.session.execute_query(request)
        # if there is a difference in the lengths of the two sets, there must be a conflict
        if self.session.cursor.fetchone()[0] != 0:
            warning_message = "There is a conflict because two commands are using the same keyboard shortcut."
            self.session.warn(warning_message)
            t = warnings.warnings()
            t.warning_links = None
            t.warning_message = warning_message
            return t.respond()
        else:
            return ""
    
        
    def validate_single_item(self, data, xmlid, langid):
        is_valid = False
        msg = ""
        if data == None or data == "":
            msg = "Data is empty."       
        else:
            mask, keys = self.parse_key_masks(data)
            if validate_keys(keys):
                is_valid = True
            else:
                msg = """The key "%s" is not valid.  Please choose from %s""" % (data, VALID_KEYS)
        
        # conflicts are allowed as part of the workflow
        # but it's good to identify them
        if is_valid:
            msg = self.check_potential_conflict(data, langid, xmlid)
        return (is_valid, msg)
    
    def check_potential_conflict(self, data, langid, xmlid):
        """Check if the new single data item would cause a conflict"""
        table = self.session.make_table_name(langid)
        request = """SELECT id FROM %s WHERE role=\"ACCELERATOR\" 
            AND actualkeys = "%s" AND xmlid !="%s"  """ \
            % (table, MySQLdb.escape_string(data), xmlid)
        self.session.execute_query(request)
        if self.session.cursor.rowcount == 0:
            return "No conflict"
        else:
            return "This conflicts with an existing accelerator"
    
    