from global_options_parser import *
from daisylion.db.liondb import LionDB

def main():
    usage = """usage: %prog [options] langid username password"""
    parser = GlobalOptionsParser(usage=usage)
    parser.add_option("-l", "--langname", dest="langname", default="",
        help="The human-readable name of the language")
    parser.add_option("-r", "--realname", dest="realname", default="",
        help="The full name of the user")
    parser.add_option("-e", "--email", dest="email", default="",
        help="The user's email address")
    parser.add_option("-m", "--mnemonics", dest="mnemonics", default=None,
        help="Set the translate_mnemonics flag for this language.")
    parser.add_option("-x", "--accelerators", dest="accelerators", default=None,
        help="Set the translate_accelerators flag for this language.")
    parser.add_option("-s", "--short", dest="short", default=None,
        help="Short (two-letter) language identifier for .resx files.")
    (options, args) = parser.parse_args()
    parser.check_args(3, args)

    session = LionDB(options.config, options.trace, options.app)
    langid, username, pwd = args
    session.add_language(langid, options.langname, username, pwd,
        options.realname, options.email,
        options.mnemonics, options.accelerators, options.short)

if __name__=="__main__": main()


