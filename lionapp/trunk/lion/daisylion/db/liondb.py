import os
import re
from xml.dom import minidom
from dbsession import DBSession
import modules.lion_module
from daisylion.config.config_parser import *
from liondb_audio_mixin import *
from liondb_module_mixin import *
from liondb_output_mixin import *
from liondb_user_lang_mgmt_mixin import *

class LionDB(LionDBAudioMixIn, LionDBModuleMixIn, LionDBOutputMixIn,
    LionDBUserLangMgmtMixIn, DBSession):
    def __init__(self, configfile, trace=False, app=None):
        # read the settings
        self.config = parse_config(configfile)
        self.masterlang = self.config["main"]["masterlang"]
        
        # for trace and app, read the values from the config file
        # override if they were turned on via the init parameters
        trace = self.config["main"]["trace"] | trace
        self.target_app = self.config["main"]["target_app"]
        if app != None: self.target_app = app
        host = self.config["main"]["dbhost"]
        dbname = self.config["main"]["dbname"]
        
        DBSession.__init__(self, host, dbname, trace)
        
        self.trace_msg("Master language = %s" % self.masterlang)
        self.trace_msg("Host = %s" % host)
        self.trace_msg("DB = %s" % dbname)
        self.trace_msg("Trace = %s" % str(trace))
        
        LionDBModuleMixIn.__init__(self)
        
    def check_language(self, langid):
        """Check the existence of a table for the given language id."""
        self.execute_query("SELECT * FROM languages WHERE langid='%s'" \
            % langid)
        if self.cursor.rowcount == 0: return False
        else: return True
    
    def check_username(self, username):
        """Check the existence of a user with the given username"""
        self.execute_query("SELECT * FROM users WHERE username='%s'" \
            % username)
        if self.cursor.rowcount == 0: return False
        else: return True
    
    def check_string_id(self, langid, stringid):
        """Check the existence of a string with the given xmlid"""
        self.execute_query("SELECT * FROM %(table)s WHERE xmlid='%(xmlid)s'" \
            % {"table": self.make_table_name(langid), "xmlid": stringid})
        if self.cursor.rowcount == 0: return False
        else: return True
    
    def make_table_name(self, langid):
        """Formalize our way of naming a table based on language ID"""
        return langid.replace("-", "_")
    
    def make_id_from_table_name(self, table):
        """get the ID given the table name for a language"""
        return table.replace("_", "-")
    
    def get_masterlang_table(self):
        return self.make_table_name(self.masterlang)
    
    def get_langname(self, langid):
        request = """SELECT langname FROM languages where langid="%s" """ \
            % langid
        self.execute_query(request)
        return self.cursor.fetchone()
    
    def get_table_length(self, langid):
        table = self.make_table_name(langid)
        request = "SELECT COUNT(*) FROM %s" % table
        self.execute_query(request)
        return self.cursor.fetchone()
    
    def has_accelerators(self):
        request = """SELECT COUNT(*) from %s WHERE role="ACCELERATOR" """ \
            % self.get_masterlang_table()
        self.execute_query(request)
        if self.cursor.fetchone()[0] == 0:
            return False
        else:
            return True
    
    def has_mnemonics(self):
        request = """SELECT COUNT(*) from %s WHERE role="MNEMONIC" """ \
            % self.get_masterlang_table()
        self.execute_query(request)
        if self.cursor.fetchone()[0] == 0:
            return False
        else:
            return True
        
    def add_string_master(self, textstring, stringid):
        """add a single string to the master language table, 
        and then add it to all other tables too
        This function is ONLY for adding anything with role=STRING"""
        self.add_string(self.masterlang, textstring, stringid)
        self.process_changes(None)
    
    def add_string(self, langid, textstring, stringid):
        """Add a new string to a language table
        This function is ONLY for adding anything with role=STRING"""
        # make sure the stringid doesn't already exist
        if self.check_string_id(langid, stringid) != False:
            self.die("String with ID %s already exists." % stringid)
        
        table = self.make_table_name(langid)
        self.execute_query("""INSERT INTO %(table)s (textstring, status, \
            xmlid, role) VALUES ("%(textstring)s", 3, \
            "%(xmlid)s", "STRING")""" % \
            {"table": table, "textstring": textstring, "xmlid": stringid})
        self.trace_msg("Remember to change the next-id value in the AMIS XML file.")    
    
    def remove_item_master(self, stringid):
        """Remove an item from the master language table and propagate the 
        results through all other tables"""
        self.remove_item(self.masterlang, stringid)
        removed_ids = stringid,
        self.process_changes(removed_ids)
    
    def remove_item(self, langid, stringid):
        """Remove a string from a table"""
        # make sure the stringid exists
        if self.check_string_id(langid, stringid) == False:
            self.die("String with ID %s does not exist." % stringid)

        table = self.make_table_name(langid)
        # delete it!
        self.execute_query("""DELETE FROM %(table)s \
            WHERE xmlid="%(xmlid)s" """ % \
            {"table": table, "xmlid": stringid})  
    
    def add_accelerator_master(self, textstring, stringid, refid, keys):
        """Add an accelerator to the master language table and propagate the
        changes through all other tables"""
        # print self.masterlang
        self.add_accelerator(self.masterlang, textstring, stringid, refid, keys)
        self.process_changes(None)
    
    def add_accelerator(self, langid, textstring, stringid, refid, keys):
        """Add an accelerator to a table.  
        textstring = the name of the keys (e.g. Space/Espacio)
        stringid = the XMLID value (even if it's not in the XML file, you need
        to give it a unique value as if it were)
        refid = the XMLID value of the entry that this is an accelerator for.  
        keys = the actual keys (Ctrl+O or Space or whatever)"""
        # make sure the stringid doesn't already exist
        if self.check_string_id(langid, stringid) != False:
            self.die("String with ID %s already exists." % stringid)
        
        table = self.make_table_name(langid)

        # add the string to the master table
        self.execute_query("""INSERT INTO %(table)s (textstring, status, \
            xmlid, actualkeys, target, role) VALUES \
            ("%(textstring)s", 3, "%(xmlid)s", "%(keys)s", "%(refid)s", \
            "ACCELERATOR")""" % \
            {"table": table, "textstring": textstring, "xmlid": stringid,
                "keys": keys, "refid": refid})
        self.trace_msg("Remember to change the next-id value in the AMIS XML file.")
    
    def change_item_master(self, textstring, stringid):
        """Change the text of the item at the given id in the master table.
        Reflect the change in all other tables"""
        self.change_item(self.masterlang, textstring, stringid)
        self.process_changes(None)
    
    def change_item(self, langid, textstring, stringid):
        """Change the text of the item at the given ID."""
        
        # make sure the item exists
        if self.check_string_id(langid, stringid) == False:
            self.die("String with ID %s does not exist" % stringid)

        table = self.make_table_name(langid)
        self.execute_query("""UPDATE %(table)s SET textstring="%(textstring)s",\
            status=2 WHERE xmlid="%(xmlid)s" """ %\
            {"table": table, "textstring": textstring, "xmlid": stringid})
    
    def copy_item(self, stringid, sourcelang, destlang):
        """Copy an item from one table to another"""
        if self.check_string_id(sourcelang, stringid) == False:
            self.die("String with ID %s does not exist in %s" % (stringid, sourcelang))
        if self.check_string_id(destlang, stringid) != False:
            self.die("String with ID %s already exists in %s" % (stringid, destlang))
        
        sourcetbl = self.make_table_name(sourcelang)
        desttbl = self.make_table_name(destlang)
        request = """SELECT textstring, role, mnemonicgroup, target, actualkeys 
            FROM %s WHERE xmlid="%s" """ % (sourcetbl, stringid)
        self.execute_query(request)
        data = self.cursor.fetchone()
        text, role, mnem, target, keys = data
        
        request = """INSERT INTO %(table)s (textstring, xmlid, role, 
            mnemonicgroup, target, actualkeys, status)
            VALUES ("%(text)s", "%(xmlid)s", "%(role)s", "%(mnem)s", 
            "%(target)s", "%(keys)s", 3)""" % \
            {"table": desttbl, "text": text, "xmlid": stringid, 
                "role": role, "mnem": mnem, "target": target, 
                "keys": keys}
        self.execute_query(request)
    
    def get_textstring(self, table, strid):
        """Get the text string for the string given by strid"""
        self.execute_query("SELECT textstring FROM %s WHERE xmlid='%s'" % (table, strid))
        row = self.cursor.fetchone()
        if row == None or len(row) == 0: return None
        else: return row[0]

    def get_mnemonic(self, table, strid):
        """Get the text string of the mnemonic for the string given by strid"""
        self.execute_query("SELECT textstring FROM %s WHERE role='MNEMONIC' AND target='%s'" \
            % (table, strid))
        row = self.cursor.fetchone()
        if row == None or len(row) == 0: return None
        else: return row[0]

    def get_accelerator(self, table, strid):
        """Get the text string of the accelerator for the string given by strid"""
        self.execute_query("SELECT textstring FROM %s WHERE role='ACCELERATOR' AND target='%s'" \
            % (table, strid))
        row = self.cursor.fetchone()
        if row == None or len(row) == 0: return None
        else: return row[0]
    
    def get_audiouri(self, table, strid):
        """get the audio clip for the string given by strid"""
        self.execute_query("SELECT audiouri FROM %s WHERE xmlid='%s'" \
            % (table, strid))
        row = self.cursor.fetchone()
        if row == None or len(row) == 0: return None
        else: return row[0]
    
    def get_accelerator_id(self, table, strid):
        """get the ID of the accelerator for the string given by strid"""
        self.execute_query("SELECT xmlid FROM %s WHERE role='ACCELERATOR' AND target='%s'" \
            % (table, strid))
        row = self.cursor.fetchone()
        if row == None or len(row) == 0: return None
        else: return row[0]
    
    def get_mnemonic_id(self, table, strid):
        """get the ID of the mnemonic for the string given by strid"""
        self.execute_query("SELECT xmlid FROM %s WHERE role='MNEMONIC' AND target='%s'" \
            % (table, strid))
        row = self.cursor.fetchone()
        if row == None or len(row) == 0: return None
        else: return row[0]
    
    def set_remarks(self, langid, textstring, stringid):
        """Add a remark for a string"""
        if self.check_string_id(langid, stringid) == False:
            self.die("String %s does not exist for language %s" % (stringid, langid))
        table = self.make_table_name(langid)
        request = """UPDATE %s SET remarks="%s" WHERE xmlid="%s" """ \
            % (table, textstring, stringid)
        self.execute_query(request)

    def process_changes(self, removed_ids):
        """Process the status values (2: changed, 3: new)
        and remove the IDs from all tables"""
        table = self.get_masterlang_table()
        # get all the other language tables except the master
        self.execute_query("SELECT langid FROM languages WHERE langid != '%s'" \
            % self.masterlang)
        languages = self.cursor.fetchall()
        # we can't do anything if there are no other languages
        if languages == None: return;

        # get the changed items
        self.execute_query("SELECT xmlid FROM %s WHERE status=2" % table)
        changed = self.cursor.fetchall()
        # get the new items
        self.execute_query("SELECT textstring, xmlid, role, mnemonicgroup, \
        target, actualkeys FROM %s WHERE status=3" % table)
        newstuff = self.cursor.fetchall()

        # reflect the changes/newstuff in all the other languages
        for lang in languages:
            langtable = self.make_table_name(lang[0])
            if changed != None:
                for row in changed:
                    self.execute_query("UPDATE %(table)s SET status=2\
                        WHERE xmlid='%(xmlid)s'" % \
                        {"table": langtable, "xmlid": row[0]})
            if newstuff != None:
                for row in newstuff:
                    text, xmlid, role, mnem, target, keys = row
                    self.execute_query("""INSERT INTO %(table)s (textstring, \
                        xmlid, role, mnemonicgroup, target, actualkeys, \
                        status) VALUES ("%(text)s", "%(xmlid)s", \
                        "%(role)s", "%(mnem)s", "%(target)s", "%(keys)s", \
                        3)""" % \
                        {"table": langtable, \
                            "text": re.sub("""(['"])""", r"\\\1", text), \
                            "xmlid": xmlid, \
                            "role": role, "mnem": mnem, "target": target, \
                            "keys": keys})
            if removed_ids != None and len(removed_ids) > 0:
                for id in removed_ids:
                    if id != "":
                        self.execute_query("DELETE FROM %(table)s WHERE \
                            xmlid='%(xmlid)s'" % {"table": langtable, "xmlid": id})
        #end language list loop

        # clear the flags in the master table -- otherwise the changes get 
        # re-added to all tables each time anything changes
        self.execute_query("UPDATE %s SET status=1 WHERE status=2 \
            or status=3" % table)
    
    
