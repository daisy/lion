from global_options_parser import *
from daisylion.db.liondb import LionDB

def main():
    usage = """usage: %prog [options] langid"""
    parser = GlobalOptionsParser(usage=usage)
    (options, args) = parser.parse_args()
    parser.check_args(1, args)
    
    session = LionDB(options.config, options.trace, options.app)    
    langid = args[0]
    if parser.safety_check("remove %s" % langid) == True:
        session.remove_language(langid)

if __name__=="__main__": main()


