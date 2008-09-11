from global_options_parser import *
from daisylion.db.liondb import LionDB

def main():
    usage = """usage: %prog [options] langid stringid string refid keys
    string: the human-readable name for the accelerator shortcut
    refid: the id of the string label for the command referenced by the accelerator
    keys: the actual keys used to access the accelerator shortcut
    
    e.g. 
    %prog eng-US t123 Escape t345 esc
    
    """
    parser = GlobalOptionsParser(usage=usage)
    session = LionDB(parser.options.config, parser.options.trace, parser.options.force)
    langid, string, stringid, refid, keys = parser.args
    session.add_accelerator(langid, string, stringid, refid, keys)

if __name__=="__main__": main()


