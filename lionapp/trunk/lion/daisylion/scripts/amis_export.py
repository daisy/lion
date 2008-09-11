from global_options_parser import *
from daisylion.db.liondb import LionDB

def main():
    export_choices = {1: "Output an AMIS Accessible UI XML file.",
        2: "Output a Microsoft resource file (RC) for use with an AMIS language pack.",
        3: "Export a DAISY book of keyboard shortcuts and save it in OUTPUT_DIR."}
    export_description = '\n'.join(["%d: %s" % (a, b) for a, b in export_choices.items()])
    
    usage = """usage: %prog [options] langid"""
    parser = GlobalOptionsParser(usage=usage)
    parser.add_option("-e", "--export_type", dest="export_type", type="int", default=1, 
        help=export_description)
    parser.add_option("-o", "--output_dir", default="/tmp", dest="output_dir",
        help="The output folder required by some export options")
    
    (options, args) = parser.parse_args()
    parser.check_args(1, args)
    
    session = LionDB(options.config, options.trace, options.force, "amis")
    langid = args[0]
    session.module_export(langid, options.export_type, options.output_dir)

if __name__=="__main__": main()


