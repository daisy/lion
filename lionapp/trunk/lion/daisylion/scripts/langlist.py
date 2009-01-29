from global_options_parser import *
from daisylion.db.liondb import LionDB

def main():
    usage = """usage: %prog"""
    parser = GlobalOptionsParser(usage=usage)
    parser.add_option("-s", "--short", dest="shortlist", 
        help="Show only the language name", action="store_true", default=False)
    parser.add_option("-d", "--date", dest="orderbydate", 
        help="Order by login date", action="store_true", default=False)
    (options, args) = parser.parse_args()
    parser.check_args(0, args)
    
    session = LionDB(options.config, options.trace, options.app)    
    results = session.list_all_languages(options.orderbydate)
    
    # the data coming back looks like this:
    # langid, langname, realname, username, password, lastlogin (optional)
    
    print "%d languages" % len(results)
    if options.orderbydate == True:
        print "Showing most recently logged-in first"
    
    for r in results:
        usernamepwd = "(%s, %s)" % (r[3], r[4])
        if options.shortlist == True:
                line = r[1]
        else:
            if options.orderbydate == True:
                line = "%-25s%-10s%-30s%-20s %-10s" % (r[5], r[0], r[1], r[2], usernamepwd)
            else:
                line = "%-10s%-30s%-20s %-10s" % (r[0], r[1], r[2], usernamepwd) 
        print line.encode("utf-8")
    
if __name__=="__main__": main()


