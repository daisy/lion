from xml.dom import minidom
from ConfigParser import ConfigParser
import addremove_language
from dbsession import DBSession

class LionDB(DBSession):
    def __init__(self, trace=False, force=False, app=None):
        if app:
            self.trace = trace
            self.force = force
            self.config = ConfigParser()
            self.config.read("lion.cfg")
            self.masterlang = self.config.get("main", "masterlang")
            self.trace_msg(self.masterlang)
            
            DBSession.__init__(self, trace, force)
            
            # Import the application module, which lives here:
            # top-level/modules/APP/lionio_APP.someclass
            # someclass is defined in the config file and it inherits from LionIOModule
            module_name = "modules." + app + ".lionio_" + app
            self.trace_msg("import %s" % module_name)
            try:
                module = __import__(module_name, globals(), locals(), [''], -1)
                classname = module + "." + self.config.read(app, "dbioclass")
                obj = eval(classname)
                self.dbio = obj()
            
            except Exception, e :
                self.die("""Unknown application "%s" (%s)""" % (app, e))
    
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
    
    def import_xml(self, file, langid):
        """Import from XML to the database."""
        if not file: die("No XML file given.")
        if not self.check_language(langid):
            die("No table for language %s." % langid)
        self.trace_msg("Import from " + file + " for " + langid)
        self.dbio.import_from_xml(self, file, langid)
        removed_ids = self.dbio.get_removed_ids(doc)
        self.process_changes(langid, removed_ids)
    
    def export(self, file, langid, export_type):
        print self.dbio.export(self, file, langid, export_type)
    
    def all_strings(self, langid):
        """Export all strings to stdout"""
        self.trace_msg("Export all strings to stdout")
        table = self.make_table_name(langid)
        self.execute_query("""SELECT textstring FROM """ + table + """
            where (role="STRING" or role="MENUITEM" or role="DIALOG" or \
            role="CONTROL") and translate=1""")
        strings = self.cursor.fetchall()
        print self.__stringlist_to_xml(strings, langid)
    
    def textstrings(self, langid):
        """Export all strings to stdout"""
        self.trace_msg("Export strings to stdout")
        table = self.make_table_name(langid)
        self.execute_query("SELECT textstring FROM " + table)
        strings = self.cursor.fetchall()
        print self.__stringlist_to_xml(strings, langid)
    
    def __stringlist_to_xml(self, results, langid):
        """Get all strings that have the given roles"""
        output = """<?xml version="1.0"?>\n<strings langid=\"""" + langid + "\">"
        for item in results:
            output += "<s>" + item[0].encode("utf-8") + "</s>"
        output += "</strings>"
        return output
    
    def import_audio_prompts(self, langid, ncx):
        """Fill up the database with prompts file names. We use the NCX file
        from the Obi export and match the navPoint text label with textstrins
        in the DB."""
        self.trace_msg("Getting audio prompts from NCX")
        try:
            dom = minidom.parse(ncx)
        except Exception, e:
            self.die("""Couldn't open "%s" (%s)""" % (ncx, e))
        self.execute_query("SELECT id, textstring FROM " +
                self.make_table_name(langid))
        strings = self.cursor.fetchall()
        labels = dom.getElementsByTagNameNS(
            "http://www.daisy.org/z3986/2005/ncx/", "navLabel")
        self.trace_msg("Got %d labels for %d strings" %
            (labels.__len__(), strings.__len__()))
        for label, string in zip(labels, strings):
            text = label.getElementsByTagNameNS(
                "http://www.daisy.org/z3986/2005/ncx/", "text")[0].firstChild.data
            audio_src = label.getElementsByTagNameNS(
                "http://www.daisy.org/z3986/2005/ncx/", "audio")[0].getAttribute("src")
            if string[1] == text:
                self.execute_query("""UPDATE %s SET audiouri="%s", audioflag=1 WHERE id=%d""" %
                        (self.make_table_name(langid), audio_src, string[0]))
            else:
                self.warn("""No match between db string="%s" and ncx label="%s"?!""" %
                        (string[1], text))

        
    def add_language(self, langid, langname, username, password, realname, email):
        """Add a language and corresponding uer"""
        addremove_language.add_language(self, langid, langname, username, password, realname, email)
    
    def remove_language(self, langid):
        """Remove a language (also removes the user)"""
        addremove_language.remove_language(self, langid)
    
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
            3, "%(xmlid)s", "STRING")""" % \
            {"table": table, "textstring": textstring, "xmlid": stringid})
        self.trace_msg("Remember to change the next-id value in the AMIS XML file.")
        __process_changes(langid, None)

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

        __process_changes(langid, removed_ids)

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
            ("%(textstring)s", 3, 3, "%(xmlid)s", "%(keys)s", "%(refid)s", \
            "ACCELERATOR")""" % \
            {"table": table, "textstring": textstring, "xmlid": stringid,
                "keys": keys, "refid": refid})
        self.trace_msg("Remember to change the next-id value in the AMIS XML file.")
        __process_changes(langid, None)

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
        __process_changes(langid, None)
    
    
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
                    self.execute_query("UPDATE %(table)s SET textflag=2 WHERE \
                        xmlid='%(xmlid)s'" % \
                        {"table": langtable, "xmlid": row[0]})
            if newstuff != None:
                for row in newstuff:
                    text, xmlid, role, mnem, target, keys = row
                    self.execute_query("""INSERT INTO %(table)s (textstring, \
                        xmlid, role, mnemonicgroup, target, actualkeys, \
                        textflag, audioflag) VALUES ("%(text)s", "%(xmlid)s", \
                        "%(role)s", "%(mnem)s", "%(target)s", "%(keys)s", \
                        3, 3)""" % \
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
            

