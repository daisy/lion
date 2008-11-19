"""Get the strings to translate from a list of .resx files"""

from global_options_parser import *
from daisylion.db.modules.obi_import import ObiImport

def main():
    parser = GlobalOptionsParser(usage="%prog [options] files...")
    (options, args) = parser.parse_args()
    importer = ObiImport()
    show_strings(strings)

def show_strings(strings):
    """Show strings found with their full id/text value."""
    for role in strings.keys():
        prefix = role[0]
        for id, pairs in strings[role].iteritems():
            l = len(pairs.keys())
            if l == 1:
                print '%s:%s:%s="%s"' \
                    % (prefix, pairs.keys()[0], id, pairs.values()[0])
            elif l > 1:
                values = pairs.values()
                if reduce(lambda x, y: x and y == values[0], values, True):
                    print '%s::%s="%s"' % (prefix, id, values[0])
                else:
                    for stem, text in pairs.iteritems():
                        print '%s:%s:%s="%s"' % (prefix, stem, id, text)

if __name__=="__main__": main()
