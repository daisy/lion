"""Get the strings to translate from a list of .resx files"""

from global_options_parser import *
from xml.dom import minidom
import re, os.path

def main():
    parser = GlobalOptionsParser(usage="%prog [options] files...")
    (options, args) = parser.parse_args()
    strings = {}
    prefix = os.path.commonprefix(args)
    for file in args:
        new_strings = get_strings(file)
        file_stem = re.sub("\\.resx$", "", file)
        file_stem = re.sub("^%s" % prefix, "", file_stem)
        for role in new_strings.keys():
            if not strings.has_key(role): strings[role] = {}
            for id, text in new_strings[role].iteritems():
                if not strings[role].has_key(id): strings[role][id] = {}
                strings[role][id][file_stem] = text
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

def get_strings(file):
    """Get all strings for a file: go through data elements that are named
    with no . (e.g. strings in messages.resx) or that are named .Text or
    .AccessibleSomething. The id is the name of that element (which will also
    be qualified by the file where it came from). The text is the content of
    the first text child element."""
    strings = {"STRING":{}, "MNEMONIC":{}, "ACCELERATORS":{}}
    doc = minidom.parse(file)
    for data in doc.getElementsByTagName("data"):
        try:
            xmlid = data.attributes["name"].nodeValue
            text = data.getElementsByTagName("value")[0]
            text.normalize
            text = text.hasChildNodes() and text.firstChild.data or ""
            re.sub("""(['"])""", r"\\\\1", text)
            if not re.search('\.', xmlid) or \
                re.search('\.Accessible\w+$', xmlid):
                strings["STRING"][xmlid] = text
            elif re.search('\.ShortcutKeys$', xmlid):
                strings["ACCELERATORS"][xmlid] = text
            elif re.search('\.Text$', xmlid):
                m = re.match(".*&(.)", text)
                if m:
                    strings["MNEMONIC"][xmlid] = m.groups()[0]
                    strings["STRING"][xmlid] = re.sub("\s*\(&.\)|&", "", text)
                else:
                    strings["STRING"][xmlid] = text
        except:
            print "  ?! something went wrong :("
    return strings

if __name__=="__main__": main()
