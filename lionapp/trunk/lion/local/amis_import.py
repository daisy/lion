from xml.dom import Node

def find_mnemonic_groups(session, langid):
    """Identify groups for the mnemonics based on menu and dialog control
groupings."""
    groupid = 0
    # Container elements
    for elem in doc.getElementsByTagName("container") + \
        doc.getElementsByTagName("containers"):
        items = get_items_in_container(elem)
        get_mnemonics_and_write_data(langid, items, groupid)
        groupid += 1
    # Dialog elements
    for elem in doc.getElementsByTagName("dialog"):
        items = get_items_in_dialog(elem)
        get_mnemonics_and_write_data(langid, items, groupid)
        groupid += 1

def get_all_children_with_tagname(elem, tagname):
    """Get the immediate children (not the grandchildren) of the element with
the given tag name"""
    return filter(
        lambda n: n.nodeType == Node.ELEMENT_NODE and n.tagName == tagname,
        elem.childNodes)

def get_items_in_container(elem):
    """For an XML element, get the actions and containers. Look one level deep
(also look in switches)."""
    items = []
    items.extend(get_all_children_with_tagname(elem, "action"))
    items.extend(get_all_children_with_tagname(elem, "container"))
    for sw in get_all_children_with_tagname(elem, "switch"):
        items.extend(get_all_children_with_tagname(sw, "action"))
        items.extend(get_all_children_with_tagname(sw, "container"))
    return items

def set_roles(doc, session, langid):
    """Set role for text elements (?)"""
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

def find_accelerator_targets(table):
    """Get the accelerator element text ids and write who their targets are.
The only reason we're using textids is that the code is already in place to do
the same for mnemonics and it works."""
    idlist = []
    for el in doc.getElementsByTagName("accelerator"):
        textelm = get_first_child_with_tagname(el, "text")
        idlist.append(textelm.getAttribute("id"))
    idtargets = get_targets(idlist)
    for xmlid, targetid in zip(idlist, idtargets):
        request = "UPDATE %s SET target=\"%s\" WHERE xmlid = \"%s\"" % (table, targetid, xmlid)
        execute(request)

def get_targets(idlist):
    """from the textid of a mnemonic or accelerator, find out who it is intended for"""
    targets = []
    for xmlid in idlist:
        #the <text> element of the mnemonic or accelerator
        elm = find_element_with_id("text", xmlid)
        #the parent element of the mnemonic or accelerator
        parentTag = elm.parentNode.parentNode.tagName
        if parentTag == "action" or parentTag == "container" or parentTag == "control" or parentTag == "dialog":
            caption = getFirstChildWithTagName(elm.parentNode.parentNode, "caption")
            textid = getTextIdForCaption(caption)
            targets.append(textid)
    return targets

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
        
    if elem.getAttribute("flag") == "new": textflag = 3
    elif elem.getAttribute("flag") == "changed": textflag = 2
    else: textflag = 1
    
    if audio.getAttribute("flag") == "new": audioflag = 3
    elif audio.getAttribute("flag") == "changed": audioflag = 2
    else: audioflag = 1
    
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

