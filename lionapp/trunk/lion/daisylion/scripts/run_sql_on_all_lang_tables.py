from global_options_parser import *
from daisylion.db.liondb import LionDB

def main():
    usage = """usage: %prog [options] sqlstatement
    Type %(table)s as a token for the language table name
    
    This will run the sql query on all language tables"""
    
    parser = GlobalOptionsParser(usage=usage)
    (options, args) = parser.parse_args()
    parser.check_args(1, args)
    session = LionDB(options.config, options.trace, options.app)    
    
    if parser.safety_check("run this query on each language table") == False:
        exit(1)
    
    sql = args[0]
    run_sql_on_all_lang_tables(session, sql)

def run_sql_on_all_lang_tables(session, sql):
    request = "SELECT langid FROM languages"
    
    session.execute_query(request)
    all_langs = session.cursor.fetchall()
    
    retvals = {}
    
    for l in all_langs:
        table = session.make_table_name(l[0])
        request = sql % {"table": table}
        try:
            session.execute_query(request)
            if session.cursor.rowcount > 0:
                rows = session.cursor.fetchall()
                for r in rows:
                    for field in r:
                        print field
                retvals[table] = rows
        except Exception, e:
            print "Exception: %s" % e
    
    return retvals
    
if __name__=="__main__": main()


