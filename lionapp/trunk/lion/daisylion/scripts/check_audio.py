from global_options_parser import *
from daisylion.db.liondb import LionDB

def main():
    usage = """usage: %prog [options] langid audio_dir
    see if all required audio files are there audio_dir is the current audio directory.  
    e.g. 
    %prog eng-US ./audio/
    
    """
    parser = GlobalOptionsParser(usage=usage)
    parser.add_option("-s", "--svn", dest="svn",
        help="commit the changes to SVN", action="store_true", default=False)
    (options, args) = parser.parse_args()
    parser.check_args(2, args)
    
    session = LionDB(options.config, options.trace, options.app)    
    langid, audio_dir = args
    if not audio_dir.endswith("/"): audio_dir += "/"
    session.check_audio(langid, audio_dir)

if __name__=="__main__": main()


