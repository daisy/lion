from global_options_parser import *
from daisylion.db.liondb import LionDB
from daisylion.db.modules.amis import amisxml
from xml.dom import minidom
from run_sql_on_all_lang_tables import run_sql_on_all_lang_tables

def main():
    # who customized the menu mnemonics?
    usage = """usage: %prog [options]"""
    
    parser = GlobalOptionsParser(usage=usage)
    (options, args) = parser.parse_args()
    parser.check_args(0, args)
    session = LionDB(options.config, options.trace, options.app)    
    
    # top level menu items
    request = "SELECT xmlid FROM eng_US WHERE istoplevel=1 and role=\"MENUITEM\""
    session.execute_query(request)
    menuitems = session.cursor.fetchall()
    
    mnemonic_ids = []
    for id in menuitems:
        request = "SELECT xmlid FROM eng_US WHERE target=\"%s\" and role=\"MNEMONIC\"" % id
        session.execute_query(request)
        mnemonic_ids.append(session.cursor.fetchone()[0])
    
    tablelist = []
    # look in each table vs eng_US for the mnemonic value and see if it's different
    for id in mnemonic_ids:
        request = """select eng_US.textstring, %%(table)s.textstring from eng_US, 
        %%(table)s where eng_US.xmlid="%s" and %%(table)s.xmlid="%s" """ % (id, id)
        result = run_sql_on_all_lang_tables(session, request)
        # result is a langtable:rows dictionary
        # ('hin_IN', ( ('H', 'X'),() ) )  
        for item in result.items():
            table = item[0]
            row = item[1][0]
            eng = row[0]
            other = row[1]
            if eng != other and table not in tablelist: tablelist.append(table)
    
    for table in tablelist:
        langid = table.replace("_", "-")
        request = "SELECT email FROM users WHERE langid=\"%s\" " % langid
        session.execute_query(request)
        e = session.cursor.fetchone()
        if e is not None: 
            e = e[0]
            print "%s, " % e



def set_toplevel_accel():
    usage = """usage: %prog [options] langid"""
    
    parser = GlobalOptionsParser(usage=usage)
    (options, args) = parser.parse_args()
    parser.check_args(0, args)
    session = LionDB(options.config, options.trace, options.app)    
    
    request = "select xmlid from eng_US where istoplevel=1 and role=\"MENUITEM\""
    session.execute_query(request)
    menuitems = session.cursor.fetchall()
    
    accel_mnem = []
    # for each menu item, find the mnemonic and the accelerator
    for id in menuitems:
        request = "select xmlid from eng_US where target=\"%s\" and role=\"MNEMONIC\"" % id
        session.execute_query(request)
        m = session.cursor.fetchone()[0]
        request = "select xmlid from eng_US where target=\"%s\" and role=\"ACCELERATOR\"" % id
        session.execute_query(request)
        a = session.cursor.fetchone()[0]
        accel_mnem.append((a,m))
    
    # loop through all the known IDs for accelerator/mnemonic pairs representing top level menu items
    for a,m in accel_mnem:
        # for a single ID, get the mnemonic text for all languages
        request = "select textstring from %%(table)s where xmlid=\"%s\"" % m
        result = run_sql_on_all_lang_tables(session, request)
        # result is a langtable:rows dictionary
        for item in result.items():
            table = item[0]
            rows = item[1]
            row = rows[0]
            field = row[0]
            # this is what the accelerator should be
            accelstr = "Alt+%s" % field
            request2 = """UPDATE %s SET textstring="%s", actualkeys="%s" WHERE xmlid="%s" """ % \
                (table, accelstr, accelstr, a)
            print request2
            session.execute_query(request2)
    
if __name__=="__main__": main()


