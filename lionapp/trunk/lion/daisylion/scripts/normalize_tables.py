from global_options_parser import *
from daisylion.db.liondb import LionDB

def main():
    usage = """usage: %prog
    Normalizes imbalances in the DB"""
    parser = GlobalOptionsParser(usage=usage)
    (options, args) = parser.parse_args()
    parser.check_args(0, args)
    session = LionDB(options.config, options.trace, options.app)    
    
    warn1 = "remove items from all tables that aren't in %s" % session.masterlang
    warn2 = "add missing items to all tables from %s " % session.masterlang
    
    if parser.safety_check(warn1) == False:
        exit(1)
    if parser.safety_check(warn2) == False:
        exit(1)
    
    # first get a list of the diffs between each language and the master language
    request = "SELECT langid FROM languages"
    session.execute_query(request)
    langs = session.cursor.fetchall()
    
    for l in langs:
        lid = l[0]
        diffs = session.list_langtable_diffs(lid, session.masterlang)
        if diffs != None:
            longer, shorter, data = diffs
            # if the given language has more entries than the master language, remove the extras
            if longer == lid:
                for d in data:
                    xmlid = d[0]
                    session.remove_item(lid, xmlid)
            
            # if the given language has fewer entries than the master language, copy the relevant items over
            else:
                for d in data:
                    xmlid = d[0]
                    session.copy_item(xmlid, session.masterlang, lid)
                

if __name__=="__main__": main()


