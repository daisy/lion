from global_options_parser import *
from daisylion.db.liondb import LionDB

def main():
    usage = """usage: %prog langid1 langid2"""
    parser = GlobalOptionsParser(usage=usage)
    (options, args) = parser.parse_args()
    parser.check_args(2, args)
    
    session = LionDB(options.config, options.trace, options.app)    
    results = session.list_langtable_diffs(args[0], args[1])
    if results == None:
        print "Tables are equal"
    else:
        longer, shorter, data = results
        print "Items in %s that are not in %s" % (longer, shorter)
        
        for r in data:
            print "%-10s%-10s" % (r[0], r[1]) 
    
if __name__=="__main__": main()