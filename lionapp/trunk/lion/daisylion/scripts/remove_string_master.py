from global_options_parser import *
from daisylion.db.liondb import LionDB

def main():
    usage = """usage: %prog [options] stringid
    Edits the master language and updates all other languages."""
    parser = GlobalOptionsParser(usage=usage)
    (options, args) = parser.parse_args()
    parser.check_args(1, args)
    
    session = LionDB(options.config, options.trace, options.app)    
    stringid = args[0]
    # do a safety check to see if the user really wants to remove a string
    if parser.safety_check("remove a string in ALL tables") == True:
        session.remove_item_master(stringid)

if __name__=="__main__": main()


