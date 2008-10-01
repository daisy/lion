from global_options_parser import *
from daisylion.db.liondb import LionDB

def main():
    usage = """usage: %prog"""
    parser = GlobalOptionsParser(usage=usage)
    (options, args) = parser.parse_args()
    parser.check_args(0, args)
    
    session = LionDB(options.config, options.trace, options.app)    
    results = session.list_all_languages()
    for r in results:
        usernamepwd = "(%s, %s)" % (r[3], r[4])
        line = "%-10s%-30s%-20s %-10s" % (r[0], r[1], r[2], usernamepwd) 
        print line
    
if __name__=="__main__": main()


