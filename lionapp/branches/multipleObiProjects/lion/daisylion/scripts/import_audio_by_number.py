from global_options_parser import *
from daisylion.db.liondb import LionDB

def main():
    usage = """usage: %prog [options] langid audioDir"""
    parser = GlobalOptionsParser(usage=usage)
    (options, args) = parser.parse_args()
    parser.check_args(2, args)
    
    session = LionDB(options.config, options.trace, options.app)    
    langid, audio_dir = args
    session.import_audio_by_number(langid, audio_dir)

if __name__=="__main__": main()
