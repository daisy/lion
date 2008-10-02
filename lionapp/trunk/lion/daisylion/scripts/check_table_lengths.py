from global_options_parser import *
from daisylion.db.liondb import LionDB

def main():
    usage = """usage: %prog
    Report if all tables are the same length"""
    parser = GlobalOptionsParser(usage=usage)
    (options, args) = parser.parse_args()
    parser.check_args(0, args)
    session = LionDB(options.config, options.trace, options.app)    
    
    # first get a list of the diffs between each language and the master language
    request = "SELECT langid FROM languages"
    session.execute_query(request)
    langs = session.cursor.fetchall()
    any_diffs_found = False
    for l in langs:
        lid = l[0]
        diffs = session.list_langtable_diffs(lid, session.masterlang)
        if diffs != None:
            any_diffs_found = True
            longer, shorter, data = diffs
            if longer == lid:
                print "%s has more entries than %s" % (lid, session.masterlang)
            else:
                print "%s has fewer entries than %s" % (lid, session.masterlang)
        
    if any_diffs_found == False:
        print "All tables are the same length as %s" % session.masterlang


if __name__=="__main__": main()


