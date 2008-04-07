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
                self.die("""Unknown application "%s" (%s)""" % (app, e.msg))
        self.connect()

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

    def die(self, msg, err=1):
        """Die with an error message and an error code. If the code is 0, don't
die just yet."""
        os.sys.stderr.write("Error: %s\n" % msg)
        if err > 0:
            os.sys.exit(err)

    def connect(self):
        """Connect to the database."""
        if not self.connected:
            self.trace_msg("Connecting to the database...")
            self.db = connect_to_db_from_local_machine("admin")
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
        self.trace_msg("""Query: "%s".""" % q)
        self.cursor.execute(q)

    def check_language(self, langid):
        """Check the existence of a table for the given language id."""
        self.execute_query("SELECT langname FROM languages WHERE langid='%s'" \
            % langid)
        row = self.cursor.fetchone()
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
    action = None
    file = None
    langid = None
    try:
        opts, args = getopt.getopt(os.sys.argv[1:], "a:ef:hil:t",
            ["application", "export", "file", "help", "import", "language",
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
    if not action:
        die("no action defined.", 0)
        usage(1)
    session = DBSession(trace, app)
    action(session, file, langid)

if __name__ == "__main__": main()
