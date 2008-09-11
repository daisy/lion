from global_options_parser import *
from daisylion.db.liondb import LionDB

def main():
    usage = """usage: %prog [options] langid username password
    The language referenced by langid must already exist.
    """
    parser = GlobalOptionsParser(usage=usage)
    parser.add_option("-r", "--realname", dest="realname", default="",
        help="The full name of the user")
    parser.add_option("-e", "--email", dest="email", default="",
        help="The user's email address")
    (options, args) = parser.parse_args()
    parser.check_args(3, args)
    
    session = LionDB(options.config, options.trace, options.force, options.app)
    langid, username, pwd = args
    session.add_user(langid, username, pwd, options.realname, options.email)

if __name__=="__main__": main()
