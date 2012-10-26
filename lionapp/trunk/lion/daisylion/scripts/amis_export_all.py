from global_options_parser import *
from daisylion.db.liondb import LionDB
import os
import re

#langid for languages whose translations are complete or ready for testing
LANGS=["afr-ZA", "eng-AU", "zho-CN", "ice-IS", "tam-IN", "fra-FR", "nob-NO", "nno-NO", "jpn-JP", 
"spa", "zho-TW", "vie-VN", "fin-FI", "srp-RS", "swe-SE", "hun-HU", "nld-NL", "heb-IL", "ger-DE", 
"por-PT"]

def main():
	usage = """usage: %prog [options] local_langpack_dir"""
	parser = GlobalOptionsParser(usage=usage)
	parser.add_option("-v", "--amisversion", dest="amis_version", type="string", default="3.1", 
		help="Target version of AMIS (default = 3.1)")
	parser.add_option("-y", "--tmp", dest="tmp", default=False, action="store_true", help="Save output files in /tmp")
	parser.add_option("-x", "--all", dest="all", default=False, action="store_true", help="Export all languages")
	parser.add_option("-l", "--langid", dest="langid", default="", 
		help="language ID")
	parser.add_option("-z", "--custom", dest="custom", default="", help="a comma-separated list of language IDs")
    
	(options, args) = parser.parse_args()
	parser.check_args(1, args)
	langpacks_dir = args[0]
    
	session = LionDB(options.config, options.trace, "amis")
	
	# export all languages (see LANGS list above)
	if options.all == True:
		for l in LANGS:
			process_one(l, langpacks_dir, options, session)
	# export one language		
	else:
	    if options.custom != "":
	        custom_langs = options.custom.split(",")
	        for l in custom_langs:
	            process_one(l.strip(), langpacks_dir, options, session)
	    else:
	        if options.langid != "":
	            process_one(options.langid, langpacks_dir, options, session)
	        else:
	            session.die("No lang ID specified.  Use --all, --custom, or --langid to specify all, a custom set, or a single language.")
	            return


def process_one(langid, langpacks_dir, options, session):
	langdir = find_language_directory(langid, langpacks_dir)
	if langdir == "":
		session.warn("Cannot process *%s*: not found in %s" % (langid, langpacks_dir))
	if options.tmp == True:
		output_dir = "/tmp/%s" % langid
	else: 
		output_dir = langdir
	export_one(langid, langdir, output_dir, options.amis_version, session)

def find_language_directory(langid, langpacks_dir):
	"""look in the parent langpacks directory for the subdir 
	containing a file named moduleDesc.xml that has id=LANGID in it. 
	return the full path to the subdir"""
	
	flist = []
	for root, dirs, files in os.walk(langpacks_dir):
		if "moduleDesc.xml" in files:
			flist.append(os.path.join(root, "moduleDesc.xml"))
		if '.svn' in dirs:
			dirs.remove('.svn')  # don't visit subversion directories
	
	idstr = "id=\"%s\"" % langid
	for f in flist:
		q = open(f)
		data = q.read() # these files are small so it doesn't hurt to read the whole file at once
		q.close()
		if re.search(idstr, data):
			return os.path.dirname(f)
	return ""
	
def export_one(langid, langdir, output_dir, amis_version, session):
	"""export all the files from the LION"""
	rc_filename = os.path.join(output_dir, "AmisLangpack/AmisLangpack.rc")
	xml_filename = os.path.join(output_dir, "amisAccessibleUi.xml")
	keys_book_dir = os.path.join(output_dir, "shortcuts")
	local_audio_dir = os.path.join(langdir, "audio")
	
	if not os.path.exists(output_dir) or not os.path.isdir(output_dir):
		os.mkdir(output_dir)
	if not os.path.exists(keys_book_dir) or not os.path.isdir(keys_book_dir):
		os.mkdir(keys_book_dir)
	tmp = os.path.join(output_dir, "AmisLangpack")
	if not os.path.exists(tmp) or not os.path.isdir(tmp):
		os.mkdir(tmp)
	
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

if __name__=="__main__": main()


