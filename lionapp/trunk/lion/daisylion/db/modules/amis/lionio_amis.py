import os
import amis_import
import amis_export
import daisylion.db.modules.lion_module

class AmisLionIO (daisylion.db.modules.lion_module.LionIOModule):
    """The AMIS-specific implementation of lion_module.LionIOModule"""
    def import_xml(self, session, file, langid, import_type):
        """Import a document object (from minidom) into a table."""
        self.importer = amis_import.AmisImport(session)
        
        if import_type == None or import_type == 1:
            self.importer.import_xml(file, langid)
        elif import_type == 2:
            self.importer.import_xml_updates_only(file, langid)
        elif import_type == 3:
            self.importer.import_xml_audio_only(file, langid)
    
    def get_removed_ids_after_import(self):
        """Items that have been removed are specified in the document root's 
        "removed" attribute"""
        return self.importer.get_idlist_for_removal()
    
    def export(self, session, langid, export_type, additional_params=[]):
        # the xml file that acts as a template for exports
        xml_filepath = daisylion.db.modules.amis.templates.__path__[0]
        xml_filepath = os.path.join(xml_filepath, "amisAccessibleUi.xml")
        
        if export_type == 1:
            return amis_export.export_xml(session, xml_filepath, langid)
        elif export_type == 2:
            return amis_export.export_rc(session, langid)
        elif export_type == 3:
            output_folder = additional_params[0]
            local_audio_dir = additional_params[1]
            sz = len(output_folder)
            # make sure the folder path ends with a slash
            if sz > 0 and output_folder[sz-1] != '/':
                output_folder += '/'
            return amis_export.export_keys_book(session, xml_filepath, langid, output_folder, local_audio_dir)
    
