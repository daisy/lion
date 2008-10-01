from global_options_parser import *
from daisylion.db.liondb import LionDB

def main():
    usage = """usage: %prog [options] username"""
    parser = GlobalOptionsParser(usage=usage)
    (options, args) = parser.parse_args()
    parser.check_args(1, args)
    
    session = LionDB(options.config, options.trace, options.app)    
    username = args[0]
    if parser.safety_check("remove a user") == True:
        session.remove_user(username)

if __name__=="__main__": main()


