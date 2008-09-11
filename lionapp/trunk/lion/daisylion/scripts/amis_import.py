from global_options_parser import *
from daisylion.db.liondb import LionDB

def main():
    import_choices = {1: "Rebuild a language table from an AMIS Accessible UI XML file.",
        2: "Update existing data from an AMIS Accessible UI XML file.",
        3: "Update only the audio data for existing table elements from an AMIS Accessible UI XML file."}
    
    import_description = '\n'.join(["%d: %s" % (a, b) for a, b in import_choices.items()])
    
    usage = """usage: %prog [options] langid"""
    parser = GlobalOptionsParser(usage=usage)
    parser.add_option("-e", "--import_type", dest="import_type", type="int", default=1, 
        help=import_description)
    (options, args) = parser.parse_args()
    parser.check_args(2, args)
    
    session = LionDB(options.config, options.trace, options.force, "amis")
    langid, file = args
    session.module_import(file, langid, options.import_type)

if __name__=="__main__": main()


