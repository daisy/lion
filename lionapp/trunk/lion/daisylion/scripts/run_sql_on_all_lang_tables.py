from global_options_parser import *
from daisylion.db.liondb import LionDB

def main():
    usage = """usage: %prog [options] sqlstatement
    Type %s for the language table name
    
    This will run the sql query on all language tables"""
    
    parser = GlobalOptionsParser(usage=usage)
    (options, args) = parser.parse_args()
    parser.check_args(1, args)
    
    session = LionDB(options.config, options.trace, options.app)    
    sql = args[0]
    
    request = "SELECT langid FROM languages"
    
    session.execute_query(request)
    all_langs = session.cursor.fetchall()
    if parser.safety_check("run this query on each language table") == False:
        exit(1)
    
    for l in all_langs:
        request = sql % session.make_table_name(l[0])
        try:
            session.execute_query(request)
        except Exception, e:
            print "Exception: %s" % e
    
if __name__=="__main__": main()


