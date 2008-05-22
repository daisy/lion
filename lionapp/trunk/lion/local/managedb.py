#!/usr/bin/python

# Manage the database

import getopt
import os
from xml.dom import minidom
# Harcoded DB connection info, not stored in SVN
os.sys.path.append("../")
from DB.connect import *
import addremove_language

class DBSession:
    """A session with the DB."""

    def __init__(self, trace, force, app=None):
        self.trace = trace      # trace flag
        self.warnings = 0       # warnings during operation
        self.connected = False  # no connection yet
        self.force = force      # force flag
        if app:
            # Import the application module
            module = "dbio_" + app
            self.trace_msg("import %s" % module)
            try:
                self.dbio = __import__(module)
            except Exception, e :
                self.die("""Unknown application "%s" (%s)""" % (app, e))

    def __del__(self):
        """Disconnect when disappearing."""
        self.disconnect()


    def trace_msg(self, msg):
        """Output a trace message if the trace flag is set."""
        if self.trace: os.sys.stderr.write("*** %s\n" % msg)

    def warn(self, msg):
        """Report a warning and increment the warnings count."""
        os.sys.stderr.write("Warning: %s\n" % msg)
        self.warnings += 1

    def die(self, msg, err=0):
        """Die with an error message and an error code. If the code is 0, don't
die just yet."""
        os.sys.stderr.write("Error: %s\n" % msg)
        if err > 0: os.sys.exit(err)

    def connect(self):
        """Connect to the database."""
        if not self.connected:
            self.trace_msg("Connecting to the database...")
            self.db = db_connect("admin")
            self.cursor = self.db.cursor()
            self.connected = True
            self.trace_msg("... connected")

    def disconnect(self):
        """Disconnect from the database."""
        if self.connected:
            self.trace_msg("Disconnecting from the database...")
            self.cursor.close()
            self.db.close()
            self.trace_msg("... disconnected.")

    def execute_query(self, q):
        """Execute a query."""
        self.connect()
        self.trace_msg("""Query: "%s".""" % q)
        self.cursor.execute(q)

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
    
    def import_xml(self, file, langid):
        """Import from XML to the database."""
        if not file: die("No XML file given.")
        if not self.check_language(langid):
            die("No table for language %s." % langid)
        self.trace_msg("Import from " + file + " for " + langid)
        doc = minidom.parse(file)
        self.dbio.import_from_xml(self, doc, langid)
        removed_ids = self.dbio.get_removed_ids(doc)
        self.process_changes(langid, removed_ids)
    
    def export_xml(self, file, langid):
        print self.dbio.export_xml(self, file, langid)
    
    def export_rc(self, langid):
        print self.dbio.export_rc(self, langid)
    
    def strings(self, langid):
        """Export strings to stdout"""
        self.trace_msg("Export strings to stdout")
        self.execute_query("""SELECT textstring FROM """ + langid + """
            where (role="STRING" or role="MENUITEM" or role="DIALOG" or \
            role="CONTROL") and translate=1""")
        strings = self.cursor.fetchall()
        print """<?xml version="1.0"?>\n<strings langid=\"""" + langid + "\">"
        for string in strings:
            print "<s>" + string[0].encode("utf-8") + "</s>"
        print "</strings>"
    
    def get_all_strings(self, langid):
        """Get all strings from the DB for a langid and return a handy list."""
        self.execute_query("SELECT textstring FROM " + langid)
        return map(lambda s: s[0], self.cursor.fetchall())

    def all_strings(self, langid):
        """Export all strings to stdout"""
        self.trace_msg("Export strings to stdout")
        strings = self.get_all_strings(langid)
        print """<?xml version="1.0"?>\n<strings langid=\"""" + langid + "\">"
        for string in strings:
            print "<s>" + string + "</s>"
        print "</strings>"

    def audio_prompts(self, langid, ncx):
        """Fill up the database with prompts file names. We use the NCX file
        from the Obi export and match the navPoint text label with textstrins
        in the DB."""
        self.trace_msg("Getting audio prompts from NCX")
        strings = self.get_all_strings(langid)

    def process_changes(self, langid, removed_ids):
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
    
    
    def add_language(self, langid, langname, username, password, realname, email):
        """Add a language and corresponding uer"""
        addremove_language.add_language(self, langid, langname, username, password, realname, email)
    
    def remove_language(self, langid):
        """Remove a language (also removes the user)"""
        addremove_language.remove_language(self, langid)
    
    def add_string(self, langid, textstring, stringid):
        """Add a string to all language tables.  XMLID must be supplied."""
        success = self.dbio.add_string(self, langid, textstring, stringid)
        if success == True:
            self.process_changes(langid, None)
    
    def remove_item(self, langid, stringid):
        """Remove an item from all language tables by XMLID."""
        success = self.dbio.remove_item(self, langid, stringid)
        if success == True:
            removed_ids = stringid,
            self.process_changes(langid, removed_ids)
    
    def add_accelerator(self, langid, textstring, stringid, refid, keys):
        """Add an accelerator to all language tables.  
        textstring = the name of the keys (e.g. Space/Espacio)
        stringid = the XMLID value (even if it's not in the XML file, you need
        to give it a unique value as if it were)
        refid = the XMLID value of the entry that this is an accelerator for.  
        keys = the actual keys (Ctrl+O or Space or whatever)"""
        success = self.dbio.add_accelerator(self, langid, textstring, stringid, refid, keys)
        if success == True:
            self.process_changes(langid, None)
    
    
def usage(code=0):
    """Print usage information and exits with an error code."""
    print """
Usage:

  %(script)s --help                              Show this help message.
  %(script)s --import --langid=id --file=file    Import file into table id.
  %(script)s --export_xml --langid=id --file=file    Export to XML
  %(script)s --export_rc --langid=id --file=file    Export to RC
  %(script)s --add_language --langid=id --langname=langname \
--username=username --password=password --email=email \
--realname=realname                              
                                                 Add a new language
  %(script)s --remove_language --langid=id       Remove a language
  %(script)s --add_string --langid=id --textstring=string --stringid=id 
                                                 Add a string to all tables
  %(script)s --remove_string --langid=id --stringid=id
                                                 Remove an item from all tables
  %(script)s --add_accelerator --langid=id --textstring=string --stringid=id
--refid=id --keys=accelerator                    Add an accelerator to all tables
  %(script)s --strings --langid=id               Output XML of strings, not including keyboard shortcuts
  %(script)s --all_strings --langid=id           Output XML of strings, including keyboard shortcuts
  
Other options:
  --application, -a: which application module to use (e.g. "amis" or "obi")
  --trace, -t: trace mode (send trace messages to stderr.)
  --force, -f: force execution without safe checks 

""" % {"script": os.sys.argv[0]}
    os.sys.exit(code)


def main():
    """Parse command line arguments and run."""
    app = "amis"
    trace = False
    action = lambda s, f, l: usage(1)
    file = None
    langid = None
    langname = None
    username = None
    password = None
    email = None
    realname = None
    force = False
    # if the action is add/remove a language/string/accelerator, the parameters are different
    add_language = False  
    add_string = False
    remove_item = False
    add_accel = False
    textstring = None
    stringid = None
    refid = None
    actualkeys = None
    try:
        """
        a: - application
        e  - export_xml
        F: - file
        h  - help
        i  - import
        l: - language id
        t  - trace
        n: - language name
        u: - username
        p: - password
        r: - real name
        e: - email
        f  - force
        A  - add language
        R  - remove language
        s  - strings export
        """
        opts, args = getopt.getopt(os.sys.argv[1:], "a:eF:hil:tn:u:p:r:e:fARs",
            ["application=", "export_xml", "file=", "help", "import", "langid=",
                "trace", "add_language", "remove_language", "langname=", 
                "username=", "password=", "realname=", "email=", "force", 
                "stringid=", "text=", "remove_item", "add_string", "refid=", 
                "keys=", "add_accelerator", "strings", "all_strings",
                "export_rc", "audio_prompts="])
    except getopt.GetoptError, e:
        os.sys.stderr.write("Error: %s" % e.msg)
        usage(1)
    for opt, arg in opts:
        if opt in ("-a", "--application"): app = arg
        elif opt in ("-e", "--export_xml"):
            action = lambda s, f, l: s.export_xml(f, l)
        elif opt in ("--export_rc"):
            action = lambda s, f, l: s.export_rc(l)
        elif opt in ("-F", "--file"): file = arg
        elif opt in ("-h", "--help"):
            action = lambda s, f, l: usage()
        elif opt in ("-i", "--import"):
            action = lambda s, f, l: s.import_xml(f, l)
        elif opt in ("-l", "--langid"): langid = arg
        elif opt in ("-t", "--trace"): trace = True
        elif opt in ("-A", "--add_language"): add_language = True
        elif opt in ("-R", "--remove_language"):
            action = lambda s, f, l: s.remove_language(l)
        elif opt in ("-n", "--langname"): langname = arg
        elif opt in ("-u", "--username"): username = arg
        elif opt in ("-p", "--password"): password = arg
        elif opt in ("-r", "--realname"): realname = arg
        elif opt in ("-e", "--email"): email = arg
        elif opt in ("-f", "--force"): force = True
        elif opt in ("--stringid"): stringid = arg
        elif opt in ("--text"): textstring = arg
        elif opt in ("--remove_item"): remove_item = True
        elif opt in ("--add_string"): add_string = True
        elif opt in ("--refid"): refid = arg
        elif opt in ("--keys"): actualkeys = arg
        elif opt in ("--add_accelerator"): add_accel = True
        elif opt in ("-s", "--strings"):
            action = lambda s, f, l: s.strings(l)
        elif opt in ("--all_strings"):
            action = lambda s, f, l: s.all_strings(l)
        elif opt in ("--audio_prompts"):
            action = lambda s, f, l: s.audio_prompts(l, arg)
    session = DBSession(trace, force, app)
    if add_language == True:
        session.add_language(langid, langname, username, password, realname, email)
    elif add_string == True:
        session.add_string(langid, textstring, stringid)
    elif remove_item == True:
        session.remove_item(langid, stringid)
    elif add_accel == True:
        session.add_accelerator(langid, textstring, stringid, refid, actualkeys)
    else:
        action(session, file, langid)

if __name__ == "__main__": main()
