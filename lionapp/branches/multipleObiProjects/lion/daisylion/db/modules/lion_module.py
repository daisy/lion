import daisylion.db.modules

class LionIOModule():
    """All IO modules should derive from this class"""
    def import_xml(self, session, file, langid, import_type):
        return NotImplemented
    
    def get_removed_ids_after_import(self):
        return NotImplemented
    
    def export(self, session, langid, export_type, additional_params):
        return NotImplemented
  