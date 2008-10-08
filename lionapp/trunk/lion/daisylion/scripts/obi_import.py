from global_options_parser import *
from daisylion.db.liondb import LionDB

def main():
    parser = GlobalOptionsParser(usage="usage: %prog [options] langid file ...")
    (options, args) = parser.parse_args()
    parser.check_args(2, args)
    session = LionDB(options.config, options.trace)
    langid, file = args
    session.module_import(file, langid, 1)

if __name__=="__main__": main()
