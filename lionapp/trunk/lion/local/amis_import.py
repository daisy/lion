from xml.dom import Node

def find_accelerator_targets(doc, session, table):
    """Get the accelerator element text ids and write who their targets are.
The only reason we're using textids is that the code is already in place to do
the same for mnemonics and it works."""
    idlist = []
    for elem in doc.getElementsByTagName("accelerator"):
        textelem = get_first_child_with_tagname(elem, "text")
        idlist.append(textelem.getAttribute("id"))
    idtargets = get_targets(idlist)
    for xmlid, targetid in zip(idlist, idtargets):
        session.execute_query("""
UPDATE %s SET target="%s" WHERE xmlid="%s" """ % (table, targetid, xmlid))

def find_mnemonic_groups(doc, session, langid):
    """Identify groups for the mnemonics based on menu and dialog control
groupings."""
    groupid = 0
    # Container elements
    for elem in doc.getElementsByTagName("container") + \
        doc.getElementsByTagName("containers"):
        items = get_items_in_container(elem)
        get_mnemonics_and_write_data(doc, session, langid, items, groupid)
        groupid += 1
    # Dialog elements
    for elem in doc.getElementsByTagName("dialog"):
        items = get_items_in_dialog(elem)
        get_mnemonics_and_write_data(doc, session, langid, items, groupid)
        groupid += 1

def get_all_children_with_tagname(elem, tagname):
    """Get the immediate children (not the grandchildren) of the element with
the given tag name"""
    return filter(
        lambda n: n.nodeType == Node.ELEMENT_NODE and n.tagName == tagname,
        elem.childNodes)

def get_element_by_id(doc, tagname, id):
    """Workaround the absence of DTD."""
    for t in doc.getElementsByTagName(tagname):
        if t.getAttribute("id") == id:
            return t

def get_first_child_with_tagname(elem, tagname):
    """Get first child of elem with tagname tag name."""
    for c in elem.childNodes:
        if c.nodeType == Node.ELEMENT_NODE and c.tagName == tagname:
            return c
    return None

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

def get_mnemonics_and_write_data(doc, session, table, items, groupid):
    """Get the mnemonic text ids and their targets, and write it to the
database."""
    idlist = []
    for it in items:
        elem = get_first_child_with_tagname(it, "mnemonic")
        if elem != None:
            idlist.append(
                get_first_child_with_tagname(elem, "text").getAttribute("id"))
    idtargets = get_targets(doc, idlist)
    for xmlid, targetid in zip(idlist, idtargets):
        session.execute_query("""
UPDATE %s SET mnemonicgroup = %d, target="%s" WHERE xmlid="%s" """ % \
        (table, groupid, targetid, xmlid))

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

def get_targets(doc, idlist):
    """From the textid of a mnemonic or accelerator, find out who it is
intended for."""
    targets = []
    for xmlid in idlist:
        # the <text> element of the mnemonic or accelerator
        elem = get_element_by_id(doc, "text", xmlid)
        # the parent element of the mnemonic or accelerator
        parentTag = elem.parentNode.parentNode.tagName
        if parentTag == "action" or parentTag == "container" or \
                parentTag == "control" or parentTag == "dialog":
            caption = get_first_child_with_tagname(elem.parentNode.parentNode,
                    "caption")
            targets.append(get_text_id_for_caption(doc, caption))
    return targets

def get_text_id_for_caption(doc, elem):
    """Resolve the text for the caption element.  It might be directly nested
or it might be a prompt reference.
The permutations are:
    1. <caption>
        <text>The text</text>
        ...

    2. <caption>
        <promptItem refid="id123"/>
        means "go find the text in prompt@id='id123'"

    3. <caption>
        <promptItem>
            <text>The text</text>

    4. <caption>
        <prompt>
            <promptItem ... can be either with a refid or with nested text

    ignore all other cases."""
    # the obvious case #1
    text = get_first_child_with_tagname(elem, "text")
    # the less-obvious cases
    if text == None:
        promptItem = get_first_child_with_tagname(elem, "promptItem")
        if promptItem == None:
            prompt = get_first_child_with_tagname(elem, "prompt")
            if prompt == None: return ""
            promptItem = get_first_child_with_tagname(prompt, "promptItem")
            if promptItem == None: return ""
        #promptItem variable better have something in it at this point
        return get_text_id_from_prompt_item(promptItem)
    else:
        return text.getAttribute("id")

def get_text_id_from_prompt_item(doc, elem):
    """Get the text out of a prompt item.  Resolve references if necessary."""
    if elem == None: return ""
    text = get_first_child_with_tagname(elem, "text")
    if text != None:
        return text.getAttribute("id")
    else:
        refid = elem.getAttribute("refid")
        if refid:
            prompt = get_element_by_id(doc, "promptItem", refid)
            return get_text_id_from_prompt_item(prompt)
        else:
            return ""

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
