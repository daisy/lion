import templates.ncc
import templates.smil
import templates.xhtml_daisy_text
import os
from daisylion.db.liondb import *
import amisxml
from xml.dom import minidom, Node
import xml.dom.minidom

# some classes to help organize the data
# a combination of the XML file and the database is used to produce a list of all the menus
# plus a few other lists that just contain the headings/phrases for the introduction
# The list of lists will be:
#
# 1. Title (only one item in this list)
# 2. Organized by menu
# 3....n. Each menu
# n+1. Other shortcuts
#
# the first item in each list is the heading of the section

class TextAudio():
    """a text and audio pair, plus an id"""
    def __init__(self):
        self.id = ""
        self.text = ""
        self.audio = ""

class Shortcut(TextAudio):
    """a key shortcut is a textaudio object plus a shortcut type"""
    def __init__(self):
        TextAudio.__init__()
        self.shortcut_type = 0
    
class PhrasePair():
    def __init__(self):
        self.caption = None
        self.shortcut = None

# enumeration
MNEMONIC, ACCELERATOR = range(2)


def export_keys_book(session, xmlfile, langid, folder, local_audio_dir):
    """generate a DAISY book of the keyboard commands"""
    table = session.make_table_name(langid)
    
    # get the menus based on the XML file structure
    menus = __calculate_menus(session, langid, xmlfile)
    
    title_chapter, organized_by_menu_chapter, other_commands_chapter = \
        __make_predetermined_chapters(session, table)
    
    # fill in the NCC template
    nav = templates.ncc.ncc()
    nav.langid = langid
    nav.menus = menus
    """for menu in menus:
        for m in menu:
            session.trace_msg(m.caption.text)
            session.trace_msg(m.caption.id)
            session.trace_msg(m.caption.audio)
        session.trace_msg("---")
    """
    nav.title_chapter = title_chapter
    nav.organized_by_menu_chapter = organized_by_menu_chapter
    nav.other_commands_chapter = other_commands_chapter
    navstring = nav.respond()
    
    
    # fill in the text template
    txt = templates.xhtml_daisy_text.xhtml_daisy_text()
    txt.langid = langid
    txt.menus = menus
    txt.title_chapter = title_chapter
    txt.organized_by_menu_chapter = organized_by_menu_chapter
    txt.other_commands_chapter = other_commands_chapter
    textfile = txt.respond()
    textfilename = "amiskeys.html"

    # for each menu item, fill in a smil template.  watch the numbering.
    smiles = []
    smil = templates.smil.smil()
    smil.langid = langid
    smil.title_text = title_chapter[0].caption.text
    smil.textfile = textfilename
    
    audio_files = []
    smil_objects = []
    # the title chapter
    smil.menuitems = title_chapter
    smiles.append(smil.respond())
    smil_objects.append(smil.menuitems)
    
    # the "organized by menu" chapter
    smil.menuitems = organized_by_menu_chapter
    smiles.append(smil.respond())
    smil_objects.append(smil.menuitems)
    
    # all the menus
    for menu in menus:
        smil.menuitems = menu
        smiles.append(smil.respond())
        smil_objects.append(smil.menuitems)
    
    smil.menuitems = other_commands_chapter
    smiles.append(smil.respond())
    smil_objects.append(smil.menuitems)
    
    # collect the audio files
    for s in smil_objects:
        for item in s:
            if item.caption != None: 
                audio_files.append(item.caption.audio)
            if item.shortcut != None:
                audio_files.append(item.shortcut.audio)
    
    __write_to_disk(folder, textfilename, navstring, textfile, smiles)
    __copy_audio_files(local_audio_dir, audio_files, folder)

def __calculate_menus(session, langid, xmlfile):
    # use our dom instead
    xml.dom.minidom.Document = amisxml.AmisUiDoc
    doc = minidom.parse(xmlfile)
    doc.set_session(session)

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
            # skip the mfcid's that say BASE_ID -- these are the start of dynamic lists, such
            # as recent books or bookmarks or available navigation panes, and don't need to be
            # listed in the commands list
            if node.nodeType == Node.ELEMENT_NODE and (node.tagName == "action" or node.tagName == "container") \
                and not ("BASE_ID" in node.getAttribute("mfcid")):
                menu.append(node)
        menus.append(__make_menu(session, table, menu, doc))

    return menus

def __make_menu(session, table, elms, doc):
    """return an object with text, shortcut, textid, and shortcutid"""
    # the menu list represents the menuheader followed by all its first-level children
    # there is no need to go any deeper 
    menulist = []
    for elm in elms:
        menuitem = PhrasePair()
        menuitem.caption = TextAudio()
        caption_elms = elm.getElementsByTagName("caption")
        menuitem.caption.id = doc.get_text_id_for_caption(caption_elms[0])
        menulist.append(menuitem)

    return __get_all_data_from_idlist(session, table, menulist)

def __get_all_data_from_idlist(session, table, idlist):
    """idlist looks like a list of PhrasePair objects, with the caption.id field filled in"""
    for item in idlist:
        item.caption.text = session.get_textstring(table, item.caption.id)
        item.caption.audio = session.get_audiouri(table, item.caption.id)
        # first, look for an accelerator (e.g. Ctrl + O)
        shortcut_text = session.get_accelerator(table, item.caption.id)
        if shortcut_text != None or shortcut_text == "":
            shortcut_type = ACCELERATOR
            shortcut_id = session.get_accelerator_id(table, item.caption.id)
        # then settle for a mnemonic
        else:
            shortcut_type = MNEMONIC
            shortcut_id = session.get_mnemonic_id(table, item.caption.id)
            shortcut_text = session.get_mnemonic(table, item.caption.id)
            
        # if this item has a shortcut of some type
        if shortcut_text != None and shortcut_text != "":
            item.shortcut = TextAudio()
            item.shortcut.text = shortcut_text
            item.shortcut.shortcut_type = shortcut_type
            item.shortcut.id = shortcut_id
            item.shortcut.audio = session.get_audiouri(table, shortcut_id)
            
    return idlist

def __make_predetermined_chapters(session, table):
    # these are commands that aren't in the menus
    """+-------+------------------------------+
    | xmlid | textstring                   |
    +-------+------------------------------+
    | t394  | Toggle book audio         | 
    | t396  | Toggle self-voicing audio    | 
    | t399  | Focus on sidebar             | 
    | t402  | Focus on text                | 
    | t405  | Decrease self-voicing volume | 
    | t408  | Increase self-voicing volume | 
    | t411  | Decrease book volume         | 
    | t414  | Increase book volume         | 
    | t417  | Decrease section depth       | 
    | t420  | Find next                    | 
    | t423  | Find previous                | 
    | t426  | Increase section depth       | 
    | t429  | Reset highlight colors       | 
    | t440  | Increase TTS volume          | 
    | t443  | Decrease TTS volume          | 
    +-------+------------------------------+
    """
    extra_ids = ["t420", "t423", 
        "t399", "t402", 
        "t394", "t396", 
        "t405", "t408", 
        "t411", "t414",
        "t440", "t443", 
        "t417", "t426", 
        "t429", ]
    extra_ids_as_menuitems = []
    for id in extra_ids:
        item = PhrasePair()
        item.caption = TextAudio()
        item.caption.id = id
        extra_ids_as_menuitems.append(item)
    other_commands_chapter = __get_all_data_from_idlist(session, table, extra_ids_as_menuitems)
    
    # the pre-determined chapters
    title_chapter = []
    organized_by_menu_chapter = []
    title = PhrasePair()
    title.caption = TextAudio()
    title.caption.text = session.get_textstring(table, "t391")
    title.caption.audio = session.get_audiouri(table, "t391")
    title.caption.id = "t391"
    organized_by_menu_header = PhrasePair()
    organized_by_menu_header.caption = TextAudio()
    organized_by_menu_header.caption.text = session.get_textstring(table, "t392")
    organized_by_menu_header.caption.audio = session.get_audiouri(table, "t392")
    organized_by_menu_header.caption.id = "t392"
    other_commands_header = PhrasePair()
    other_commands_header.caption = TextAudio()
    other_commands_header.caption.text = session.get_textstring(table, "t393")
    other_commands_header.caption.audio = session.get_audiouri(table, "t393")
    other_commands_header.caption.id = "t393"

    description = PhrasePair()
    description.caption = TextAudio()
    description.caption.text = session.get_textstring(table, "t439")
    description.caption.audio = session.get_audiouri(table, "t439")
    description.caption.id = "desc"
    
    # fill in the pre-determined chapters
    title_chapter.append(title)
    title_chapter.append(description)
    organized_by_menu_chapter.append(organized_by_menu_header)
    other_commands_chapter.insert(0, other_commands_header)
    
    return title_chapter, organized_by_menu_chapter, other_commands_chapter

def __write_to_disk(folder, textfilename, navstring, textfile, smiles):
    f = open(folder + textfilename, "w")
    f.write(textfile)
    f.close()
    
    f = open(folder + "ncc.html", "w")
    f.write(navstring)
    f.close()
    
    smilcount = 1
    for s in smiles:
        f = open(folder + str(smilcount) + ".smil", "w")
        # our audio files aren't in any directory
        s = s.replace("<audio src=\"./audio/", "<audio src=\"")
        f.write(s)
        f.close()
        smilcount += 1
        

def __copy_audio_files(sourcefolder, audio_files, destfolder):
    if not sourcefolder.endswith("/"): sourcefolder += "/"
    for a in audio_files:
        f = sourcefolder + a.replace("./audio/", "")
        print f
        cmd = "cp %s %s" % (f, destfolder)
        os.popen(cmd)
    