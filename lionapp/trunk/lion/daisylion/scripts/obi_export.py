from global_options_parser import *
from daisylion.db.liondb import LionDB

def main():
    parser = GlobalOptionsParser(usage="usage: %prog [options] langid dir")
    (options, args) = parser.parse_args()
    parser.check_args(2, args)
    session = LionDB(options.config, options.trace)
    langid, dir = args
    session.trace_msg("Export for langid=%s to directory %s" % (langid, dir))
    additional_params = (dir,)
    session.module_export(langid, 0, additional_params)

if __name__=="__main__": main()
