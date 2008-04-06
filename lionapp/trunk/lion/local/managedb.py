#!/usr/bin/python

# Manage the database

import getopt
import os
from xml.dom import minidom

# Harcoded DB connection info, not stored in SVN
os.sys.path.append("../")
from DB.connect import *

# TODO select this module dynamically
import dbio_amis

class DBSession:
    """A session with the DB."""

    def __init__(self, trace):
        self.trace = trace  # trace flag
        self.warnings = 0   # warnings during operation
        self.connect()

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
            self.disconnect()
            os.sys.exit(err)

    def connect(self):
        """Connect to the database."""
        self.trace_msg("Connecting to the database...")
        self.db = connect_to_db_from_local_machine("admin")
        self.cursor = self.db.cursor()
        self.trace_msg("... connected")

    def disconnect(self):
        """Disconnect from the database."""
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
        for langname in self.cursor:
            self.trace_msg("%s is %s." % (langid, langname))
            return True
        return False


def usage(code=0):
    """Print usage information and exits with an error code."""
    print """
Usage:

  %(script)s --help                              Show this help message.
  %(script)s --import --language=id --file=file  Import file into table id.
  %(script)s --export                            Export to XML

Other options:
  --trace, -t: trace mode (send trace messages to stderr.)

""" % {"script": os.sys.argv[0]}
    os.sys.exit(code)

def import_action(session, file, langid):
    """Import."""
    session.trace_msg("Import from " + file + " for " + langid)
    doc = minidom.parse(file)
    dbio_amis.import_from_xml(session, doc, langid)

def export_action(session, file, langid):
    """Export."""
    session.trace_msg("Export to " + file + " for " + langid)

def main():
    """Parse command line arguments and run."""
    trace = False
    errors = 0
    action = None
    file = None
    langid = None
    try:
        opts, args = getopt.getopt(os.sys.argv[1:], "ef:hil:t",
            ["export", "file", "help", "import", "language", "trace"])
    except getopt.GetoptError, e:
        die(e.msg, 0)
        usage(1)
    for opt, arg in opts:
        if opt in ("-e", "--export"): action = export_action
        elif opt in ("-f", "--file"): file = arg
        elif opt in ("-h", "--help"): usage()
        elif opt in ("-i", "--import"): action = import_action
        elif opt in ("-l", "--language"): langid = arg
        elif opt in ("-t", "--trace"): trace = True
    errors = 0
    if not action:
        die("no action defined.", 0)
        errors += 1
    if not file:
        die("no XML file given.", 0)
        errors += 1
    if not langid:
        die("no language code given.", 0)
        errors += 1
    if errors: usage(1)
    session = DBSession(trace)
    if not session.check_language(langid):
        session.die("""No table for language "%s".""" % langid)
    action(session, file, langid)
    session.disconnect()

if __name__ == "__main__": main()
