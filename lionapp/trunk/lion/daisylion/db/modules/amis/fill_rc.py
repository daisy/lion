import os
from daisylion.db.liondb import *

class FillRC():
    # note that VK_ADD and VK_SUBTRACT (number pad +/-) are permanently mapped
    # to the +/- keys in the template
    # we had to map +/- to VK_OEM keys here because those are suspected to be more common
    vkeys = {"ctrl": "CONTROL",
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
        caption = self.session.get_textstring(self.table, strid)
        if caption == None or len(caption) == 0:
            self.session.warn("No caption for %s" % strid)
            return ""
        mnemonic = self.session.get_mnemonic(self.table, strid)
        caption = self.__apply_mnemonic(caption, mnemonic)
        if accel == True:
            accelerator = self.session.get_accelerator(self.table, strid)    
            if accelerator != None and len(accelerator) > 0:
                caption += "\\t%s" % accelerator
        return caption

    def s(self, strid):
        """Get a string (including mnemonic, if exists)"""
        return self.menu(strid, False).replace("\n", "\\n")
    
    def s2(self, strid1, strid2):
        """concatenate the string with strid + str"""
        ret = self.session.get_textstring(self.table, strid1)
        ret += " "
        ret += self.session.get_textstring(self.table, strid2)
        return ret
    
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
