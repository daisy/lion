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
        file_stem = re.sub("(\\.\\w+)?\\.resx$", "", file)
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
    # We add a fake REMARKS field to store remarks; they will be integrated
    # back into the table after the strings have been added.
    strings = {"STRING":{}, "MNEMONIC":{}, "ACCELERATOR":{}, "REMARKS":{}}
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
            # Get comments as well
            comments = data.getElementsByTagName("comment")
            if len(comments) > 0:
                comments[0].normalize()
                if comments[0].hasChildNodes():
                    strings["REMARKS"][xmlid] = re.sub("""(["'])""", r"\\\1",
                        comments[0].firstChild.data)
        except:
            pass
    return strings

def get_strings_by_xmlid(files):
    """Get all strings indexed by their xmlid for easy sorting and retrieval."""
    strings = get_all_strings(files)
    xmlids = {}
    for role in strings.keys():
        suffix = role[0]
        for id, pairs in strings[role].iteritems():
            l = len(pairs.keys())
            if l == 1:
                # Only one string with this name/id so it is prefixed with
                # its role and its file name
                xmlids[get_xmlid(pairs.keys()[0], id, suffix)] = \
                    pairs.values()[0]
            elif l > 1:
                # Several pairs; this can be either common labels like
                # mOKButton.Text (which should all have the same value)
                # or just a common name like label1.Text where the value
                # is different for all occurrences.
                values = pairs.values()
                if reduce(lambda x, y: x and y == values[0], values, True):
                    # All values are the same, so list all files that
                    # contain it for the id separated by ;
                    files = sorted(pairs.keys())
                    filestr = reduce(lambda x, y: "%s;%s" % (x, y), files,
                        files.pop(0))
                    xmlids[get_xmlid(filestr, id, suffix)] = values[0]
                else:
                    # Values are different so output them all
                    for stem, text in pairs.iteritems():
                        xmlids[get_xmlid(stem, id, suffix)] = text
    return xmlids

def get_xmlid(file, id, suffix):
    """Create an xmlid id from the name, file stem list and role suffix."""
    return "%s:%s:%s" % (file, id, suffix)

def get_role_from_xmlid(xmlid):
    """Get back the role from the xmlid suffix."""
    suffix = xmlid[-1]
    return suffix == "S" and "STRING" or suffix == "M" and "MNEMONIC" \
        or suffix == "A" and "ACCELERATOR" or suffix == "R" and "REMARKS"


class ObiImport():

    def __init__(self, session):
        """Creat a new import object for a session."""
        self.session = session


    def import_resx(self, files, langid):
        """Import strings from a list of .resx files."""
        xmlids = get_strings_by_xmlid(files)
        table = self.session.make_table_name(langid)
        self.session.execute_query("DELETE FROM %s" % table)
        remarks = []
        for xmlid in sorted(xmlids.keys()):
            role = get_role_from_xmlid(xmlid)
            if role == "REMARKS":
                # We'll handle remarks later
                remarks.append(xmlid)
            else:
                self.session.execute_query("""INSERT INTO %s
                    (xmlid, textstring, role, status, mnemonicgroup)
                    VALUES ("%s", "%s", "%s", 3, 0)""" \
                    % (table, xmlid, xmlids[xmlid], role))
        for xmlid in remarks:
            x = re.sub("R$", "S", xmlid)
            if xmlids.has_key(x):
                self.session.execute_query("""UPDATE %s
                    SET remarks="%s" WHERE xmlid="%s" """ \
                    % (table, xmlids[xmlid], x))
            else:
                self.session.warn("Couldn't match remark for %s" % xmlid)

    def populate_from_resx(self, files, langid):
        """Populate strings for a slave language from a list of .resx files.
        The language table must already exist; replace strings that exist in
        the database with values from the .resx files and skip those that
        don't exist in the database."""
        if self.session.check_language(langid) == False:
            self.session.die("Language %s does not exist" % langid, 1)
        table = self.session.make_table_name(langid)
        strings = get_strings_by_xmlid(files)    
        for id in strings.keys():
            request = """UPDATE %s SET textstring="%s", status=1 WHERE xmlid="%s" """ % \
                (table, strings[id], id)
            self.session.execute_query(request)
    
    def update_from_resx(self, files, langid):
        """Update strings from a list of .resx files: replace those that have a
        different value; remove old strings that are not in the new import and
        add new ones."""
        self.session.die("Update is not implemented yet", 1)
