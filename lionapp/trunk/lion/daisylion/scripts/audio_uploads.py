#audio [accept|clear] langid --stringid

from global_options_parser import *
from daisylion.db.liondb import LionDB

def main():
    usage = """usage: %prog [options] langid [accept | clear]
    Accept or clear audio uploads for a given language.
    If no string ID is specified, the action applies to all.
    """
    parser = GlobalOptionsParser(usage=usage)
    parser.add_option("-r", "--stringid", dest="stringid",
        help="The string ID associated with the audio clip")
    (options, args) = parser.parse_args()
    parser.check_args(2, args)
    
    session = LionDB(options.config, options.trace, options.app)    
    langid, action = args
    
    # warn the user before they blow away all their files
    do_action = True
    if options.stringid == None:
        warning = "%s ALL temporary audio files for %s? (y/n)" % (action, langid)
        do_action = parser.safety_check(warning)
    
    if do_action == True:
        if action == "accept":
            if options.stringid == None:
                session.accept_all_temp_audio(langid)
            else:
                session.accept_temp_audio(langid, options.stringid)
        elif action == "clear":
            if options.stringid == None:
                session.clear_all_temp_audio(langid)
            else:
                session.clear_temp_audio(langid, options.stringid)        
        else:
            parser.error("""Must specify "accept" or "clear" """)
    
    else:
        print "Action cancelled."
        os.sys.exit(0)

    
if __name__=="__main__": main()
