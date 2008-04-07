from xml.dom import Node

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
    """Import a document object (from minidom) into a table. The cursor has the
current connection to the database."""
    session.trace_msg("IMPORT FROM AMIS.")
    session.execute_query("DELETE FROM %s" % langid)
    for elem in doc.getElementsByTagName("text"):
        data = parse_text_element(session, elem)
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
    #set_roles(doc, session, langid)
    #find_mnemonic_groups(session, langid)
    #find_accelerator_targets(session, langid)

def parse_text_element(session, elem):
    """A text element that appears in the following context:
    <parent>
        <text>CDATA</text>
        <audio src="path"/>
    </parent>

Return None in case of error, otherwise a tuple: (textstring, audiosrc, xmlid,
textflag, audioflag)"""
    if not elem.firstChild or \
        elem.firstChild.nodeType != Node.TEXT_NODE or \
        not elem.parentNode:
            return None
    text = quote(elem.firstChild.wholeText)
    id = elem.getAttribute("id")
    if id == "":
        session.warn('No id for text element with text = "%s"' % text)
    audio = get_first_child_with_tagname(elem.parentNode, "audio")
    if not audio: return None
    src = audio.getAttribute("src")
    if src == "":
        session.warn('No src for for audio element near text with id "%s"' % id)
    textflag = elem.getAttribute("flag") == "new" and 3 or 1
    audioflag = audio.getAttribute("flag") == "new" and 3 or 1
    return text, src, id, textflag, audioflag

def quote(str):
    """Escape double quotes inside a double-quoted string."""
    return str.replace("\"", "\\\"")

def get_first_child_with_tagname(elem, tagname):
    """Get first child of elem with tagname tag name."""
    for c in elem.childNodes:
        if c.nodeType == Node.ELEMENT_NODE and c.tagName == tagname:
            return c
    return None

def get_element_by_id(doc, tagname, id):
    """Workaround the absence of DTD."""
    for t in doc.getElementsByTagName(tagname):
        if t.getAttribute("id") == id:
            return t

def set_roles(doc, session, langid):
    session.execute_query("SELECT id, xmlid, textstring FROM %s" % langid)
    for id, xmlid, textstring in session.cursor:
        elem = get_element_by_id(doc, "text", xmlid)
        if elem:
            tag = elem.parentNode.tagName
            if tag == "accelerator": role = "ACCELERATOR"
            elif tag == "mnemonic": role = "MNEMONIC"
            elif tag == "caption":
                tag = elem.parentNode.tagName
                if tag == "action" or tag == "container": role = "MENUITEM"
                elif tag == "control": role = "CONTROL"
                elif tag == "dialog": role = "DIALOG"
                else: role = "STRING"
            else: role = "STRING"
            session.execute_query("""UPDATE %s SET role="%s" WHERE id=%s""" % \
                (langid, role, id))

def find_mnemonic_groups(session, langid):
    """Identify groups for the mnemonics based on menu and dialog control
groupings."""
    groupid = 0
    # Container elements
    for elem in doc.getElementsByTagName("container") + \
        doc.getElementsByTagName("containers"):
        #items = get_items_in_container(elem)
        #get_mnemonics_and_write_data(langid, items, groupid)
        groupid += 1
    # Dialog elements
    for e in doc.getElementsByTagName("dialog"):
        #items = get_items_in_dialog(e)
        #get_mnemonics_and_write_data(langid, items, groupid)
        groupid += 1

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
