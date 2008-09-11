from global_options_parser import *
from daisylion.db.liondb import LionDB

def main():
    usage = """usage: %prog [options] langid ncxFile"""
    parser = GlobalOptionsParser(usage=usage)
    (options, args) = parser.parse_args()
    parser.check_args(2, args)
    
    session = LionDB(options.config, options.trace, options.force, options.app)
    langid, ncx_file = args
    session.import_audio_prompts(langid, ncx_file)

if __name__=="__main__": main()
