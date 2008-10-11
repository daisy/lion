import daisylion.db.modules.lion_module
import obi_import
import obi_export

class ObiLionIO(daisylion.db.modules.lion_module.LionIOModule):
    """Obi-specific import and export from/to .resx files."""

    def import_xml(self, session, files, langid, import_type):
        """Import files into the database."""
        importer = obi_import.ObiImport(session)
        if import_type == 1:
            importer.import_resx(files, langid)
        else:
            importer.update_from_resx(files, langid)

    def get_removed_ids_after_import(self):
        pass

    def export(self, session, langid, export_type, output_folder):
        """Export .resx files for a given language."""
        exporter = obi_export.export_resx(session, langid, output_folder)
        return "OK"
