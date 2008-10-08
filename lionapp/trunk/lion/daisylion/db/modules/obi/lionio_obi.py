import daisylion.db.modules.lion_module
import obi_import

class ObiLionIO(daisylion.db.modules.lion_module.LionIOModule):
    """Obi-specific import and export from/to .resx files."""

    def import_xml(self, session, file, langid, import_type):
        """Import a document object (from minidom) into a table. The cursor has
        the current connection to the database."""
        importer = obi_import.ObiImport(session)
        if import_type == 1:
            importer.import_resx(file, langid)
        else:
            importer.update_from_resx(file, langid)

    def get_removed_ids_after_import(self):
        pass

    def export(session, langid, file):
        session.trace_msg("EXPORT FROM OBI.")
