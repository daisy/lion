import daisylion.db.modules.lion_module
import obi_import
import obi_export

class ObiLionIO(daisylion.db.modules.lion_module.LionIOModule):
    """Obi-specific import and export from/to .resx files."""

    def import_xml(self, session, files, langid, import_type):
        """Import files into the database. 1 is create a new master language
        table for the application; 2 is populate a language table for existing
        translated files; 3 is update the application for the master language
        resource files and propagate the changes to existing languages."""
        importer = obi_import.ObiImport(session)
        if import_type == 1:
            importer.import_resx(files, langid)
        elif import_type == 2:
            importer.populate_from_resx(files, langid)
        elif import_type == 3:
            importer.update_from_resx(files, langid)
        else:
            session.die("Import type must be 1, 2 or 3 (got %s)" % import_type)

    def get_removed_ids_after_import(self):
        pass

    def export(self, session, langid, export_type, additional_params):
        """Export .resx files for a given language."""
        exporter = obi_export.export_resx(session, langid, additional_params[0])
        return "OK"
