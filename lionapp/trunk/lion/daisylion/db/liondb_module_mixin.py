import daisylion.db.modules

class LionDBModuleMixIn():
    """The module functionality"""
    def __init__(self):
        # Import the application module, which lives here:
        # top-level/modules/APP/lionio_APP.someclass
        # someclass is defined in the config file and it inherits from LionIOModule
        mod = self.config["main"]["module"]
        self.dbio = self.load_module(
            mod, 
            self.config[mod]["lioniomodule"],
            self.config[mod]["lionioclass"])
    
    def load_module(self, app, module_file, class_name):
        # Import the application module, which lives here:
        # top-level/modules/APP/lionio_APP.someclass
        # someclass is defined in the config file and it inherits from LionIOModule
        module_name = "daisylion.db.modules." + app + "." + module_file
        self.trace_msg("import %s" % module_name)
        module_object = None
        try:
            module = __import__(module_name, globals(), locals(), [''], -1)
            lionioclass = module_name + "." + class_name    
            obj = eval(lionioclass)
            module_object = obj()

        except Exception, e:
            self.die("""Could not load module for application "%s" (%s)""" \
                % (self.target_app, e), 1)
        
        return module_object
    
    def module_import(self, files, langid, option):
        """Import from XML to the database."""
        if not file: self.die("No XML file given.")
        if not self.check_language(langid):
            self.die("No table for language %s." % langid)
        self.trace_msg("Import from %s for %s" % (files, langid))
        self.dbio.import_xml(self, files, langid, option)
        removed_ids = self.dbio.get_removed_ids_after_import()
        if langid == self.masterlang:
            self.process_changes(removed_ids)
    
    def module_export(self, langid, option, output_dir):
        print self.dbio.export(self, langid, option, output_dir)
