from xml.dom import minidom
import re

class ObiImport():

    def __init__(self, session):
        self.doc = None
        self.session = session

    def import_resx(self, files, langid):
        """Import strings from a list of .resx files."""
        table = self.session.make_table_name(langid)
        self.session.execute_query("DELETE FROM %s" % table)
        for file in files:
            self.session.trace_msg("import_resx %s %s" % (file, langid))
            doc = minidom.parse(file)
            for data in doc.getElementsByTagName("data"):
                try:
                    xmlid = data.attributes["name"].nodeValue
                    if not re.search('\.', xmlid) or \
                        re.search('\.Text$', xmlid):
                        self.session.trace_msg("OK for <%s>" % xmlid)
                        self.__import(table, data, file + ":" + xmlid)
                    else:
                        self.session.trace_msg("NOK for <%s>" % xmlid)
                except:
                    # TODO display position of this element in the source file
                    # for this message to be actually useful
                    self.session.warn("Skipping element %s" % data)
        self.session.trace_msg("done: import_resx")

    def __import(self, table, data, xmlid):
        """Import <data> element with the given xmlid."""
        text = data.getElementsByTagName("value")[0]
        text.normalize()
        text = text.hasChildNodes() and text.firstChild.data or ""
        self.session.trace_msg("Adding message <%s>" \
            % re.sub("""(['"])""", r"\\\1", text))
        self.session.execute_query("""INSERT INTO %s
            (textstring, xmlid, textflag, role, mnemonicgroup)
            VALUES ("%s", "%s", 3, "STRING", 0)""" %
            (table, re.sub("""(['"])""", r"\\\1", text), xmlid))

    def update_from_resx(self, path, langid):
        self.session.trace_msg("Update from resx file %s" % path)
