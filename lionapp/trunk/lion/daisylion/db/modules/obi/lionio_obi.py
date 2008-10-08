import daisylion.db.modules.lion_module

class ObiLionIO(daisylion.db.modules.lion_module.LionIOModule):
    """Obi"""

    def import_xml(self, session, file, langid, import_type):
        """Import a document object (from minidom) into a table. The cursor has
        the current connection to the database."""
        session.trace_msg("IMPORT FROM OBI.")

    def get_removed_ids_after_import(self):
        pass

    def export(session, langid, file):
        session.trace_msg("EXPORT FROM OBI.")
