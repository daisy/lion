import amis_import

#note that this is also defined for the web scripts
#we could share when the managedb stuff goes online instead of locally
XHTML_TEMPLATE = """Content-type: text/html; charset=utf-8

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
    session.execute_query("DELETE FROM %s" % langid)
    for elem in doc.getElementsByTagName("text"):
        data = amis_import.parse_text_element(session, elem)
        if data:
            textstring, audiouri, xmlid, textflag, audioflag = data
            keys = elem.parentNode.tagName == "accelerator" and \
                elem.parentNode.getAttribute("keys") or "NULL"
        session.execute_query(
"""INSERT INTO %(table)s (textstring, textflag, audioflag, audiouri, xmlid,
actualkeys) VALUES ("%(textstring)s", "%(textflag)s", "%(audioflag)s",
"%(audiouri)s", "%(xmlid)s", "%(keys)s")""" % \
        {"table": langid, "textstring": textstring, "textflag": textflag,
            "audioflag": audioflag, "audiouri": audiouri, "xmlid": xmlid,
            "keys": keys})
    amis_import.set_roles(doc, session, langid)
    amis_import.find_mnemonic_groups(session, langid)
    amis_import.find_accelerator_targets(session, langid)

def export_xhtml(session, langid):
    """return a string of xhtml generated from the database
       each text string will be an h1 with the xml id from the database.  
       the first heading will be the name of the language 
       E.g.:
       <h1 id="thislang">U.S. English</h1>
       <h1 id="t1">File...</h1>
       <h1 id="t2">F</h1>
       <h1 id="t3">Alt + F</h1>
       ...
    """
    thislang = session.check_language(langid)
    body = """<h1 id="thislang">%s</h1>""" % thislang
    table = langid.replace("-", "_")
    request = "SELECT xmlid, textstring from %s" % table
    session.execute_query(request)
    for id, txt in session.cursor:
        body += """<h1 id="%s">%s</h1>""" % (id, txt)
    return XHTML_TEMPLATE % {"TITLE": thislang, "BODY": body)
    
def export(session, file, langid):
    session.trace_msg("Export for %s to %s" % (langid, file))
      
    #export the XHTML list of all the text prompts
    xhtml_contents = export_xhtml(session, langid)
    filename = file + ".html"
    outfile = open(filename, 'w')
    outfile.write(xhtml_contents)
    outfile.close
