from global_options_parser import *
from daisylion.db.liondb import LionDB

def main():
    usage = """usage: %prog [options] langid ncxFile"""
    parser = GlobalOptionsParser(usage=usage)
    parser.add_option("-s", "--simulate", dest="simulate", 
        help="Simulate the import without saving any data", action="store_true", default=False)
    (options, args) = parser.parse_args()
    
    parser.check_args(2, args)
    
    session = LionDB(options.config, options.trace, options.app)    
    langid, ncx_file = args
    warnings = session.import_audio_prompts(langid, ncx_file, False, options.simulate)
    if (parser.force == False and len(warnings) > 0):
        a = raw_input("\nYou have %d warnings.  Review? (y)es/(n)o/(a)ccept all/(r)eject all)" % len(warnings))
        automatically_accept = False
        if a == "n" or a=="r": 
            return
        elif a == "a":
            automatically_accept = True
        
        for w in warnings:
            xmlid, audio, db_text, xml_text = w
            if automatically_accept == False:
                print ("\nID=%s, DB text is:\n%s\nNCX text is:\n%s\naudio=%s" % \
                    (xmlid, db_text, xml_text, audio))
                ans = raw_input("(a)ccept or (r)eject?")
                if ans == "r": 
                    continue
                else:
                    write_audio(session, langid, xmlid, audio, options.simulate)
            else:
                write_audio(session, langid, xmlid, audio, options.simulate)

def write_audio(session, langid, xmlid, audio, simulate=False):
    request = """UPDATE %s SET audiouri="./audio/%s" WHERE xmlid="%s" """ % \
        (session.make_table_name(langid), xmlid, audio)
    if simulate == True:
        print "\n(Simulation)\n%s" % request
    else:
        session.execute_query(request)


if __name__=="__main__": main()
