from optparse import OptionParser
import daisylion.db.liondb

class GlobalOptionsParser(OptionParser):
    def __init__(self, usage):
        OptionParser.__init__(self, usage=usage)
        self.add_option("-t", "--trace", dest="trace", 
            help="Enable program trace.", action="store_true", default=False)
        self.add_option("-f", "--force", dest="force", 
            help="Do not ask before executing potentially dangerous actions", 
            action="store_true", default=False)
        self.add_option("-c", "--config", dest="config", 
            help="Configuration file", default="../config/lion.cfg")
        
        (self.options, self.args) = self.parse_args()
    