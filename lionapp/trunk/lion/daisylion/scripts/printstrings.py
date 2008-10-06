from global_options_parser import *
from daisylion.db.liondb import LionDB

def main():
    usage = """usage: %prog [options] langid
    The language referenced by langid must already exist.
    """
    parser = GlobalOptionsParser(usage=usage)
    parser.add_option("-d", "--all", dest="all", default="False", action="store_true",
        help="Output all strings, including keyboard-related items.")
    (options, args) = parser.parse_args()
    parser.check_args(1, args)
    
    session = LionDB(options.config, options.trace, options.app)    
    langid = args[0]
    if options.all == True:
        if parser.safety_check("for fun"):
            print session.all_strings(langid)
    else:
        print session.textstrings(langid)

if __name__=="__main__": main()
