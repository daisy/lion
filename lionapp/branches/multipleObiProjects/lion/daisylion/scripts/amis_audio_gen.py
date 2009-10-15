from global_options_parser import *
from daisylion.db.liondb import LionDB

def main():
    """Generate the TTS prompts for AMIS.  Run on OS X; be configured to use the server DB."""
    
    usage = """usage: %prog [options] langid"""
    parser = GlobalOptionsParser(usage=usage)
    
    (options, args) = parser.parse_args()
    parser.check_args(1, args)
    
    session = LionDB(options.config, options.trace, "amis")
    langid = args[0]
    dir = "/tmp/%s/" % langid
    session.generate_audio(langid, dir)
    
    print "your audio files are in " + dir

if __name__=="__main__": main()


