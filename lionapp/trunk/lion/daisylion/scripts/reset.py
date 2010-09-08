from global_options_parser import *
from daisylion.db.liondb import LionDB

def main():
    usage = """usage: %prog langid [options]"""
    parser = GlobalOptionsParser(usage=usage)
    parser.add_option("-k", "--keyboard", dest="keyboard", 
        help="Reset keyboard accelerators", action="store_true", default=False)
    parser.add_option("-m", "--mnemonic", dest="mnemonic",
        help="Reset mnemonics", action="store_true", default=False)
    parser.add_option("-s", "--strings", dest="strings",
        help="Reset strings", action="store_true", default=False)
	
    (options, args) = parser.parse_args()
    parser.check_args(1, args)
    
    session = LionDB(options.config, options.trace, options.app)    
    mastertable = session.get_masterlang_table()
    lang = args[0]
    
    # ACCELERATOR, MNEMONIC, STRING, MENUITEM, DIALOG, CONTROL
    if options.keyboard == True:
        session.reset_items_by_role(lang, "ACCELERATOR")
    if options.mnemonic == True:
        session.reset_items_by_role(lang, "MNEMONIC")
    if options.strings == True:
        session.reset_items_by_role(lang, "DIALOG")
        session.reset_items_by_role(lang, "CONTROL")
        session.reset_items_by_role(lang, "STRING")
        session.reset_items_by_role(lang, "MENUITEM")
    if options.keyboard == False and options.mnemonic == False and options.strings == False:
        print "Please specify one or more options [-k | -m | -s]"

if __name__=="__main__": main()


