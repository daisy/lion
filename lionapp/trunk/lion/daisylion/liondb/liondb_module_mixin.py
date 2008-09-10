import modules

class LionDBModuleMixIn():
    """The module functionality"""
    def __init__(self, app=None):
        if app:
            # Import the application module, which lives here:
            # top-level/modules/APP/lionio_APP.someclass
            # someclass is defined in the config file and it inherits from LionIOModule
            module_name = "modules." + app + "." + self.config[app]["lioniomodule"]
            self.trace_msg("import %s" % module_name)
            try:
                module = __import__(module_name, globals(), locals(), [''], -1)
                classname = self.config[app]["lionioclass"]
                lionioclass = module_name + "." + classname    
                obj = eval(lionioclass)
                self.dbio = obj()
            
            except Exception, e :
                self.die("""Could not load module for application "%s" (%s)""" % (app, e))
        
    def module_import(self, file, langid, option):
        """Import from XML to the database."""
        if not file: self.die("No XML file given.")
        if not self.check_language(langid):
            self.die("No table for language %s." % langid)
        self.trace_msg("Import from %s for %s" % (file, langid))
        self.dbio.import_xml(self, file, langid, option)
        removed_ids = self.dbio.get_removed_ids_after_import()
        if langid == self.masterlang:
            self.__process_changes(langid, removed_ids)
    
    def module_export(self, file, langid, option, extra):
        print self.dbio.export(self, file, langid, option, extra)
