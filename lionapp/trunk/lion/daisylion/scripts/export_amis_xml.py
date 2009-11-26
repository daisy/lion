from global_options_parser import *
from daisylion.db.liondb import LionDB

def main():
    usage = """usage: %prog [options] langid"""
    parser = GlobalOptionsParser(usage=usage)
    parser.add_option("-v", "--amisversion", dest="amis_version", default="3.1", 
        help="Target version of AMIS (default = 3.1)")
    
    (options, args) = parser.parse_args()
    parser.check_args(1, args)
    
    session = LionDB(options.config, options.trace, "amis")
    langid = args[0]
    print session.module_export(langid, 1, (options.amis_version,))

if __name__=="__main__": main()


