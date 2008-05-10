#this file will probably be replaced by a nicer templating system

#need to supply the table name
TEXTFLAGS_SQL = {"new": "and %(table)s.textflag=3", 
                "todo": "and %(table)s.textflag=2", 
                "newtodo": "and (%(table)s.textflag=2 or \
                    %(table)s.textflag=3)",
                "all": ""}
#need to supply the table name
ROLES_SQL = {"main": """ and (%(table)s.role="STRING" or \
                %(table)s.role="CONTROL" or %(table)s.role="DIALOG" or \
                %(table)s.role="MENUITEM") """,
            "mnemonics": """ and %(table)s.role="MNEMONIC" """, 
            "accelerators": """ and %(table)s.role="ACCELERATOR" """}
#the width and height of the text box that translators type into
TRANSLATE_BOX_SIZE = {"main": (64, 3), "mnemonics": (1, 1), "accelerators": (20,1)}

# generic XHTML
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

# Title format
TITLE_TEMPLATE = """AMIS translation for %(lang)s: %(section)s section"""

# Each page will use this body template (except error pages)
BODY_TEMPLATE_HTML = """
<h1>%(title)s</h1>
<div id="navigation">
    %(actions)s
</div>
<p class="description">%(about_section)s  There are %(num_items)d items on this page.</p>
<div>
    <form action="/cgi-bin/page.py" method="POST">
        <select name="viewfilter">
            <option value="all">all items</option>
            <option value="newtodo">all items marked new or to-do</option>
            <option value="new">all new items</option>
            <option value="todo">all to-do items</option>
        </select>
        <input type="submit" value="Change view" />
    </form>
</div>
<br/>
<p>%(message)s</p>
<div>%(specialform)s</div>
<div>%(warning)s</div>
<div>%(form)s</div>
"""

# login
LOGIN_FORM = """
<h1>Login</h1>
<form action="process_login" method="post">
  <p>
    <label>User name:</label>
    <input type="text" name="username" value=""/>
  </p>
  <p>
    <label>Password:</label>
    <input type="password" name="password" value=""/>
    <input type="submit" value="Submit" />
  </p>
</form>

"""

# A single row of the form used for all pages
FORM_ROW= """<form action="/cgi-bin/actions.py" method="POST">
<td width="30%%">%(ref_string)s</td>
<td>
    <p class="comments">%(our_remarks)s</p>
    %(instructions)s
    <textarea id="%(xmlid)s" name="translation" cols="%(translate_box_columns)d" rows="%(translate_box_rows)d">%(translation)s</textarea>
    <p class="comments">Remarks from you:</p>
	<textarea class="remarks" name="remarks" cols="64" rows="2">%(translator_remarks)s</textarea>
</td>
<td>
	<p>Status:</p>
	<input name="%(xmlid)s_status" type="radio" %(text_status_ok)s value="1"/>
	<span class="ok">OK</span><br/>
	
	<input name="%(xmlid)s_status" type="radio" %(text_status_todo)s value="2"/>
	<span class="todo">TODO</span><br/>
	
</td>
<td>
	<input type="submit" value="Save" style="align: bottom"/>
	<input type="hidden" name="xmlid" value="%(xmlid)s"/>
	<input type="hidden" name="langid" value="%(langid)s"/>
	<input type="hidden" name="pageid" value="%(pageid)s"/>
	<input type="hidden" name="dataprefix" value="%(dataprefix)s"/>
	<input type="hidden" name="action" value="save"/>
</td>
</form>
"""

ACTIONS = ("<a href=\"TranslateStrings?view=all\">Translate AMIS strings</a>",
    "Assign AMIS keyboard shortcuts",
    "Assign mnemonics (single-letter shortcuts)")

def separate(list):
    html = ""
    for string in list:
        html += string + " | "
    # chop off the end
    if len(html) > 3: return html[0: len(html)-3]
    else: return html

def listize(list):
    html = ""
    for string in list:
        html += "<li>" + string + "</li>"
    return html

def login_form():
    return XHTML_TEMPLATE % {"TITLE": "Login", "BODY": LOGIN_FORM}


def login_error():
    body = "<p>There was an error logging in.  Try again?</p>" + LOGIN_FORM
    return XHTML_TEMPLATE % {"TITLE": "Login error -- try again", "BODY": body}

def login_success():
    body = "<p>Login successful!  <a href=\"MainMenu\">Start working.</a></p>"
    return XHTML_TEMPLATE % {"TITLE": "Logged in", "BODY": body}

def general_error():
    body = "<h1>General error</h1><p>Dear user: Sorry!</p>"
    return XHTML_TEMPLATE % {"TITLE": "General error", "BODY": body}

def user_information(user):
     return "<p>Hello %(user)s. You are working on %(lang)s.</p>" % \
        {"user": user["users.realname"], "lang": user["languages.langname"]}

def main_menu_links(user):
    
    user_info = user_information(user)
    body = """
    <h1>Welcome!</h1>
    %(user_info)s
    <h1>Actions</h1>
    <ul>
    %(list)s
    </ul>
    """ % {"user_info": user_info, "list": listize(ACTIONS)}
    return XHTML_TEMPLATE % {"TITLE": "Main Menu", "BODY": body}

def make_single_table_row(row, langid, page_id, instructions, data_prefix):
    """Process a single row of data, which is in the form of:
    (xmlid, textstring, textflag, remarks, ref_string, our_remarks)"""
    xmlid, textstring, textflag, remarks, ref_string, our_remarks = row
    #otherwise it crashes
    if remarks == None: 
        remarks = ""
	if our_remarks == None: 
	    our_remarks = ""
	#get the values for the radio buttons
    if textflag == 1:
        textok = "checked"
        texttodo = ""
    elif textflag == 2:
        textok = ""
        texttodo = "checked"
    else: #textflag == 3
        textok = ""
        texttodo = ""
    one_table_row = FORM_ROW % \
    {"ref_string": ref_string, "our_remarks": our_remarks, 
        "xmlid": xmlid, "translation": textstring, 
        "translator_remarks": remarks, "text_status_ok": textok, 
        "text_status_todo": texttodo, "langid": langid, 
        "instructions": instructions, 
        "translate_box_columns": TRANSLATE_BOX_SIZE[page_id][0], 
        "translate_box_rows": TRANSLATE_BOX_SIZE[page_id][1], 
        "pageid": page_id, "dataprefix": data_prefix}
    html_form = """<tr>%s</tr>""" % one_table_row
    return html_form
