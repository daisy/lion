#!/usr/bin/python

# Manage the database

import getopt
import os
from xml.dom import minidom
# Harcoded DB connection info, not stored in SVN
os.sys.path.append("../")
from DB.connect import *

class DBSession:
    """A session with the DB."""

    def __init__(self, trace, app=None):
        self.trace = trace      # trace flag
        self.warnings = 0       # warnings during operation
        self.connected = False  # no connection yet
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
            #self.db = connect_to_db_from_local_machine("admin")
            self.db = connect_to_local_test_db("admin")
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
        print row
        if row != None: return row[0]
        else: return None

    
    def import_xml(self, file, langid):
        """Import from XML to the database."""
        if not file: die("No XML file given.")
        if not self.check_language(langid):
            die("No table for language %s." % langid)
        self.trace_msg("Import from " + file + " for " + langid)
        doc = minidom.parse(file)
        self.dbio.import_from_xml(self, doc, langid)
        self.process_db_flags(langid)
    
    
    def export(self, file, langid):
        self.dbio.export(self, file, langid)
    
    
    def process_db_flags(self, langid):
        """ Process the textflag values 
        (1 = nothing, 2 = changed, 3 = new, 4 = remove)"""
        table = langid.replace("-", "_")
        # get all the other languages except the master language
        self.execute_query("SELECT langid FROM languages WHERE langid != '%s'" % langid)
        languages = self.cursor.fetchall()
        self.execute_query("SELECT xmlid FROM %s WHERE textflag=2" % table)
        changed = self.cursor.fetchall()
        self.execute_query("SELECT textstring, xmlid, role, mnemonicgroup, target, actualkeys FROM %s WHERE textflag=3"\
         % table)
        newstuff = self.cursor.fetchall()
        self.execute_query("SELECT xmlid FROM %s WHERE textflag=4" % table)
        deleted = self.cursor.fetchall()
        
        for lang in languages:
            langtable = lang[0].replace("-", "_")
            # if something changed in the master table, flag it as changed in all other tables
            for row in changed:
                self.execute_query("UPDATE %(table)s SET textflag=2 WHERE xmlid='%(xmlid)s'" % \
                {"table": langtable, "xmlid": row[0]})
            
            # if something was added in the master table, add it to all other tables
            for row in newstuff:
                text, xmlid, role, mnemonicgroup, target, actualkeys = row
                self.execute_query("""INSERT INTO %(table)s (textstring, xmlid, role, 
                mnemonicgroup, target, actualkeys, textflag, audioflag)
                 VALUES ("%(text)s", "%(xmlid)s", "%(role)s", "%(mnem)s", "%(target)s",
                 "%(keys)s", 3, 3)""" % \
                 {"table": langtable, "text": text, "xmlid": xmlid, \
                 "role": role, "mnem": mnemonicgroup, "target": target, \
                 "keys": actualkeys})
            
            #if something was flagged for deletion in the master table, delete it from all other tables
            for row in deleted:
                self.execute_query("DELETE FROM %(table)s WHERE xmlid='%(xmlid)s'" % \
                {"table": langtable, "xmlid": row[0]})
                
        # now delete rows flagged for deletion in the master table
        for row in deleted:
            self.execute_query("DELETE FROM %(table)s WHERE xmlid='%(xmlid)s'" % \
            {"table": table, "xmlid": row[0]})
        

def usage(code=0):
    """Print usage information and exits with an error code."""
    print """
Usage:

  %(script)s --help                              Show this help message.
  %(script)s --import --language=id --file=file  Import file into table id.
  %(script)s --export --language=id --file=file  Export to XML


Other options:
  --application, -a: which application module to use (e.g. "amis" or "obi")
  --trace, -t: trace mode (send trace messages to stderr.)

""" % {"script": os.sys.argv[0]}
    os.sys.exit(code)


def main():
    """Parse command line arguments and run."""
    app = "amis"
    trace = False
    action = lambda s, f, l: usage(1)
    file = None
    langid = None
    try:
        opts, args = getopt.getopt(os.sys.argv[1:], "a:ef:hil:t",
            ["application=", "export", "file=", "help", "import", "language=",
                "trace"])
    except getopt.GetoptError, e:
        os.sys.stderr.write("Error: %s" % e.msg)
        usage(1)
    for opt, arg in opts:
        if opt in ("-a", "--application"): app = arg
        elif opt in ("-e", "--export"):
            action = lambda s, f, l: s.export(f, l)
        elif opt in ("-f", "--file"): file = arg
        elif opt in ("-h", "--help"):
            action = lambda s, f, l: usage()
        elif opt in ("-i", "--import"):
            action = lambda s, f, l: s.import_xml(f, l)
        elif opt in ("-l", "--language"): langid = arg
        elif opt in ("-t", "--trace"): trace = True
    session = DBSession(trace, app)
    action(session, file, langid)

if __name__ == "__main__": main()
