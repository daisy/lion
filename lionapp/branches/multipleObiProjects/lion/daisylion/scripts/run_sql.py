from global_options_parser import *
from daisylion.db.liondb import LionDB

def main():
    usage = """usage: %prog [options] sqlstatement
    Run a single SQL query."""
    
    parser = GlobalOptionsParser(usage=usage)
    (options, args) = parser.parse_args()
    parser.check_args(1, args)
    
    session = LionDB(options.config, options.trace, options.app)    
    sql = args[0]
    session.execute_query(sql)
    if session.cursor.rowcount != 0:
        for r in session.cursor.fetchall():
            for field in r:
                print field
    
if __name__=="__main__": main()


