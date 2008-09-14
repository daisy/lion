import os
import getopt
from optparse import OptionParser
import daisylion.db.liondb
import daisylion.config

class GlobalOptionsParser(OptionParser):
    def __init__(self, usage):
        
        OptionParser.__init__(self, usage=usage, description="Scripts for managing the DAISY Lion database.")
        
        self.add_option("-t", "--trace", dest="trace", 
            help="Enable program trace", action="store_true", default=False)
        self.add_option("-f", "--force", dest="force", 
            help="Do not ask before executing potentially dangerous actions", 
            action="store_true", default=False)
        self.add_option("-c", "--config", dest="config", 
            help="Configuration file", default=default_config_file())
        self.add_option("-a", "--app", dest="app", default="amis", 
            help="The target application module")

    def check_args(self, num_required, args):
        if args == None: l = 0
        else: l = len(args)
        if l != num_required:
            self.error("Error: wrong number of arguments (expected %d, got %d)" \
                % (num_required, len(args)))

def default_config_file():
    # the default config file
    config_default = daisylion.config.__path__[0]
    config_default = os.path.join(config_default, "lion.cfg")
    return config_default