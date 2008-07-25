import sys
sys.path.append("/Users/marisa/Projects/lion/lionapp/trunk/lion/local")
import modules.lion_module

def main():
    # this stuff would come from the command line and/or a config file
    app = "dummy"
    app_classname = "DummyLionIO"
    module_name = "modules." + app + ".lionio_" + app
    print "import %s" % module_name
    try:
        module = __import__(module_name, globals(), locals(), [''], -1)
        classname = module_name + "." + app_classname
        obj = eval(classname)
        dbio = obj()
    
    except Exception, e :
        print """Unknown application "%s" (%s)""" % (app, e)
    
    
if __name__ == "__main__":
    main()