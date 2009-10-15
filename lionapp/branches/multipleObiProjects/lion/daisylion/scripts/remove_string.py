from global_options_parser import *
from daisylion.db.liondb import LionDB

def main():
    usage = """usage: %prog [options] langid stringid"""
    parser = GlobalOptionsParser(usage=usage)
    (options, args) = parser.parse_args()
    parser.check_args(2, args)
    
    session = LionDB(options.config, options.trace, options.app)    
    langid, stringid = args
    # do a safety check to see if the user really wants to remove a string
    if parser.safety_check("remove a string") == True:
        session.remove_item(langid, stringid)

if __name__=="__main__": main()


