from global_options_parser import *
from daisylion.db.liondb import LionDB

def main():
    usage = """usage: %prog [options] string stringid
    Edits the master language and updates all other languages."""
    parser = GlobalOptionsParser(usage=usage)
    (options, args) = parser.parse_args()
    parser.check_args(2, args)
    
    session = LionDB(options.config, options.trace, options.app)    
    string, stringid = args
    session.add_string_master(string, stringid)

if __name__=="__main__": main()


