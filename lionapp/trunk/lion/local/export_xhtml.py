from managedb import DBSession

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

def export_xhtml(session, langid):
    """export xhtml from the database
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
    print XHTML_TEMPLATE % (thislang, body)    

           
    
    
    