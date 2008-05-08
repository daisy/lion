#!/usr/bin/python

# Manage the database

import getopt
import os
from xml.dom import minidom
# Harcoded DB connection info, not stored in SVN
os.sys.path.append("../")
from DB.connect import *
import addremove_language
import addremove_string

class DBSession:
    """A session with the DB."""

    def __init__(self, trace, app=None, force):
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
            self.db = connect_to_db_from_local_machine("admin")
            #self.db = connect_to_local_test_db("admin")
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
            % {"table": make_table_name(langid), "xmlid": stringid})
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
    
    def export(self, file, langid):
        self.dbio.export(self, file, langid)
    
    def process_changes(self, langid, removed_ids):
        """ Process the textflag values (1 = nothing, 2 = changed, 3 = new)
        and the IDs to remove"""
        table = self.make_table_name(langid)
        # get all the other languages except the master language
        self.execute_query("SELECT langid FROM languages WHERE langid != '%s'" \
            % langid)
        languages = self.cursor.fetchall()
        # get the changed items
        self.execute_query("SELECT xmlid FROM %s WHERE textflag=2" % table)
        changed = self.cursor.fetchall()
        # get the new items
        self.execute_query("SELECT textstring, xmlid, role, mnemonicgroup, \
        target, actualkeys FROM %s WHERE textflag=3" % table)
        newstuff = self.cursor.fetchall()
        # for every language (except the master language), 
        # make the appropriate changes
        if languages != None:
            for lang in languages:
                langtable = self.make_table_name(lang[0])
                # if something changed in the master table, 
                # flag it as changed in all other tables
                if changed != None:
                    for row in changed:
                        self.execute_query("UPDATE %(table)s SET textflag=2 WHERE \
                            xmlid='%(xmlid)s'" % {"table": langtable, "xmlid": row[0]})
                
                # if something was added in the master table, 
                # add it to all other tables
                if newstuff != None:
                    for row in newstuff:
                        text, xmlid, role, mnemonicgroup, target, actualkeys = row
                        self.execute_query("""INSERT INTO %(table)s (textstring, \
                            xmlid, role, mnemonicgroup, target, actualkeys, textflag, \
                            audioflag)
                            VALUES ("%(text)s", "%(xmlid)s", "%(role)s", "%(mnem)s", \
                            "%(target)s", "%(keys)s", 3, 3)""" % \
                            {"table": langtable, "text": text, "xmlid": xmlid, \
                            "role": role, "mnem": mnemonicgroup, "target": target, \
                            "keys": actualkeys})
                
            
            # end languages loop
            
            #if something was flagged for deletion in the master document, 
            # delete it from all other tables
            if removed_ids != None:
                for id in removed_ids:
                    self.execute_query("DELETE FROM %(table)s WHERE \
                        xmlid='%(xmlid)s'" % {"table": langtable, "xmlid": id}
    
    def add_language(self, langid, langname, username, password, realname, email):
        addremove_language.add_language(self, langid, langname, username, password, realname, email)
    
    def remove_language(self, langid, force):
        addremove_language.remove_language(self, langid, force)
    
    def add_string(self, langid, string, stringid, role, keys, force):
        success = self.dbio.add_string(self, langid, string, stringid, force)
        if success == True:
            process_changes(langid, None)
    
    def remove_string(self, langid, stringid, force):
        success = self.dbio.remove_string(self, langid, stringid, force)
        if success == True:
            removed_ids = stringid,
            process_changes(langid, removed_ids)
        
    
def usage(code=0):
    """Print usage information and exits with an error code."""
    print """
Usage:

  %(script)s --help                              Show this help message.
  %(script)s --import --langid=id --file=file    Import file into table id.
  %(script)s --export --langid=id --file=file    Export to XML
  %(script)s --add_language --langid=id --langname=langname \
--username=username --password=password --email=email \
--realname=realname                              
                                                 Add a new language
  %(script)s --remove_language --langid=id       Remove a language
  %(script)s --add_string --langid=id --string=string --stringid=itemid 
                                                 Add a string to all tables
  %(script)s --remove_string --langid=id --stringid=itemid
                                                 Remove an item from all tables
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
    # if the action is add/remove a language/string, the parameters are different
    add_language = False  
    remove_language = False
    add_string = False
    remove_string = False
    string = None
    stringid = None
    try:
        """
        a: - application
        e  - export
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
        """
        opts, args = getopt.getopt(os.sys.argv[1:], "a:eF:hil:tn:u:p:r:e:fAR",
            ["application=", "export", "file=", "help", "import", "langid=",
                "trace", "add_language", "remove_language", "langname=", 
                "username=", "password=", "realname=", "email=", "force", 
                "stringid=", "string", "remove_item", "add_string"])
    except getopt.GetoptError, e:
        os.sys.stderr.write("Error: %s" % e.msg)
        usage(1)
    for opt, arg in opts:
        if opt in ("-a", "--application"): app = arg
        elif opt in ("-e", "--export"):
            action = lambda s, f, l: s.export(f, l)
        elif opt in ("-F", "--file"): file = arg
        elif opt in ("-h", "--help"):
            action = lambda s, f, l: usage()
        elif opt in ("-i", "--import"):
            action = lambda s, f, l: s.import_xml(f, l)
        elif opt in ("-l", "--langid"): langid = arg
        elif opt in ("-t", "--trace"): trace = True
        elif opt in ("-A", "--add_language"): add_language = True
        elif opt in ("-R", "--remove_language"):remove_language = True
        elif opt in ("-n", "--langname"): langname = arg
        elif opt in ("-u", "--username"): username = arg
        elif opt in ("-p", "--password"): password = arg
        elif opt in ("-r", "--realname"): realname = arg
        elif opt in ("-e", "--email"): email = arg
        elif opt in ("-f", "--force"): force = True
        elif opt in ("--stringid"): stringid = arg
        elif opt in ("--string"): string = arg
        elif opt in ("--remove_item"): remove_string = True
        elif opt in ("--add_string"): add_string = True
    session = DBSession(trace, app, force)
    if add_language == True:
        session.add_language(langid, langname, username, password, realname, email)
    elif remove_language == True:
        session.remove_language(langid)
    elif add_string == True:
        session.add_string(langid, string, stringid)
    elif remove_item == True:
        session.remove_string(langid, stringid)
    else:
        action(session, file, langid)

if __name__ == "__main__": main()
