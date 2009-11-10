from global_options_parser import *
from daisylion.db.liondb import LionDB
from daisylion.db.modules.amis import amisxml
from xml.dom import minidom
import run_sql_on_all_lang_tables

def main():
    """For whatever"""
    usage = """usage: %prog [options] langid"""
    
    parser = GlobalOptionsParser(usage=usage)
    (options, args) = parser.parse_args()
    parser.check_args(1, args)
    session = LionDB(options.config, options.trace, options.app)    
    
    s = session.all_strings(args[0])
    print s

    l = session.all_strings_length(args[0])
    print l
        
if __name__=="__main__": main()


