import amis_import

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

    
def export_xhtml(session, langid):
    """return a string of xhtml generated from the database
       each text string will be an h1 with the xml id from the database.  
       E.g.:
       <h1 id="t1">File...</h1>
       <h1 id="t2">F</h1>
       <h1 id="t3">Alt + F</h1>
       ...
    """
    thislang = session.check_language(langid)
    if thislang == None:
        session.die("Language does not exist.")
    body = ""
    table = session.make_table_name(langid)
    request = "SELECT xmlid, textstring from %s" % table
    session.execute_query(request)
    for id, txt in session.cursor:
        body += """<h1 id="%s">%s</h1>""" % (id, txt)
    return XHTML_TEMPLATE % {"TITLE": thislang, "BODY": body}
    
def export(session, file, langid):
    session.trace_msg("Export for %s to %s" % (langid, file))
      
    #export the XHTML list of all the text prompts
    xhtml_contents = export_xhtml(session, langid)
    filename = file + ".html"
    outfile = open(filename, 'w')
    outfile.write(xhtml_contents)
    outfile.close

# add or remove a single string from the master table
def add_string(session, langid, string, stringid):
    """Add a new string to all tables
        langid = master table
        stringid = xmlid for the string
        This function is ONLY for adding anything with role=STRING"""

    # make sure the stringid doesn't already exist
    if session.check_string_id(langid, stringid) != None:
        session.die("String with ID %s already exists." % stringid)
        return False
    table = session.make_table_name(langid)
    
    # add the string to the master table
    session.execute_query("""INSERT INTO %(table)s (textstring, textflag, \
        audioflag, xmlid, role) VALUES ("%(textstring)s", 3, \
        3, "%(xmlid)s", "STRING")""" % \
        {"table": table, "textstring": string, "xmlid": stringid})
    session.warn("Remember to change the next-id value in the AMIS XML file.")
    return True

def remove_item(session, langid, stringid):
    """Remove a string from all the tables
        langid = master table
        stringid = xmlid for the string"""
    # make sure the stringid exists
    if session.check_string_id(langid, stringid) == None:
        session.die("String with ID %s does not exist." % stringid)
        return False
    
    # safety check
    can_remove = session.force
    if session.force == False:
        rly = raw_input("Do you REALLY want to remove a string?  This is serious.\n \
            Type your answer (definitely/no)  ")
        if rly == "definitely":
            can_remove = True
        else:
            can_remove = False
    
    table = session.make_table_name(langid)
    # really delete it!
    if can_remove == True:
        session.execute_query("""DELETE FROM %(table)s \
            WHERE xmlid="%(xmlid)s" """ % \
            {"table": table, "xmlid": stringid})
    
    return True

def add_accelerator(session, langid, stringid, refid, keys, keysname):
    """Add an accelerator to the master table
        refid = the item it refers to
        keysname = the human-readable or translated name of the keys
        keys = the actual keypress"""
    return True
