from global_options_parser import *
from daisylion.db.liondb import LionDB

def main():
    usage = """usage: %prog [options] langid
    """
    parser = GlobalOptionsParser(usage=usage)
    (options, args) = parser.parse_args()
    parser.check_args(1, args)
    
    session = LionDB(options.config, options.trace, options.app)    
    langid = args[0]
    
    table = session.make_table_name(langid)
    session.execute_query("SELECT remarks, xmlid, textstring from %s" % table)
    results = session.cursor.fetchall()
    
    skipped = 0
    changed = 0
    for remarks, xmlid, textstring in results:
        if remarks != None and remarks != "":
            request = """UPDATE %s SET textstring="%s" WHERE xmlid="%s" """ % (table, remarks, xmlid)
            # print request
            session.execute_query(request)
            changed +=1
        else:
            print "skipping %s (text = %s)" % (xmlid, textstring)
            skipped +=1
    
    print "Skipped %d, Changed %d" % (skipped, changed)
	

if __name__=="__main__": main()
