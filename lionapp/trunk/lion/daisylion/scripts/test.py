from global_options_parser import *
from daisylion.db.liondb import LionDB

def main():
    """Simple way to test a function in the LionDB"""
    usage = """usage: %prog [options]"""
    
    parser = GlobalOptionsParser(usage=usage)
    (options, args) = parser.parse_args()
    parser.check_args(0, args)
    
    session = LionDB(options.config, options.trace, options.app)    
    if session.has_accelerators():
        print "YES"
    else:
        print "NO"
    
    
if __name__=="__main__": main()


