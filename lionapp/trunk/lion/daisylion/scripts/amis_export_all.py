from global_options_parser import *
from daisylion.db.liondb import LionDB

def main():
    usage = """usage: %prog [options] langid local_audio_dir"""
    parser = GlobalOptionsParser(usage=usage)
    
    (options, args) = parser.parse_args()
    parser.check_args(2, args)
    
    session = LionDB(options.config, options.trace, "amis")
    
    langid = args[0]
    local_audio_dir = args[1]
    
    output_dir = "/tmp/%s" % langid
    if not os.path.exists(output_dir) or not os.path.isdir(output_dir):
        os.mkdir(output_dir)
    rc_filename = os.path.join(output_dir, "%s.rc" % langid)
    xml_filename = os.path.join(output_dir, "%s.xml" % langid)
    keys_book_dir = os.path.join(output_dir, "keysbook")
    
    if not os.path.exists(keys_book_dir) or not os.path.isdir(keys_book_dir):
        os.mkdir(keys_book_dir)
    
    # export an RC file
    rc_data = session.module_export(langid, 2, None)
    f = open(rc_filename, "w")
    f.write(rc_data)
    f.close()
    
    #export an XML file
    xml_data = session.module_export(langid, 1, None)
    f = open(xml_filename, "w")
    f.write(xml_data)
    f.close()
    
    #export the keyboard shortcuts book
    session.module_export(langid, 3, (keys_book_dir, local_audio_dir))
    print "Wrote %s" % rc_filename
    print "Wrote %s" % xml_filename
    print "Created the keyboard shortcuts book in %s" % keys_book_dir
    print "Done"
    
if __name__=="__main__": main()


