import amis_import
import amis_export
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

def import_from_xml(session, doc, langid):
    """Import a document object (from minidom) into a table."""
    session.trace_msg("IMPORT FROM AMIS.")
    table = session.make_table_name(langid)
    
    # clear the table
    session.execute_query("DELETE FROM %s" % table)
    
    # add all the text item data to the table
    for elem in doc.getElementsByTagName("text"):
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
    amis_import.set_roles(doc, session, table)
    amis_import.find_mnemonic_groups(doc, session, table)
    amis_import.find_accelerator_targets(doc, session, table)

def get_removed_ids(doc):
    """Items that have been removed are specified in the document root's 
    "removed" attribute"""
    return amis_import.process_removals(doc)
    
def export_xml(session, file, langid):
    session.trace_msg("XML Export for %s to %s" % (langid, file))
    return amis_export.export_xml(session, file, langid)

def export_rc(session, langid):
    session.trace_msg("RC Export for %s" % (langid))
    return amis_export.export_rc(session, langid)

def export_keys_book(session, file, langid):
    session.trace_msg ("Keyboard shortcuts book export for %s" % (langid))
    return amis_export.export_keys_book(session, file, langid)

