from global_options_parser import *
from daisylion.db.liondb import LionDB

def main():
    """Update the release date and version info for the english table"""
    
    usage = """usage: %prog [options] version_info release_date"""
    parser = GlobalOptionsParser(usage=usage)
    
    (options, args) = parser.parse_args()
    parser.check_args(2, args)
    
    session = LionDB(options.config, options.trace, "amis")
    
    # t164 = version info
    # t165 = release date
    session.execute_query("""UPDATE eng_US SET textstring="%s" WHERE xmlid="t164" """ % args[0])
    session.execute_query("""UPDATE eng_US SET textstring="%s" WHERE xmlid="t165" """ % args[1])
    
    print "Successfully updated"
    
if __name__=="__main__": main()


