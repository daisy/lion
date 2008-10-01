from translationpage import *
from templates import tablerow
from templates import warnings
import util
from validate_keys import *

class ChooseMnemonics(TranslationPage):
    """The page for mnemonics"""
    ROLE_DESCRIPTIONS = {
        "CONTROL": "control, such as a button",
        "DIALOG": "title of a dialog window",
        "STRING": "general string",
        "MENUITEM": "menu item",
        "ACCELERATOR": "keyboard shortcut",
        "MNEMONIC": "letter (underlined) to press to activate the item"}
    
    def __init__(self, session):
        self.section = "mnemonics"
        self.textbox_columns = 1
        self.textbox_rows = 1
        self.instructions = "Enter a single letter."
        self.about = "This is the mnemonics page.  Mnemonics are shortcut \
            letters in a menu item or button.  Each item in a group must have \
            a unique mnemonic."
        TranslationPage.__init__(self, session)    

    def make_table(self, view_filter, pagenum):
        """Make the form for main page"""
        table = self.session.make_table_name(self.user["users.langid"])
        mtable = self.session.get_masterlang_table()
        langid = self.user["users.langid"]
        textflags_sql = self.get_sql_for_view_filter(view_filter, table)
        template_fields = ["xmlid", "textstring", "textflag", "remarks", 
            "target", "ref_string", "role"]
        dbfields = ["%s.xmlid" % table, "%s.textstring" % table, 
            "%s.textflag" % table, "%s.remarks" % table, "%s.target" % table,
            "%s.textstring" % mtable, "%s.role" % mtable]
        
        request = "SELECT DISTINCT mnemonicgroup FROM %s WHERE mnemonicgroup >= 0" % table
        self.session.execute_query(request)
        mnem_groups = self.session.cursor.fetchall()
        form = ""
        group_number = 1
        num_rows = 0
        # each mnemonic group gets its own section
        for g in mnem_groups:
            request = """SELECT %(fields)s FROM %(table)s, %(mastertable)s WHERE %(table)s.\
                xmlid=%(mastertable)s.xmlid AND %(table)s.mnemonicgroup=%(mnem_group)d \
                 AND %(table)s.role="MNEMONIC" %(where_flags)s""" % \
                {"fields": ",".join(dbfields), "table": table, 
                    "where_flags": textflags_sql, "mnem_group": g[0], "mastertable": mtable}

            self.session.execute_query(request)
            rows = self.session.cursor.fetchall()
            num_rows += len(rows)
            if len(rows) > 0:
                # the title of each section
                form += """<h2 id="group_%s">GROUP #%s</h2>""" % (str(g[0]), str(group_number))
                form += "<table>"
                for r in rows:
                    data = dict(zip(template_fields, r))
                    locallang_ref = self.build_mnemonic_string(table,
                        data["target"], data["textstring"])
                    masterlang_ref = self.build_mnemonic_string(mtable, 
                            data["target"], data["ref_string"])
                    # override some values
                    data["ref_string"] = locallang_ref
                    data["our_remarks"] = "This is for a %(item)s.  In %(masterlangname)s, it is \
                        used like this: \"%(example)s\"" \
                        % {"item": self.ROLE_DESCRIPTIONS[data["role"]], 
                            "example": masterlang_ref,
                            "masterlangname": self.masterlangname}
                    t = tablerow.tablerow(searchList=data)
                    t.instructions = self.instructions
                    t.width = self.textbox_columns
                    t.height = self.textbox_rows
                    t.langid = self.user["users.langid"]
                    t.audiouri = self.get_current_audio_uri(data["xmlid"], self.user["users.langid"])
                    if self.error != "" and self.error_id == data["xmlid"]:
            	        t.error = self.error
            	    else:
            	        t.error = ""
                    form += t.respond()
                form += "</table>"
                group_number += 1
        #end for
        
        return form, num_rows
    
    def build_mnemonic_string(self, table, target_id, letter):
        """build a string where the mnemonic letter is 
        underlined in the word (referenced by target_id)"""
        request = "SELECT textstring FROM %s WHERE xmlid = \"%s\"" % (table, target_id)
        self.session.execute_query(request)
        row = self.session.cursor.fetchone()
        if row == None: 
            self.session.warn("Invalid mnemonic")
            return ""
        word = row[0]
        pos = word.lower().find(letter.lower())
        if pos == -1:
            return word + ("""(<span style="text-decoration: underline">%s\
                </span>)""" % letter)
        else:
            # underline the mnemonic
            return word[0:pos] + ("""<span style="text-decoration: \
                underline">%s</span>""" % word[pos]) + word[pos+1:len(word)]
    
    def get_all_warnings(self):
        """check the mnemonic groups for conflicts and summarize as a list of links"""
        table = self.user["users.langid"].replace("-", "_")
        request = "SELECT DISTINCT mnemonicgroup FROM %s WHERE mnemonicgroup >= 0" % table
        self.session.execute_query(request)
        rows = self.session.cursor.fetchall()
        # for each mnemonic group, make sure that each entry is unique
        conflict_found = False
        warning_links = []
        for r in rows:
            group_id = r[0]
            #first get all the items in this mnemonic group
            request = "SELECT id FROM %s WHERE mnemonicgroup = %d" % (table, group_id)
            self.session.execute_query(request)
            first_set = self.session.cursor.fetchall()
            #then get all unique textstrings from this mnemonic group.  
            #this relies on MYSQL being case-insensitive in its comparisons.
            request = "SELECT DISTINCT textstring FROM %s WHERE mnemonicgroup = %d" % (table, group_id)
            self.session.execute_query(request)
            second_set = self.session.cursor.fetchall()
            #if they returned different numbers of results, then probably a mnemonic was repeated
            if len(first_set) != len(second_set):
                group_link = "group_%d" % group_id
                warning_links.append(group_link)
        
        if len(warning_links) == 0:
            return ""
        else:
            t = warnings.warnings()
            t.warning_links = warning_links
            return t.respond()
    
        
    def validate_single_item(self, data, xmlid, langid):
        is_valid = False
        msg = ""
        if data == None or data == "":
            msg = "Data is empty."       
        else:
            if validate_keys(data):
                is_valid = True
            else:
                msg = """The key "%s" is not valid.  Please choose from %s""" % (data, VALID_KEYS)
        
        # conflicts are allowed as part of the workflow
        # but it's good to identify them
        if is_valid:
            has_conflict, msg = self.check_potential_conflict(data, xmlid, langid)
        
        return (is_valid, msg)
    
    def check_potential_conflict(self, data, xmlid, langid):
        """Check if the data would cause a conflict"""
        table = self.session.make_table_name(langid)
        request = """SELECT mnemonicgroup FROM %s WHERE xmlid="%s" """ \
            % (table, xmlid)
        self.session.execute_query(request)
        if self.session.cursor.rowcount == 0:
            # if this element isn't in the table, or isn't a mnemonic, then no conflict 
            return (False, "")
        mnemonicgroup = self.session.cursor.fetchone()[0]
        # see if there is another item in this mnemonic group with the same string
        request = """SELECT id FROM %(table)s WHERE mnemonicgroup=%(mnemonicgroup)d 
            AND textstring="%(textstring)s" AND xmlid != "%(xmlid)s" 
            AND role="MNEMONIC" """ \
            % {"table": table, "mnemonicgroup": mnemonicgroup, 
                "textstring": MySQLdb.escape_string(data), "xmlid": xmlid}
        self.session.execute_query(request)
        if self.session.cursor.rowcount > 0:
            return (True, "This conflicts with an existing mnemonic")
        else:
            return (False, "")
    
    def save_data(self, translation, remarks, status, xmlid, langid, pagenum, audiofile):
        """override of TranslationPage.save_data so we can adjust the case of the data"""
        data = translation.upper()
        return TranslationPage.save_data(self, data, remarks, status, xmlid, langid, pagenum, audiofile)
    save_data.exposed = True