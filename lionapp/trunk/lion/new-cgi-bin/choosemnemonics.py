from translationpage import *

class ChooseMnemonics(TranslationPage):
    """The page of all the strings (the main page)"""
    ROLE_DESCRIPTIONS = {
        "CONTROL": "control, such as a button",
        "DIALOG": "title of a dialog window",
        "STRING": "general string",
        "MENUITEM": "menu item",
        "ACCELERATOR": "keyboard shortcut",
        "MNEMONIC": "letter (underlined) to press to activate the item"}
    
    def __init__(self):
        self.section = "mnemonics"
        self.textbox_columns = 64
        self.textbox_rows = 3
        self.instructions = "Enter a single letter and press save:"
        self.about = "This is the mnemonics page.  Mnemonics are shortcut \
            letters in a menu item or button.  Each item in a group must have \
            a unique mnemonic."    

    def make_table(self, view_filter):
        """Make the form for main page"""
        table = self.user["users.langid"].replace("-", "_")
        langid = self.user["users.langid"]
        textflags_sql = self.get_sql_for_view_filter(view_filter, table)
        template_fields = ["xmlid", "textstring", "textflag", "remarks", 
            "target", "ref_string", "role"]
        dbfields = ["%s.xmlid" % table, "%s.textstring" % table, 
            "%s.textflag" % table, "%s.remarks" % table, "%s.target" % table,
            "eng_US.textstring", "eng_US.role"]
        
        request = "SELECT DISTINCT mnemonicgroup FROM %s WHERE mnemonicgroup >= 0" % table
        db = connect_to_lion_db("ro")
        cursor = db.cursor()
        cursor.execute(request)
        mnem_groups = cursor.fetchall()
        form = ""
        group_number = 1
        num_rows = 0
        # each mnemonic group gets its own section
        for g in mnem_groups:
            # the title of each section
            form += """<h2 id="group_%s">GROUP #%s</h2>""" % (str(g[0]), str(group_number))
            request = """SELECT %(fields)s FROM %(table)s, eng_US WHERE %(table)s.\
                xmlid=eng_US.xmlid AND %(table)s.mnemonicgroup=%(mnem_group)d \
                 AND %(table)s.role="MNEMONIC" %(where_flags)s""" % \
                {"fields": ",".join(dbfields), "table": table, 
                    "where_flags": textflags_sql, "mnem_group": g[0]}

            cursor.execute(request)
            rows = cursor.fetchall()
            num_rows += len(rows)
            form += "<table>"
            for r in rows:
                data = dict(zip(template_fields, r))
                local_ref = self.build_mnemonic_string(cursor, table,
                    data["target"], data["textstring"])
                eng_ref = self.build_mnemonic_string(cursor, "eng_US", 
                        data["target"], data["ref_string"])
                # override some values
                data["ref_string"] = local_ref
                data["our_remarks"] = "This is for a %(item)s.  In English, it is \
                    used like this: \"%(example)s\"" \
                    % {"item": self.ROLE_DESCRIPTIONS[data["role"]], 
                        "example": eng_ref}
                
                t = Template(file="./templates/tablerow.tmpl", searchList=data)
                t.instructions = self.instructions
                t.width = self.textbox_columns
                t.height = self.textbox_rows
                t.langid = self.user["users.langid"]
                t.handler = self.handler
                form += str(t)
            form += "</table>"
            group_number += 1
        #end for
        cursor.close()
        db.close()
        
        return form, num_rows
    
    def build_mnemonic_string(self, cursor, table, target_id, letter):
        """build a string where the mnemonic letter is 
        underlined in the word (referenced by target_id)"""
        
        cursor.execute("SELECT textstring FROM %s WHERE xmlid = \"%s\"" \
            % (table, target_id))
        row = cursor.fetchone()
        
        if row == None: 
            print "Warning: invalid mnemonic"
            return ""
        word = row[0]
        pos = word.lower().find(letter.lower())
        print "word = %s, letter = %s" % (word, letter)
        if pos == -1:
            return word + ("""(<span style="text-decoration: underline">%s\
                </span>)""" % letter)
        else:
            # underline the mnemonic
            return word[0:pos] + ("""<span style="text-decoration: \
                underline">%s</span>""" % word[pos]) + word[pos+1:len(word)]
    
