# for now, this file can be run on its own
# eventually it should be hooked into the managedb functions

from managedb import *
#from amis_templates import AmisRCTemplate
import amis_templates.AmisRCTemplate
import amis_import
from xml.dom import minidom, Node
import os
import codecs

class FillRC():
    # note that VK_ADD and VK_SUBTRACT (number pad +/-) are permanently mapped
    # to the +/- keys in the template
    # we had to map +/- to VK_OEM keys here because those are suspected to be more common
    vkeys = {"Ctrl": "CONTROL",
        "alt": "ALT",
        "shift": "SHIFT",
        "up": "VK_UP",
        "down": "VK_DOWN",
        "left": "VK_LEFT",
        "right": "VK_RIGHT",
        "esc": "VK_ESCAPE",
        "space": "VK_SPACE",
        "+": "VK_OEM_PLUS",
        "-": "VK_OEM_MINUS",
        "escape": "VK_ESCAPE",
        "uparrow": "VK_UP",
        "downarrow": "VK_DOWN",
        "rightarrow": "VK_RIGHT",
        "leftarrow": "VK_LEFT",
        "f1": "VK_F1",
        "f2": "VK_F2",
        "f3": "VK_F3",
        "f4": "VK_F4",
        "f5": "VK_F5",
        "f6": "VK_F6",
        "f7": "VK_F7",
        "f8": "VK_F8",
        "f9": "VK_F9",
        "f10": "VK_F10",
        "f11": "VK_F11",
        "f12": "VK_F12"}
    
    def __init__(self, session, langid):
        self.langid = langid
        self.session = session
        self.table = self.session.make_table_name(langid)
    
    def __get_textstring(self, strid):
        self.session.execute_query("SELECT textstring FROM %s WHERE xmlid='%s'" % (self.table, strid))
        row = self.session.cursor.fetchone()
        if row == None or len(row) == 0: return None
        else: return row[0]
    
    def __get_mnemonic(self, strid):
        self.session.execute_query("SELECT textstring FROM %s WHERE role='MNEMONIC' AND target='%s'" \
            % (self.table, strid))
        row = self.session.cursor.fetchone()
        if row == None or len(row) == 0: return None
        else: return row[0]
    
    def __get_accelerator(self, strid):
        self.session.execute_query("SELECT textstring FROM %s WHERE role='ACCELERATOR' AND target='%s'" \
            % (self.table, strid))
        row = self.session.cursor.fetchone()
        if row == None or len(row) == 0: return None
        else: return row[0]
    
    def __apply_mnemonic(self, caption, mnemonic):
        if mnemonic == None or len(mnemonic) == 0:
            return caption
        pos = caption.lower().find(mnemonic.lower())
        if pos == -1:
            return "%s (&%s)" % (caption, mnemonic)
        else:
            return "%s&%s" % (caption[0:pos], caption[pos::])
    
    def __parse_keys_from_db(self, strid):
        """From 'Ctrl+0' return (Ctrl,), 0
        From 'Alt+Ctrl+0 return (Alt, Ctrl), 0"""
        actualkeys = self.session.execute_query("SELECT actualkeys FROM %s WHERE xmlid='%s'" % 
            (self.table, strid))
        row = self.session.cursor.fetchone()
        if row == None or len(row) == 0:
            self.session.warn("No actualkeys for %s" % strid)
            return None, None
        keys = row[0]
        did_substitution = False
        #consider "Ctrl++"
        if keys.endswith("+") == True:
            # reverse the string, replace the last '+' with another letter, but remember what we did
            keys = keys[::-1]
            keys = keys.replace("+", "x", 1)
            did_substitution = True
            keys = keys[::-1]
            
        split = keys.split("+")
        if split == None or len(split) == 0:
            return None, None
        # the keypress is the last one
        keypress = split[len(split)-1:]
        if did_substitution == True:
            # restore the "+" instead of the temporary character "x"
            keypress = "+"
        return split[0:len(split)-1], keypress
    
    def menu(self, strid, accel=True):
        """Build a menu label"""
        caption = self.__get_textstring(strid)
        if caption == None or len(caption) == 0:
            self.session.warn("No caption for %s" % strid)
            return ""
        mnemonic = self.__get_mnemonic(strid)
        caption = self.__apply_mnemonic(caption, mnemonic)
        if accel == True:
            accelerator = self.__get_accelerator(strid)    
            if accelerator != None and len(accelerator) > 0:
                caption += "\\t%s" % accelerator
        return caption

    def s(self, strid):
        """Get a string (including mnemonic, if exists)"""
        return self.menu(strid, False).replace("\n", "\\n")
    
    def join_and_prefix_with_int_token(self, strlist):
        """put the int token before each string"""
        val = ""
        for st in strlist:
            val += "%%d %s " % (self.s(st))
        return val
    
    def k(self, strid):
        """get the key or key name for the accelerator given by strid
        eg. "D" or VK_DOWN
        """
        masks, keypress = self.__parse_keys_from_db(strid)
        if keypress == None or len(keypress) == 0:
            self.session.warn("No key found")
            return ""
        if self.vkeys.has_key(keypress[0].lower()):
            return self.vkeys[keypress[0].lower()]
        else:
            return "\"%s\"" % keypress[0] # return a quoted string
    
        
    def masks(self, strid):
        """generate the appropriate key masks for the accelerator
        eg VIRTKEY, SHIFT, CONTROL, ALT, NOINVERT
        """
        masks, keypress = self.__parse_keys_from_db(strid)
        has_shift = False
        has_control = False
        has_alt = False
        # the order matters
        for m in masks:
            if m.lower() == "shift":
                has_shift = True
            if m.lower() == "control" or m.lower() == "ctrl":
                has_control = True
            if m.lower() == "alt":
                has_alt = True
        
        masklist = []
        if has_shift == True:
            masklist.append("SHIFT")
        if has_control == True:
            masklist.append("CONTROL")
        if has_alt == True:
            masklist.append("ALT")
        
        if len(masklist) > 0:
            maskstring = ", ".join(masklist)
            maskstring += ", "
        else:
            maskstring = ""
        
        val = "VIRTKEY, %sNOINVERT" % maskstring
        return val

def export_xml(session, file, langid):
    table = session.make_table_name(langid)
    session = DBSession(False, False, "amis")
    session.execute_query("SELECT xmlid, textstring, actualkeys, role, audiouri FROM %s" % table)
    doc = minidom.parse(file)
    for xmlid, textstring, actualkeys, role, audiouri in session.cursor:
        elm = amis_import.get_element_by_id(doc, "text", xmlid)
        if elm == None: 
            session.trace_msg("Text element %s not found." % xmlid)
            continue
        
        if elm.firstChild.nodeType == Node.TEXT_NODE:
            if role == "ACCELERATOR":
                elm.firstChild.data = textstring
                elm.parentNode.setAttribute("keys", actualkeys)
            else:
                elm.firstChild.data = textstring
            
            audio_elm = get_audio_sibling(elm)
            if audio_elm != None:
                audio_elm.setAttribute("src", "./audio/" + audiouri)
                audio_elm.setAttribute("from", "")
        else:
            session.warn("Text element %s has no contents." % xmlid)
    
    #outpath = os.path.join("./", table + ".xml")
    #outfile = open(outpath, "w")
    #outfile.write(codecs.BOM_UTF8)
    #outfile.write(doc.toxml().encode("utf-8"))   
    #outfile.write("\n")
    #outfile.close()
    return doc.toxml().encode("utf-8")

def get_audio_sibling(elm):
    """Get the audio sibling for this text element"""
    audios = elm.parentNode.getElementsByTagName("audio")
    if audios != None and len(audios) > 0:
        return audios[0]
    else:
        return None

def export_rc(session, langid):
    # these are template keywords
    # the microsoft #xyz statements had to be replaced with $ms_xyz in the template
    # because "#" is a special character for cheetah (the templating system)
    msterms = {"ms_include": "#include",
        "ms_define": "#define",
        "ms_if": "#if",
        "ms_ifdef": "#ifdef", 
        "ms_ifndef": "#ifndef",
        "ms_endif": "#endif",
        "ms_undef": "#undef",
        "ms_pragma": "#pragma",
        "ms_else": "#else"}
    
    rc = FillRC(session, langid)
    t = amis_templates.AmisRCTemplate.AmisRCTemplate(searchList=msterms)
    t.rc = rc
    return t.respond()
