import modules.lion_module

def main():
    # this stuff would come from the command line and/or a config file
    app = "amis"
    module_name = "modules." + app + ".lionio_" + app
    print "import %s" % module_name
    try:
        module = __import__(module_name, globals(), locals(), [''], -1)
        classname = "AmisLionIO"
        lioniomodule = module_name + "." + classname
        print lioniomodule
        obj = eval(lioniomodule)
        dbio = obj()
        
    except Exception, e :
        print """Unknown application "%s" (%s)""" % (app, e)
    
    print dbio.import_from_xml(1, 2, 3)
    
if __name__ == "__main__":
    main()