from amisxml import AmisUiDoc
from xml.dom import Node
import os
from daisylion.db.liondb import *
from xml.dom import minidom, Node

class AmisImport():
    
    def __init__(self, session):
        self.doc = None
        self.session = session
    
    def import_xml(self, filepath, langid):
        """Rebuild the language table from the XML file."""
        self.session.trace_msg("Amis import from XML.  File = %s, Language = %s." % (filepath, langid))
        self.table = self.session.make_table_name(langid)
        # clear the tables
        self.session.execute_query("DELETE FROM %s" % self.table)
        
        # use our implementation of minidom.Document instead
        minidom.Document = AmisUiDoc
        self.doc = minidom.parse(filepath)
        self.doc.set_session(self.session)
        
        # add all the text item data to the table
        for elem in self.doc.getElementsByTagName("text"):
            data = self.doc.parse_text_element(elem)
            if data:
                textstring, audiouri, xmlid, textflag = data
                # keys = the actual keys associated with a command
                keys = elem.parentNode.tagName == "accelerator" and \
                    elem.parentNode.getAttribute("keys") or "NULL"
        
            self.session.execute_query(
            """INSERT INTO %(table)s (textstring, textflag, audiouri, xmlid,
            actualkeys) VALUES ("%(textstring)s", %(textflag)d,
            "%(audiouri)s", "%(xmlid)s", "%(keys)s")""" % \
            {"table": self.table, "textstring": textstring, "textflag": textflag,
                "audiouri": audiouri, "xmlid": xmlid,
                "keys": keys})
    
        # specify relationships 
        self.__set_roles()
        self.__find_mnemonic_groups()
        self.__find_accelerator_targets()
    
    def import_xml_updates_only(self, filepath, langid):
        """Refresh existing text/audio from the XML file"""
        self.session.trace_msg("Amis updates-only import from XML.  File = %s, Language = %s." % (filepath, langid))
        self.table = self.session.make_table_name(langid)
        
        # use our implementation of minidom.Document instead
        minidom.Document = AmisUiDoc
        self.doc = minidom.parse(filepath)
        self.doc.set_session(self.session)
        
        # add all the text item data to the table
        for elem in self.doc.getElementsByTagName("text"):
            data = self.doc.parse_text_element(elem)
            if data:
                textstring, audiouri, xmlid, textflag = data
            
            self.session.execute_query(
            """UPDATE %(table)s SET textstring="%(textstring)s", textflag=%(textflag)d, 
            audiouri="%(audiouri)s" WHERE xmlid="%(xmlid)s" """ % \
            {"table": self.table, "textstring": textstring, "textflag": textflag,
            "audiouri": audiouri, "xmlid": xmlid})
    
    def import_xml_audio_only(self, filepath, langid):
        """Import the audio URIs from the XML file"""
        self.session.trace_msg("Amis audio-only import from XML.  File = %s, Language = %s." % (filepath, langid))
        self.table = self.session.make_table_name(langid)
        
        # use our implementation of minidom.Document instead
        minidom.Document = AmisUiDoc
        self.doc = minidom.parse(filepath)
        self.doc.set_session(self.session)
        
        # add all the text item data to the table
        for elem in self.doc.getElementsByTagName("text"):
            data = self.doc.parse_text_element(elem)
            if data:
                textstring, audiouri, xmlid, textflag = data
        
            self.session.execute_query(
            """UPDATE %(table)s SET audiouri="%(audiouri)s" WHERE xmlid="%(xmlid)s" """ % \
            {"table": self.table, "audiouri": audiouri, 
            "xmlid": xmlid})
        
    def __set_roles(self):
        """Set role for text elements"""
        self.session.execute_query("SELECT id, xmlid, textstring FROM %s" % self.table)
        for id, xmlid, textstring in self.session.cursor:
            elem = self.doc.get_element_by_id("text", xmlid)
            if elem:
                tag = elem.parentNode.tagName
                if tag == "accelerator": role = "ACCELERATOR"
                elif tag == "mnemonic": role = "MNEMONIC"
                elif tag == "caption":
                    tag = elem.parentNode.parentNode.tagName
                    if tag == "action" or tag == "container": role = "MENUITEM"
                    elif tag == "control": role = "CONTROL"
                    elif tag == "dialog": role = "DIALOG"
                    else: role = "STRING"
                else: role = "STRING"
                self.session.trace_msg("Role = %s for %s" % (role, xmlid))
                self.session.execute_query("""UPDATE %s SET role="%s" WHERE id=%s""" % \
                    (self.table, role, id))


    def __find_accelerator_targets(self):
        """Get the accelerator element text ids and write who their targets are.
    The only reason we're using textids is that the code is already in place to do
    the same for mnemonics and it works."""
        idlist = []
        for el in self.doc.getElementsByTagName("accelerator"):
            textelm = self.doc.get_first_child_with_tagname(el, "text")
            idlist.append(textelm.getAttribute("id"))
        idtargets = self.doc.get_targets(idlist)
        for xmlid, targetid in zip(idlist, idtargets):
            request = "UPDATE %s SET target=\"%s\" WHERE xmlid = \"%s\"" % (self.table, targetid, xmlid)
            self.session.execute_query(request)


    def __find_mnemonic_groups(self):
        """Identify groups for the mnemonics based on menu and dialog control
    groupings."""
        groupid = 0
        # Container elements
        for elem in self.doc.getElementsByTagName("container") + \
            self.doc.getElementsByTagName("containers"):
            items = self.doc.get_items_in_container(elem)
            
            self.session.trace_msg("group id = %d" % groupid)
            self.doc.printelements(self.session, items)
            
            self.__get_mnemonics_and_write_data(items, groupid)
            groupid += 1
        
        # Dialog elements
        for elem in self.doc.getElementsByTagName("dialog"):
            items = self.doc.get_items_in_dialog(elem)
            self.__get_mnemonics_and_write_data(items, groupid)
            self.session.trace_msg("group id = %d" % groupid)
            self.doc.printelements(self.session, items)
            groupid += 1


    def get_idlist_for_removal(self):
        """Flag items as removed"""
        ui = self.doc.getElementsByTagName("ui")[0]
        ids_to_remove = ui.getAttribute("removed").split(" ")
        return ids_to_remove    

    def __get_mnemonics_and_write_data(self, items, groupid):
        """get the mnemonic text ids and their targets, and write it to the database"""
        idlist = []
        for it in items:
            elm = self.doc.get_first_child_with_tagname(it, "mnemonic")
            if elm != None:
                xmlid = self.doc.get_first_child_with_tagname(elm, "text").getAttribute("id")
                idlist.append(xmlid)
        idtargets = self.doc.get_targets(idlist)
        for xmlid, targetid in zip(idlist, idtargets):
            request = "UPDATE %s SET mnemonicgroup = %d, target=\"%s\" WHERE xmlid = \"%s\"" % \
                (self.table, groupid, targetid, xmlid)
            self.session.execute_query(request)

