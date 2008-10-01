from global_options_parser import *
from daisylion.db.liondb import LionDB

def main():
    usage = """usage: %prog [options] langid outputdir"""
    parser = GlobalOptionsParser(usage=usage)
    
    (options, args) = parser.parse_args()
    parser.check_args(2, args)
    
    session = LionDB(options.config, options.trace, "amis")
    langid = args[0]
    outputdir = args[1]
    session.module_export(langid, 3, outputdir)

if __name__=="__main__": main()


