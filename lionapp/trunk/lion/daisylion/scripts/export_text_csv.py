from global_options_parser import *
from daisylion.db.liondb import LionDB

def main():
    usage = """usage: %prog langid"""
    parser = GlobalOptionsParser(usage=usage)
    
    (options, args) = parser.parse_args()
    parser.check_args(1, args)
    
    session = LionDB(options.config, options.trace, options.app)    
    results = session.all_strings_bilingual(args[0])
    for r in results:
        print "%s, %s" % (r[0], r[1])
    
    
if __name__=="__main__": main()


