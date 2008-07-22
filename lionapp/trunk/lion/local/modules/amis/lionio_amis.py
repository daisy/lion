import amisxml
import amis_import
import amis_export
import os
os.sys.path.append("../")
import lion_module

#note that this is also defined for the web scripts
#we could share when the managedb stuff goes online instead of locally
XHTML_TEMPLATE = """
<?xml version="1.0"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xml:lang="en" lang="en" xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <title>%(TITLE)s</title>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
    <link href="http://amisproject.org/translate/l10n.css" rel="stylesheet" type="text/css"/>
  </head>
  <body>%(BODY)s</body>
</html>"""

class AmisLionIO (lion_module.LionIOModule):
    """The AMIS-specific implementation of lion_module.LionIOModule"""
    
    def import_from_xml(session, file, langid):
        """Import a document object (from minidom) into a table."""
        session.trace_msg("IMPORT FROM AMIS.")
        table = session.make_table_name(langid)
    
        # clear the table
        session.execute_query("DELETE FROM %s" % table)
        
        # use our implementation of minidom.Document instead
        xml.dom.minidom.Document = amisxml.AmisUiDoc
        self.doc = minidom.parse(file)
        
        # add all the text item data to the table
        for elem in self.doc.getElementsByTagName("text"):
            data = amis_import.parse_text_element(session, elem)
            if data:
                textstring, audiouri, xmlid, textflag, audioflag = data
                # keys = the actual keys associated with a command
                keys = elem.parentNode.tagName == "accelerator" and \
                    elem.parentNode.getAttribute("keys") or "NULL"
        
            session.execute_query(
            """INSERT INTO %(table)s (textstring, textflag, audioflag, audiouri, xmlid,
            actualkeys) VALUES ("%(textstring)s", "%(textflag)d", "%(audioflag)d",
            "%(audiouri)s", "%(xmlid)s", "%(keys)s")""" % \
            {"table": table, "textstring": textstring, "textflag": textflag,
                "audioflag": audioflag, "audiouri": audiouri, "xmlid": xmlid,
                "keys": keys})
    
        # specify relationships 
        amis_import.set_roles(self.doc, session, table)
        amis_import.find_mnemonic_groups(doc, session, table)
        amis_import.find_accelerator_targets(doc, session, table)

    def get_removed_ids_after_import(self):
        """Items that have been removed are specified in the document root's 
        "removed" attribute"""
        return amis_import.process_removals(self.doc)
    
    def export(self, session, file, langid, export_type):
        if export_type == 1:
            return amis_export.export_xml(session, file, langid)
        elif export_type == 2:
            return amis_export.export_rc(session, langid)
        elif export_type == 3:
            return amis_export.export_keys_book(session, xmlfile, langid)
        
