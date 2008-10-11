from global_options_parser import *
from daisylion.db.liondb import LionDB
from daisylion.db.modules.amis import amisxml
from xml.dom import minidom
import run_sql_on_all_lang_tables

def main():
    """For whatever"""
    usage = """usage: %prog [options] xmlfile"""
    
    parser = GlobalOptionsParser(usage=usage)
    (options, args) = parser.parse_args()
    parser.check_args(1, args)
    session = LionDB(options.config, options.trace, options.app)    
    
    minidom.Document = amisxml.AmisUiDoc
    doc = minidom.parse(args[0])
    doc.set_session(session)
    
    all_xml_ids = doc.get_all_text_ids()
    session.execute_query("SELECT langid FROM languages")
    all_langs = session.cursor.fetchall()
    count = 0
    
    # make the list of IDs that are to be preserved
    request = "SELECT xmlid, textstring FROM eng_US" #"%s" % session.make_table_name(l[0])
    session.execute_query(request)
    all_table_ids = session.cursor.fetchall()
    preserve_list = []
    for id, txt in all_table_ids:
        if id not in all_xml_ids:
            count += 1
            preserve_list.append(id)
            print id, txt
    
    print "Of %d IDs in the DB, %d were not found" % (len(all_table_ids), count)
    
    # now mark each item in that list as preserve = 1 for each language
    
    for l in all_langs:
        table = session.make_table_name(l[0])
        for id in preserve_list:
            request = """UPDATE %s SET preserve=1 WHERE xmlid="%s" """ % (table, id)
            session.execute_query(request)
    
if __name__=="__main__": main()


