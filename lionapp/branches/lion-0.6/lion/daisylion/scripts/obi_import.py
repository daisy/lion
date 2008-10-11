from global_options_parser import *
from daisylion.db.liondb import LionDB

def main():
    parser = GlobalOptionsParser(usage="usage: %prog [options] langid file ...")
    (options, args) = parser.parse_args()
    parser.check_args_atleast(2, args)
    session = LionDB(options.config, options.trace)
    langid = args.pop(0)
    session.trace_msg("Import for langid=%s with %s" % (langid, args))
    session.module_import(args, langid, 1)

if __name__=="__main__": main()
