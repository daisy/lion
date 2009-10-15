from global_options_parser import *
from daisylion.db.liondb import LionDB

def main():
    usage = """usage: %prog"""
    parser = GlobalOptionsParser(usage=usage)
    parser.add_option("-s", "--short", dest="shortlist", 
        help="Show only the language name", action="store_true", default=False)
    parser.add_option("-d", "--date", dest="orderbydate", 
        help="Order by login date", action="store_true", default=False)
    parser.add_option("-w", "--work", dest="orderbytodo",
        help="Order by the number of work items remaining (new or todo)", action="store_true", default=False)
    (options, args) = parser.parse_args()
    parser.check_args(0, args)
    
    session = LionDB(options.config, options.trace, options.app)    
    results = session.list_all_languages(options.orderbydate, options.orderbytodo)
    
    # the data coming back looks like this:
    # workleft (optional), langid, langname, realname, username, password, lastlogin (optional)
    # workleft and lastlogin are mutually exclusive
    # if workleft is being returned, then the remaining results are wrapped up in a tuple
    # as in (34, ('langid', 'langname', etc))
    print "%d languages" % len(results)
    if options.orderbydate == True:
        print "Showing most recently logged-in first"
    if options.orderbytodo == True:
        print session.get_table_length(session.masterlang)
        print session.masterlang
        print "Showing the most work remaining first (items out of %s total still needing translation)" % \
            session.get_table_length(session.masterlang)
    
    for r in results:
        if options.orderbytodo == False: usernamepwd = "(%s, %s)" % (r[3], r[4])
        if options.shortlist == True:
                line = r[1]
        else:
            if options.orderbydate == True:
                line = "%-25s%-10s%-30s%-20s %-10s" % (r[5], r[0], r[1], r[2], usernamepwd)
            elif options.orderbytodo == True:
                usernamepwd = "(%s, %s)" % (r[1][3], r[1][4])
                line = "%-25s%-10s%-30s%-20s %-10s" % (r[0], r[1][0], r[1][1], r[1][2], usernamepwd)
            else:
                line = "%-10s%-30s%-20s %-10s" % (r[0], r[1], r[2], usernamepwd) 
        print line.encode("utf-8")
    
if __name__=="__main__": main()


