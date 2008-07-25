# this is a command line interface to the liondb utility
import os
import getopt
from liondb import *

def usage(code=0):
    """Print usage information and exits with an error code."""
    print """
Usage:

  %(script)s --help                              Show this help message.
  %(script)s --import --langid=id --file=file    Import file into table id.
  
  %(script)s --export --langid=id --file=file --export_type=1|2|3|etc --export_param=extra information    
                                                Export
  
  %(script)s --add_language --langid=id --langname=langname \
--username=username --password=password --email=email \
--realname=realname                              
                                                 Add a new language
  %(script)s --remove_language --langid=id       Remove a language
  %(script)s --add_string --langid=id --text=string --stringid=id 
                                                 Add a string to all tables
  %(script)s --remove_string --langid=id --stringid=id
                                                 Remove an item from all tables
  %(script)s --add_accelerator --langid=id --text=string --stringid=id
--refid=id --keys=accelerator                    Add an accelerator to all tables
  %(script)s --textstrings --langid=id               Output XML of strings, not including keyboard shortcuts
  %(script)s --all_strings --langid=id           Output XML of strings, including keyboard shortcuts
  %(script)s --change_item --langid=id --text=string --stringid=id  
                                                Change an item in the master table and reflect the change elsewhere 
  
Other options:
  --application, -a: which application module to use (e.g. "amis" or "obi")
  --trace, -t: trace mode (send trace messages to stderr.)
  --force, -f: force execution without safe checks 

""" % {"script": os.sys.argv[0]}
    os.sys.exit(code)


def main():
    """Parse command line arguments and run."""
    app = "amis"
    trace = False
    action = lambda s, f, l: usage(1)
    file = None
    langid = None
    langname = None
    username = None
    password = None
    email = None
    realname = None
    force = False
    textstring = None
    stringid = None
    refid = None
    actualkeys = None
    export_extra_param = None
    export_type = None
    # if the action is add/remove a language/string/accelerator, the parameters are different
    add_language = False  
    add_string = False
    remove_item = False
    add_accel = False
    change_item = False
    export = False
    
    try:
        opts, args = getopt.getopt(os.sys.argv[1:], "a:ef:hil:e",
            ["application=", "export", "file=", "help", "import", "langid=",
                "trace", "add_language", "remove_language", "langname=", 
                "username=", "password=", "realname=", "email=", "force", 
                "stringid=", "text=", "remove_item", "add_string", "refid=", 
                "keys=", "add_accelerator", "textstrings", "all_strings", 
                "audio_prompts", "change_item", "export_param=", "export_type="])
    except getopt.GetoptError, e:
        os.sys.stderr.write("Error: %s" % e.msg)
        usage(1)
    for opt, arg in opts:
        if opt in ("-a", "--application"): app = arg
        elif opt in ("--langname"): langname = arg
        elif opt in ("--username"): username = arg
        elif opt in ("--password"): password = arg
        elif opt in ("--realname"): realname = arg
        elif opt in ("--email"): email = arg
        elif opt in ("--force"): force = True
        elif opt in ("--stringid"): stringid = arg
        elif opt in ("--text"): textstring = arg
        elif opt in ("-f", "--file"): file = arg
        elif opt in ("-l", "--langid"): langid = arg
        elif opt in ("--trace"): trace = True
        elif opt in ("--refid"): refid = arg
        elif opt in ("--keys"): actualkeys = arg
        elif opt in ("--export_param"): output_folder = arg
        elif opt in ("-e", "--export"): export = True
        elif opt in ("-h", "--help"):
            action = lambda s, f, l: usage()
        elif opt in ("-i", "--import"):
            action = lambda s, f, l: s.import_xml(f, l)
        elif opt in ("--add_language"): add_language = True
        elif opt in ("--remove_language"):
            action = lambda s, f, l: s.remove_language(l)
        elif opt in ("--remove_item"): remove_item = True
        elif opt in ("--add_string"): add_string = True
        elif opt in ("--add_accelerator"): add_accel = True
        elif opt in ("--change_item"): change_item = True
        elif opt in ("--textstrings"):
            action = lambda s, f, l: s.textstrings(l)
        elif opt in ("--all_strings"):
            action = lambda s, f, l: s.all_strings(l)
        elif opt in ("--audio_prompts"):
            action = lambda s, f, l: s.audio_prompts(l, f)
    
    session = LionDB(trace, force, app)
    if add_language == True:
        session.add_language(langid, langname, username, password, realname, email)
    elif add_string == True:
        session.add_string(langid, textstring, stringid)
    elif remove_item == True:
        session.remove_item(langid, stringid)
    elif add_accel == True:
        session.add_accelerator(langid, textstring, stringid, refid, actualkeys)
    elif change_item == True:
        session.change_item(langid, textstring, stringid)
    elif export == True:
        session.export(file, langid, export_type)
    else:
        action(session, file, langid)

if __name__ == "__main__": main()
