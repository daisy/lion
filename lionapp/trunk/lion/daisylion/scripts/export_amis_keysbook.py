from global_options_parser import *
from daisylion.db.liondb import LionDB

def main():
    usage = """usage: %prog [options] langid output_dir local_audio_dir"""
    parser = GlobalOptionsParser(usage=usage)
    
    (options, args) = parser.parse_args()
    parser.check_args(3, args)
    
    session = LionDB(options.config, options.trace, "amis")
    langid = args[0]
    outputdir = args[1]
    local_audio_dir = args[2]
    session.module_export(langid, 3, (outputdir, local_audio_dir))

if __name__=="__main__": main()


