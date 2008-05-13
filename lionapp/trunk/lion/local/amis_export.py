# for now, this file can be run on its own
# eventually it should be hooked into the managedb functions

from managedb import *
from AmisRCTemplate import *

class FillRC():
    def __init__(self, langid):
        self.langid = langid
        self.session = DBSession(True, False, "amis")
        self.table = self.session.make_table_name(langid)
    
    def get_textstring(self, strid):
        self.session.execute_query("SELECT textstring FROM %s WHERE xmlid='%s'" % (self.table, strid))
        row = self.session.cursor.fetchone()
        if row == None or len(row) == 0: return None
        else: return row[0]
    
    def get_mnemonic(self, strid):
        self.session.execute_query("SELECT textstring FROM %s WHERE role='MNEMONIC' AND target='%s'" \
            % (self.table, strid))
        row = self.session.cursor.fetchone()
        if row == None or len(row) == 0: return None
        else: return row[0]
    
    def get_accelerator(self, strid):
        self.session.execute_query("SELECT textstring FROM %s WHERE role='ACCELERATOR' AND target='%s'" \
            % (self.table, strid))
        row = self.session.cursor.fetchone()
        if row == None or len(row) == 0: return None
        else: return row[0]
    
    def apply_mnemonic(self, caption, mnemonic):
        if mnemonic == None or len(mnemonic) == 0:
            return caption
        pos = caption.lower().find(mnemonic.lower())
        if pos == -1:
            return "%s (&%s)" % (caption, mnemonic)
        else:
            return "%s&%s" % (caption[0:pos], caption[pos::])
    
    def menu(self, strid, accel=True):
        caption = self.get_textstring(strid)
        if caption == None or len(caption) == 0:
            self.session.warn("No caption for %s" % strid)
            return ""
        mnemonic = self.get_mnemonic(strid)
        caption = self.apply_mnemonic(caption, mnemonic)
        if accel == True:
            accelerator = self.get_accelerator(strid)    
            if accelerator != None and len(accelerator) > 0:
                caption += "\\t%s" % accelerator
        return caption


def main():
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
    
    rc = FillRC("eng-US")
    t = AmisRCTemplate(searchList=msterms)
    t.rc = rc
    print t.respond()


if __name__ == "__main__": main()
