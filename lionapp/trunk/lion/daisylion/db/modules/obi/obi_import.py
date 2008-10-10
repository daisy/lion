from xml.dom import minidom
import re, os.path

def get_all_strings(files):
    """Get all strings to be imported for a set of .resx files. Strings are
    organized by role, then id, then file."""
    strings = {}
    prefix = os.path.commonprefix(files)
    for file in files:
        # The new strings are organized by role, then by ids.
        new_strings = get_strings(file)
        # Use the base name of the file (remove common directory prefix and
        # extension) as a part of the id of strings, since many may share the
        # same name (like label1.Text for instance.)
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
            # The id is derived from the name attribute
            xmlid = data.attributes["name"].nodeValue
            # Get the text content (if empty, there is no text node child so
            # be careful) and escape quotes so that the SQL statement remains
            # valid. The call to normalize() consolidates all text nodes into
            # a single one.
            text = data.getElementsByTagName("value")[0]
            text.normalize()
            text = text.hasChildNodes() and text.firstChild.data or ""
            text = re.sub("""(['"])""", r"\\\1", text)
            if not re.search('\.', xmlid) or \
                re.search('\.Accessible\w+$', xmlid):
                # Accessible labels and names are treated as regular strings
                strings["STRING"][xmlid] = text
            elif re.search('\.ShortcutKeys$', xmlid):
                strings["ACCELERATOR"][xmlid] = text
            elif re.search('\.Text$', xmlid):
                # Text labels may have a mnemonic, so take it out of the string
                # to translate and add it as a mnemonic.
                m = re.match(".*&(.)", text)
                if m:
                    strings["MNEMONIC"][xmlid] = m.groups()[0]
                    # Mnemonics can look like "&Open" or "Open (&q)"
                    strings["STRING"][xmlid] = re.sub("\s*\(&.\)|&", "", text)
                else:
                    strings["STRING"][xmlid] = text
        except:
            pass
    return strings


class ObiImport():

    def __init__(self, session):
        """Creat a new import object for a session."""
        self.session = session

    def import_resx(self, files, langid):
        """Import strings from a list of .resx files."""
        strings = get_all_strings(files)
        table = self.session.make_table_name(langid)
        self.session.execute_query("DELETE FROM %s" % table)
        for role in strings.keys():
            prefix = role[0]
            queries = {}
            for id, pairs in strings[role].iteritems():
                l = len(pairs.keys())
                if l == 1:
                    # Only one string with this name/id so it is prefixed with
                    # its role and its file name
                    xmlid, q = self.__add_query(table, id, pairs.keys()[0],
                        pairs.values()[0], role)
                    queries[xmlid] = q
                elif l > 1:
                    # Several pairs; this can be either common labels like
                    # mOKButton.Text (which should all have the same value)
                    # or just a common name like label1.Text where the value
                    # is different for all occurrences.
                    values = pairs.values()
                    if reduce(lambda x, y: x and y == values[0], values, True):
                        # All values are the same, so drop the filename from
                        # the id (keep the role as a prefix)
                        xmlid, q = self.__add_query(table, id, "", values[0],
                            role)
                        queries[xmlid] = q
                    else:
                        # Values are different so output them all
                        for stem, text in pairs.iteritems():
                            xmlid, q = self.__add_query(table, id, stem, text,
                                role)
                            queries[xmlid] = q
            # Execute queries in the order of the xmlids (hopefully this order
            # will make sense to users)
            for xmlid in sorted(queries.keys()):
                self.session.execute_query(queries[xmlid])
        self.session.trace_msg("done: import_resx")

    def update_from_resx(self, path, langid):
        """Update strings from a .resx file: replace those that have a
        different value; remove old strings that are not in the new import and
        add new ones."""


    def __add_query(self, table, id, file, textstring, role, status=3):
        """Creat a query to add a string in the DB. Return the xmlid that is
        being build for this string as well as the query to be executed
        later."""
        prefix = role[0]
        xmlid = "%s:%s:%s" % (prefix, file, id)
        return xmlid, """INSERT INTO %s
            (xmlid, textstring, role, status, mnemonicgroup)
            VALUES ("%s", "%s", "%s", %d, 0)""" \
            % (table, xmlid, textstring, role, status)
