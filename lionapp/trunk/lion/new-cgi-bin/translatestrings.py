from translationpage import *

class TranslateStrings(TranslationPage):
    """The page of all the strings (the main page)"""
    def __init__(self):
        self.title = "AMIS Translation -- main section"
        self.section = "main"
        self.textbox_columns = 64
        self.textbox_rows = 3
        self.instructions = "Enter the translation:"
        self.about = "This is the main page.  All the strings to be translated\
         for the AMIS interface are on this page."
        self.roles_sql =  """ and (%(table)s.role="STRING" or \
            %(table)s.role="CONTROL" or %(table)s.role="DIALOG" or \
            %(table)s.role="MENUITEM") """ % {"table": "%(table)s"}            
            
        # the other pages (mnemonics, accelerators) will need this sql:
        #"mnemonics": """ and %(table)s.role="MNEMONIC" """, 
        #"accelerators": """ and %(table)s.role="ACCELERATOR" """}
