import os
from xml.dom import minidom
from dbsession import DBSession
import modules.lion_module
from daisylion.config_parser import *
from liondb_audio_mixin import *
from liondb_module_mixin import *
from liondb_output_mixin import *
from liondb_user_mgmt_mixin import *

class LionDB(LionDBAudioMixIn, LionDBModuleMixIn, LionDBOutputMixIn,
    LionDBUserMgmtMixIn, DBSession):
    def __init__(self, configfile, trace=False, force=False, app=None):
        # read the settings
        self.config = parse_config(configfile)
        self.masterlang = self.config["main"]["masterlang"]
        
        # for trace and force, read the values from the config file
        # override if they were turned on via the init parameters
        trace = self.config["main"]["trace"] | trace
        force = self.config["main"]["force"] | force
        
        host = self.config["main"]["dbhost"]
        dbname = self.config["main"]["dbname"]
        
        DBSession.__init__(self, host, dbname, trace, force)
        
        self.trace_msg("Master language = %s" % self.masterlang)
        self.trace_msg("Host = %s" % host)
        self.trace_msg("DB = %s" % dbname)
        self.trace_msg("Trace = %s" % str(trace))
        self.trace_msg("Force = %s" % str(force))
        
        LionDBModuleMixIn.__init__(self, app)
        
    def check_language(self, langid):
        """Check the existence of a table for the given language id."""
        self.execute_query("SELECT langname FROM languages WHERE langid='%s'" \
            % langid)
        row = self.cursor.fetchone()
        if row != None: return row[0]
        else: return None
    
    def check_username(self, username):
        """Check the existence of a user with the given username"""
        self.execute_query("SELECT username FROM users WHERE username='%s'" \
            % username)
        row = self.cursor.fetchone()
        if row != None: return row[0]
        else: return None
    
    def check_string_id(self, langid, stringid):
        """Check the existence of a string with the given xmlid"""
        self.execute_query("SELECT textstring FROM %(table)s WHERE xmlid='%(xmlid)s'" \
            % {"table": self.make_table_name(langid), "xmlid": stringid})
        row = self.cursor.fetchone()
        if row != None: return row[0]
        else: return None
    
    def make_table_name(self, langid):
        """Formalize our way of naming a table based on language ID"""
        return langid.replace("-", "_")

    def get_masterlang_table(self):
        return make_table_name(self.masterlang)
    
    # add a single string from the master table
    def add_string(self, langid, textstring, stringid):
        """Add a new string to all tables
            langid = master table
            stringid = xmlid for the string
            This function is ONLY for adding anything with role=STRING"""

        # make sure the stringid doesn't already exist
        if self.check_string_id(langid, stringid) != None:
            self.die("String with ID %s already exists." % stringid)
        
        table = self.make_table_name(langid)

        # add the string to the master table
        self.execute_query("""INSERT INTO %(table)s (textstring, textflag, \
            audioflag, xmlid, role) VALUES ("%(textstring)s", 3, \
            2, "%(xmlid)s", "STRING")""" % \
            {"table": table, "textstring": textstring, "xmlid": stringid})
        self.trace_msg("Remember to change the next-id value in the AMIS XML file.")
        if langid == self.masterlang:
            self.__process_changes(langid, None)

    def remove_item(self, langid, stringid):
        """Remove a string from all the tables
            langid = master table
            stringid = xmlid for the string"""
        # make sure the stringid exists
        if self.check_string_id(langid, stringid) == None:
            self.die("String with ID %s does not exist." % stringid)

        # safety check
        can_remove = session.force
        if self.force == False:
            rly = raw_input("Do you REALLY want to remove a string?  This is serious.\n \
                Type your answer (definitely/no)  ")
            if rly == "definitely":
                can_remove = True
            else:
                can_remove = False

        table = self.make_table_name(langid)
        # really delete it!
        if can_remove == True:
            self.execute_query("""DELETE FROM %(table)s \
                WHERE xmlid="%(xmlid)s" """ % \
                {"table": table, "xmlid": stringid})

        if langid == self.masterlang:
            self.__process_changes(langid, removed_ids)

    def add_accelerator(self, langid, textstring, stringid, refid, keys):
        """Add an accelerator to all language tables.  
        textstring = the name of the keys (e.g. Space/Espacio)
        stringid = the XMLID value (even if it's not in the XML file, you need
        to give it a unique value as if it were)
        refid = the XMLID value of the entry that this is an accelerator for.  
        keys = the actual keys (Ctrl+O or Space or whatever)"""
        # make sure the stringid doesn't already exist
        if self.check_string_id(langid, stringid) != None:
            self.die("String with ID %s already exists." % stringid)
        
        table = self.make_table_name(langid)

        # add the string to the master table
        self.execute_query("""INSERT INTO %(table)s (textstring, textflag, \
            audioflag, xmlid, actualkeys, target, role) VALUES \
            ("%(textstring)s", 3, 2, "%(xmlid)s", "%(keys)s", "%(refid)s", \
            "ACCELERATOR")""" % \
            {"table": table, "textstring": textstring, "xmlid": stringid,
                "keys": keys, "refid": refid})
        self.trace_msg("Remember to change the next-id value in the AMIS XML file.")
        if langid == self.masterlang:
            self.__process_changes(langid, None)

    def change_item(self, langid, textstring, stringid):
        """Change the text of the item at the given ID.  Reflect the change in the other tables.
        Assumed: the language given by langid is the master language"""
        
        # make sure the item exists
        if self.check_string_id(langid, stringid) == None:
            self.die("String with ID %s does not exist" % stringid)

        table = self.make_table_name(langid)
        self.execute_query("""UPDATE %(table)s SET textstring="%(textstring)s",\
            textflag=2 WHERE xmlid="%(xmlid)s" """ %\
            {"table": table, "textstring": textstring, "xmlid": stringid})
        if langid == self.masterlang:
            self.__process_changes(langid, None)
    
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
    
    def __process_changes(self, langid, removed_ids):
        """Process the textflag values (2: changed, 3: new)
        and remove the IDs from all tables"""
        table = self.make_table_name(langid)
        # get all the other language tables except the master (langid)
        self.execute_query("SELECT langid FROM languages WHERE langid != '%s'" \
            % langid)
        languages = self.cursor.fetchall()
        # we can't do anything if there are no other languages
        if languages == None: return;

        # get the changed items
        self.execute_query("SELECT xmlid FROM %s WHERE textflag=2" % table)
        changed = self.cursor.fetchall()
        # get the new items
        self.execute_query("SELECT textstring, xmlid, role, mnemonicgroup, \
        target, actualkeys FROM %s WHERE textflag=3" % table)
        newstuff = self.cursor.fetchall()

        # reflect the changes/newstuff in all the other languages
        for lang in languages:
            langtable = self.make_table_name(lang[0])
            if changed != None:
                for row in changed:
                    self.execute_query("UPDATE %(table)s SET textflag=2, audioflag=2 \
                        WHERE xmlid='%(xmlid)s'" % \
                        {"table": langtable, "xmlid": row[0]})
            if newstuff != None:
                for row in newstuff:
                    text, xmlid, role, mnem, target, keys = row
                    self.execute_query("""INSERT INTO %(table)s (textstring, \
                        xmlid, role, mnemonicgroup, target, actualkeys, \
                        textflag, audioflag) VALUES ("%(text)s", "%(xmlid)s", \
                        "%(role)s", "%(mnem)s", "%(target)s", "%(keys)s", \
                        3, 2)""" % \
                        {"table": langtable, "text": text, "xmlid": xmlid, \
                            "role": role, "mnem": mnem, "target": target, \
                            "keys": keys})
            if removed_ids != None:
                for id in removed_ids:
                    self.execute_query("DELETE FROM %(table)s WHERE \
                        xmlid='%(xmlid)s'" % {"table": langtable, "xmlid": id})
        #end language list loop

        # clear the flags in the master table -- otherwise the changes get 
        # re-added to all tables each time anything changes
        self.execute_query("UPDATE %s SET textflag=1 WHERE textflag=2 \
            or textflag=3" % table)
    
    