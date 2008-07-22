from amisxml import AmisUiDoc
from xml.dom import Node
import os
os.sys.path.append("../../")
from liondb import LionDB       # the session object

class AmisImport():
    
    def __init__(self, session, amisxml):
        self.doc = amisxml  # the xml document
        self.session = session
        
    def set_roles(self, table):
        """Set role for text elements"""
        self.session.execute_query("SELECT id, xmlid, textstring FROM %s" % table)
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
                if self.session.trace == True:
                    print "Role = %s for %s" % (role, xmlid)
                self.session.execute_query("""UPDATE %s SET role="%s" WHERE id=%s""" % \
                    (table, role, id))


    def find_accelerator_targets(self, session, table):
        """Get the accelerator element text ids and write who their targets are.
    The only reason we're using textids is that the code is already in place to do
    the same for mnemonics and it works."""
        idlist = []
        for el in self.doc.getElementsByTagName("accelerator"):
            textelm = self.doc.get_first_child_with_tagname(el, "text")
            idlist.append(textelm.getAttribute("id"))
        idtargets = self.doc.get_targets(idlist)
        for xmlid, targetid in zip(idlist, idtargets):
            request = "UPDATE %s SET target=\"%s\" WHERE xmlid = \"%s\"" % (table, targetid, xmlid)
            self.session.execute_query(request)


    def find_mnemonic_groups(self, session, table):
        """Identify groups for the mnemonics based on menu and dialog control
    groupings."""
        groupid = 0
        # Container elements
        for elem in self.doc.getElementsByTagName("container") + \
            self.doc.getElementsByTagName("containers"):
            items = self.doc.get_items_in_container(elem)
            
            # redo this
            if self.session.trace == True:
                print "group id = %d" % groupid
                self.doc.printelements(items)
            
            self.get_mnemonics_and_write_data(doc, session, table, items, groupid)
            groupid += 1
        # Dialog elements
        for elem in self.doc.getElementsByTagName("dialog"):
            items = self.doc.get_items_in_dialog(elem)
            self.get_mnemonics_and_write_data(doc, session, table, items, groupid)
            if session.trace == True:
                print "group id = %d" % groupid
                printelements(session, items)
            groupid += 1


    def process_removals(self, doc):
        """Flag items as removed"""
        ui = self.doc.getElementsByTagName("ui")[0]
        ids_to_remove = ui.getAttribute("removed").split(" ")
        return ids_to_remove    

    def get_mnemonics_and_write_data(self, doc, session, table, items, groupid):
        """get the mnemonic text ids and their targets, and write it to the database"""
        idlist = []
        for it in items:
            elm = get_first_child_with_tagname(it, "mnemonic")
            if elm != None:
                xmlid = self.doc.get_first_child_with_tagname(elm, "text").getAttribute("id")
                idlist.append(xmlid)
        idtargets = self.doc.get_targets(idlist)
        for xmlid, targetid in zip(idlist, idtargets):
            request = "UPDATE %s SET mnemonicgroup = %d, target=\"%s\" WHERE xmlid = \"%s\"" % (table, groupid, targetid, xmlid)
            session.execute_query(request)

