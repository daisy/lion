from global_options_parser import *
from daisylion.db.liondb import LionDB

def main():
    usage = """usage: %prog [options] langid output_dir local_audio_dir"""
    parser = GlobalOptionsParser(usage=usage)
    parser.add_option("-v", "--amisversion", dest="amis_version", default="3.1", 
        help="Target version of AMIS (default = 3.1)")
    
    (options, args) = parser.parse_args()
    parser.check_args(3, args)
    
    session = LionDB(options.config, options.trace, "amis")
    langid = args[0]
    outputdir = args[1]
    local_audio_dir = args[2]
    session.module_export(langid, 3, (options.amis_version, outputdir, local_audio_dir))

if __name__=="__main__": main()


