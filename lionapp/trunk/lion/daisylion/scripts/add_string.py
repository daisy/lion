from global_options_parser import *
from daisylion.db.liondb import LionDB

def main():
    usage = """usage: %prog [options] langid string stringid"""
    parser = GlobalOptionsParser(usage=usage)
    (options, args) = parser.parse_args()
    parser.check_args(3, args)
    
    session = LionDB(options.config, options.trace, options.force, options.app)    
    langid, string, stringid = args
    session.add_string(langid, string, stringid)

if __name__=="__main__": main()


