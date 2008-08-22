class LionIOModule():
    """All IO modules should derive from this class"""
    def import_xml(self, session, file, langid):
        return NotImplemented
    
    def get_removed_ids_after_import(self):
        return NotImplemented
    
    def export(self, session, file, langid, export_type):
        return NotImplemented
    
    