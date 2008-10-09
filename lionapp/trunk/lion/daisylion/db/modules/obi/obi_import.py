from xml.dom import minidom
import re, os.path

def get_all_strings(files):
    """Get all strings to be imported for a set of .resx files."""
    strings = {}
    prefix = os.path.commonprefix(files)
    for file in files:
        new_strings = get_strings(file)
        file_stem = re.sub("\\.resx$", "", file)
        file_stem = re.sub("^%s" % prefix, "", file_stem)
        for role in new_strings.keys():
            if not strings.has_key(role): strings[role] = {}
            for id, text in new_strings[role].iteritems():
                if not strings[role].has_key(id): strings[role][id] = {}
                strings[role][id][file_stem] = text
    return strings

def get_strings(file):
    """Get all strings for a file: go through data elements that are named
    with no . (e.g. strings in messages.resx) or that are named .Text or
    .AccessibleSomething. The id is the name of that element (which will also
    be qualified by the file where it came from). The text is the content of
    the first text child element."""
    strings = {"STRING":{}, "MNEMONIC":{}, "ACCELERATOR":{}}
    doc = minidom.parse(file)
    for data in doc.getElementsByTagName("data"):
        try:
            xmlid = data.attributes["name"].nodeValue
            text = data.getElementsByTagName("value")[0]
            text.normalize
            text = text.hasChildNodes() and text.firstChild.data or ""
            text = re.sub("""(['"])""", r"\\1", text)
            if not re.search('\.', xmlid) or \
                re.search('\.Accessible\w+$', xmlid):
                strings["STRING"][xmlid] = text
            elif re.search('\.ShortcutKeys$', xmlid):
                strings["ACCELERATOR"][xmlid] = text
            elif re.search('\.Text$', xmlid):
                m = re.match(".*&(.)", text)
                if m:
                    strings["MNEMONIC"][xmlid] = m.groups()[0]
                    strings["STRING"][xmlid] = re.sub("\s*\(&.\)|&", "", text)
                else:
                    strings["STRING"][xmlid] = text
        except:
            pass
    return strings


class ObiImport():

    def __init__(self, session):
        self.session = session

    def import_resx(self, files, langid):
        """Import strings from a list of .resx files."""
        strings = get_all_strings(files)
        table = self.session.make_table_name(langid)
        self.session.execute_query("DELETE FROM %s" % table)
        for role in strings.keys():
            prefix = role[0]
            for id, pairs in strings[role].iteritems():
                l = len(pairs.keys())
                if l == 1:
                    xmlid = "%s:%s:%s" % (prefix, pairs.keys()[0], id)
                    self.session.execute_query("""INSERT INTO %s
                        (textstring, xmlid, status, role, mnemonicgroup)
                        VALUES ("%s", "%s", 3, "%s", 0)""" \
                        %(table, pairs.values()[0], xmlid, role))
                elif l > 1:
                    values = pairs.values()
                    if reduce(lambda x, y: x and y == values[0], values, True):
                        xmlid = "%s::%s" % (prefix, id)
                        self.session.execute_query("""INSERT INTO %s
                            (textstring, xmlid, status, role, mnemonicgroup)
                            VALUES ("%s", "%s", 3, "%s", 0)""" \
                            %(table, values[0], xmlid, role))
                    else:
                        for stem, text in pairs.iteritems():
                            xmlid = "%s:%s:%s" % (prefix, stem, id)
                            self.session.execute_query("""INSERT INTO %s
                                (textstring, xmlid, status, role, mnemonicgroup)
                                VALUES ("%s", "%s", 3, "%s", 0)""" \
                                %(table, text, xmlid, role))
        self.session.trace_msg("done: import_resx")

    def update_from_resx(self, path, langid):
        self.session.trace_msg("Update from resx file %s" % path)
