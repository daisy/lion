from global_options_parser import *
from daisylion.db.liondb import LionDB

def main():
    """which are the top-level accelerators?"""
    usage = """usage: %prog [options] langid"""
    parser = GlobalOptionsParser(usage=usage)
    (options, args) = parser.parse_args()
    parser.check_args(1, args)
    session = LionDB(options.config, options.trace, options.app)    
    table = session.make_table_name(args[0])
    # top level menu items
    request = "SELECT xmlid, textstring FROM %s WHERE istoplevel=1 and role=\"MENUITEM\"" % table
    session.execute_query(request)
    menuitems = session.cursor.fetchall()
    accels = []
    for id, text in menuitems:
        request = "SELECT textstring, audiouri, xmlid FROM %s WHERE target=\"%s\" and role=\"ACCELERATOR\"" % \
            (table, id)
        session.execute_query(request)
        info = (text, id), session.cursor.fetchone()
        accels.append(info)
    for a in accels: 
        print "Item: %s (id=%s)" % (a[0][0], a[0][1])
        print "Shortcut: %s (id=%s)" % (a[1][0], a[1][2])
        print "Audio file: %s" % a[1][1]
        print ""

    
if __name__=="__main__": main()

