from global_options_parser import *
from daisylion.db.liondb import LionDB

def main():
    parser = GlobalOptionsParser(usage="usage: %prog [options] langid file ...")
    parser.add_option("-i", "--importtype", dest="import_type", default=1,
        help="Import type (1: import, 2: populate, 3: update")
    (options, args) = parser.parse_args()
    parser.check_args_atleast(2, args)
    session = LionDB(options.config, options.trace)
    langid = args.pop(0)
    session.trace_msg("Import for langid=%s with %s" % (langid, args))
    session.module_import(args, langid, int(options.import_type))

if __name__=="__main__": main()
