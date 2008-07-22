from amis_import import AmisImport
import amis_export
import os
os.sys.path.append("../")
import lion_module

class AmisLionIO (lion_module.LionIOModule):
    """The AMIS-specific implementation of lion_module.LionIOModule"""
    self.importer = None
    
    def import_from_xml(self, session, filepath, langid):
        """Import a document object (from minidom) into a table."""
        self.importer = AmisImport()
        self.session = session
        self.importer.import_from_xml(session, filepath, langid)
        
    def get_removed_ids_after_import(self):
        """Items that have been removed are specified in the document root's 
        "removed" attribute"""
        return self.importer.process_removals(self.doc)
    
    def export(self, session, file, langid, export_type):
        if export_type == 1:
            return amis_export.export_xml(session, file, langid)
        elif export_type == 2:
            return amis_export.export_rc(session, langid)
        elif export_type == 3:
            return amis_export.export_keys_book(session, xmlfile, langid)
        
