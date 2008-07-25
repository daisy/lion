import sys
sys.path.append("/Users/marisa/Projects/lion/lionapp/trunk/lion/local")
import modules.lion_module

class DummyLionIO (lion_module.LionIOModule):
    """a dumb test"""
    def import_from_xml(self, session, filepath, langid):
        return "dummy import"
        
    def get_removed_ids_after_import(self):
        return "dummy get removed ids"
    
    def export(self, session, file, langid, export_type, output_folder = ""):
        return "dummy export"
