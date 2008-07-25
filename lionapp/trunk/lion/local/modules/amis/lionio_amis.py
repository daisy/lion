import amis_import
import amis_export
import modules.lion_module

class AmisLionIO (modules.lion_module.LionIOModule):
    """The AMIS-specific implementation of lion_module.LionIOModule"""
    importer = None
    
    def import_from_xml(self, session, filepath, langid):
        """Import a document object (from minidom) into a table."""
        self.importer = amis_import.AmisImport()
        self.session = session
        self.importer.import_from_xml(session, filepath, langid)
        
    def get_removed_ids_after_import(self):
        """Items that have been removed are specified in the document root's 
        "removed" attribute"""
        return self.importer.process_removals(self.doc)
    
    def export(self, session, file, langid, export_type, output_folder = ""):
        if export_type == 1:
            return amis_export.export_xml(session, file, langid)
        elif export_type == 2:
            return amis_export.export_rc(session, langid)
        elif export_type == 3:
            sz = len(output_folder)
            # make sure the folder path ends with a slash
            if sz > 0 and output_folder[sz-1] != '/':
                output_folder.append('/')
            return amis_export.export_keys_book(session, file, langid, output_folder)
