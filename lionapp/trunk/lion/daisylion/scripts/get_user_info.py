from global_options_parser import *
from daisylion.db.liondb import LionDB

def main():
    usage = """usage: %prog [options] langid
    """
    parser = GlobalOptionsParser(usage=usage)
    (options, args) = parser.parse_args()
    parser.check_args(1, args)
    
    session = LionDB(options.config, options.trace, options.app)    
    langid = args[0]
    user_info = session.get_user_info(langid)
    s = ""
    for i in user_info:
        s += "%-25s" % i
    print s

if __name__=="__main__": main()
