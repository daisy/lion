import os
os.sys.path.append("../")

import DB.connect  # Harcoded DB connection info, not stored in SVN

class DBSession:
    """A session with the DB."""
    
    def __init__(self, host, dbname, trace=False):
        self.trace = trace      # trace flag
        self.warnings = 0       # warnings during operation
        self.connected = False  # no connection yet
        self.host = host
        self.dbname = dbname
    
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
        """Die with an error message and an error code. If the code is 0, don't die just yet."""
        os.sys.stderr.write("Error: %s\n" % msg)
        if err > 0: os.sys.exit(err)

    def connect(self):
        """Connect to the database."""
        if not self.connected:
            self.trace_msg("Connecting to the database...")
            self.db = DB.connect.db_connect("admin", self.host, self.dbname)
            self.cursor = self.db.cursor()
            # just for safety!
            self.cursor.execute("SET collation_connection = utf8_unicode_ci")
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
