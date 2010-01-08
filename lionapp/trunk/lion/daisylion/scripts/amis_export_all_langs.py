from global_options_parser import *
from daisylion.db.liondb import LionDB

#subdir and langid
LANGS=[
["afrikaans", "afr-ZA"],
["australian", "eng-AU"],
["chinese", "zho-CN"],
["icelandic", "ice-IS"],
["tamil", "tam-IN"],
["french", "fra-FR"],
["norwegian-bokmal", "nob-NO"],
["norwegian-nynorsk", "nno-NO"]
]

#all the langpacks are here
LANGPACKS_DIR="/Users/marisa/Devel/amis/trunk/langpacks/"


def main():
    """export all languages listed above for AMIS 3.1
    The output files are copied directly into the language pack directory"""
    usage = """usage: %prog [options]"""
    parser = GlobalOptionsParser(usage=usage)
    (options, args) = parser.parse_args()
    parser.check_args(0, args)
    session = LionDB(options.config, options.trace, "amis")
    
    for lang in LANGS:
        output_dir = os.path.join(LANGPACKS_DIR, lang[0])
        export_one(lang[1], output_dir, session)
    
    print "Done"

        
def export_one(langid, output_dir, session):
    """output_dir must exist"""
    
    amis_version = 3.1
    rc_filename = os.path.join(output_dir, "AmisLangpack/AmisLangpack.rc")
    xml_filename = os.path.join(output_dir, "amisAccessibleUi.xml")
    keys_book_dir = os.path.join(output_dir, "shortcuts")
    local_audio_dir = os.path.join(output_dir, "audio")
    
    session.trace_msg("Exporting %s" % langid)
    
    
    # export an RC file
    rc_data = session.module_export(langid, 2, (amis_version,))
    f = open(rc_filename, "w")
    f.write(rc_data)
    f.close()
    
    #export an XML file
    xml_data = session.module_export(langid, 1, (amis_version,))
    f = open(xml_filename, "w")
    f.write(xml_data)
    f.close()
    
    #export the keyboard shortcuts book
    session.module_export(langid, 3, (amis_version, keys_book_dir, local_audio_dir))
    
    print "Wrote %s" % rc_filename
    print "Wrote %s" % xml_filename
    print "Created the keyboard shortcuts book in %s" % keys_book_dir
    print "Finished %s" % langid

    
if __name__ == "__main__": main()
