from global_options_parser import *
from daisylion.db.liondb import LionDB

HTML_TEMPLATE = """<?xml version="1.0"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xml:lang="en" lang="en" xmlns="http://www.w3.org/1999/xhtml">
	<head>
    	<title>%s</title>
    	<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
  	</head>
  	<body>
  	%s
  	</body>
</html>"""

def main():
    usage = """usage: %prog langid"""
    parser = GlobalOptionsParser(usage=usage)
    parser.add_option("-p", "--pretty", dest="pretty", 
        help="Format as html", action="store_true", default=False)
    
    (options, args) = parser.parse_args()
    parser.check_args(1, args)
    
    session = LionDB(options.config, options.trace, options.app)    
    results = session.get_new_todo(args[0])
    langname = session.get_langname(args[0])[0]
    
    if options.pretty == False:
        print "Items still requiring translation work for %s (%s)" % (langname, args[0])
    html_body = "<p>%d items</p>" % len(results)
    for r in results:
        if r[2] == 2: status = "TODO"
        else: status = "NEW"
        if options.pretty == True:
            if len(r) > 1 and r[1] != None:
                html_body += """<h1 id="%s">%s</h1>""" % (r[0], r[1].encode("utf-8"))
            else:
                html_body += """<h1>MISSING %s</h1>""" % r[0]
        else:
            if len(r) > 1 and r[1] != None:
                line ="%-25s%-10s%-10s" % (status, r[0], r[1].encode("utf-8")) 
            else:
                line = "%-25s%-10s%-10s" % (status, r[0], "MISSING")
            print line	
    if options.pretty == False:
		print "%d items" % len(results)
	
    if options.pretty == True:
        print HTML_TEMPLATE % ("amis %s" % langname, html_body)

    
if __name__=="__main__": main()


