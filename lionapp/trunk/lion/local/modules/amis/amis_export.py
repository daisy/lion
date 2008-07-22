import os
os.sys.path.append("../../")
from liondb import *
import codecs
import amisxml
import templates.ncc
import templates.smil
import templates.xhtml_daisy_text
import fill_rc

def export_xml(session, file, langid):
    session.trace_msg("XML Export for %s to %s" % (langid, file))
    # use our dom instead
    xml.dom.minidom.Document = amisxml.AmisUiDoc
    doc = minidom.parse(file)
    doc.set_session(self.session)
    if doc == None:
        session.die("Document could not be parsed.")
    
    table = session.make_table_name(langid)
    session.execute_query("SELECT xmlid, textstring, actualkeys, role, audiouri FROM %s" % table)
    
    for xmlid, textstring, actualkeys, role, audiouri in session.cursor:
        elm = doc.get_element_by_id("text", xmlid)
        if elm == None: 
            session.trace_msg("Text element %s not found." % xmlid)
            continue
        
        if elm.firstChild.nodeType == Node.TEXT_NODE:
            if role == "ACCELERATOR":
                elm.firstChild.data = textstring
                elm.parentNode.setAttribute("keys", actualkeys)
            else:
                elm.firstChild.data = textstring
            
            audio_elm = doc.get_audio_sibling(elm)
            if audio_elm != None:
                audio_elm.setAttribute("src", "./audio/" + audiouri)
                audio_elm.setAttribute("from", "")
        else:
            session.warn("Text element %s has no contents." % xmlid)
    
    return doc.toxml().encode("utf-8")


def export_rc(session, langid):
    # these are template keywords
    # the microsoft #xyz statements had to be replaced with $ms_xyz in the template
    # because "#" is a special character for cheetah (the templating system)
    session.trace_msg("RC Export for %s" % (langid))
    msterms = {"ms_include": "#include",
        "ms_define": "#define",
        "ms_if": "#if",
        "ms_ifdef": "#ifdef", 
        "ms_ifndef": "#ifndef",
        "ms_endif": "#endif",
        "ms_undef": "#undef",
        "ms_pragma": "#pragma",
        "ms_else": "#else"}
    
    rc = fill_rc.FillRC(session, langid)
    t = amis_templates.AmisRCTemplate.AmisRCTemplate(searchList=msterms)
    t.rc = rc
    return t.respond()

def export_keys_book(session, xmlfile, langid):
    """Fill in the templates for the keyboard shortcuts book"""
    session.trace_msg ("Keyboard shortcuts book export for %s" % (langid))
    
    menus = __calculate_menus(session, langid, xmlfile)

    # TODO: fill in "others" list
    others_ids = [""]
    # fill in the NCC template
    nav = amis_templates.keyboard_shortcuts_book.ncc.ncc()
    nav.menus = menus
    nav.title = "AMIS Keyboard Shortcuts"
    nav.langid = langid
    nav.organized_by_menu = "Organized by menu"
    nav.other_shortcuts = "Other shortcuts"

    navstring = nav.respond()

    # fill in the text template
    txt = amis_templates.keyboard_shortcuts_book.xhtml_daisy_text.xhtml_daisy_text()
    txt.title = "AMIS Keyboard Shortcuts"
    txt.langid = langid
    txt.menus = menus
    txt.other_shortcuts = "Other shortcuts"
    txt.organized_by_menu = "Organized by menu"
    txt.others = None
    print txt.respond()

    # for each menu item, fill in a smil template.  watch the numbering.

def __calculate_menus(session, langid, xmlfile):
    # use our dom instead
    xml.dom.minidom.Document = amisxml.AmisUiDoc
    doc = minidom.parse(file)
    doc.set_session(self.session)
    
    table = session.make_table_name(langid)
    if doc == None:
        session.die("Document could not be parsed.")
    
    # get the menu structure from the XML file
    toplevel = []
    elms = doc.getElementsByTagName("container")
    for elm in elms:
        if elm.parentNode.tagName == "containers":
            toplevel.append(elm)
    
    menus = []
    for elm in toplevel:
        menu = []
        menu.append(elm)
        for node in elm.childNodes:
            if node.nodeType == Node.ELEMENT_NODE and (node.tagName == "action" or node.tagName == "container") \
                and not ("BASE_ID" in node.getAttribute("mfcid")):
                menu.append(node)
        menus.append(__make_menu(session, table, menu))
    
    return menus

# there is probably a more elegant way to do this...
class MenuItem():
    def __init__(self):
        """empty"""

def __make_menu(session, table, elms):
    """return an object with text, shortcut, textid, and shortcutid"""
    # the menu list represents the menuheader followed by all its first-level children
    # there is no need to go any deeper 
    menulist = []
    for elm in elms:
        caption = elm.getElementsByTagName("caption")
        text = caption[0].getElementsByTagName("text")
        audio = caption[0].getElementsByTagName("audio")
        menuitem = MenuItem()
        menuitem.textid = text[0].getAttribute("id")
        menuitem.audiofile = audio[0].getAttribute("src")
        menulist.append(menuitem)
    #TODO: get the audio for the mnemonics/accelerators
    
    # now we have all the ids in the menulist
    # use the DB to get the rest of the data
    for item in menulist:
        textstring = session.get_textstring(session, table, item.textid)
        item.text = textstring
        shortcut = session.get_accelerator(session, table, item.textid)
        if shortcut == None:
            shortcut = session.get_mnemonic(session, table, item.textid)
        item.shortcut = shortcut
        item.shortcutid = item.textid + "s"
    
    return menulist

