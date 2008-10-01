from global_options_parser import *
from daisylion.db.liondb import LionDB

def main():
    usage = """usage: %prog [options] langid"""
    parser = GlobalOptionsParser(usage=usage)
    
    (options, args) = parser.parse_args()
    parser.check_args(1, args)
    
    session = LionDB(options.config, options.trace, "amis")
    langid = args[0]
    session.module_export(langid, 1, None)

if __name__=="__main__": main()


