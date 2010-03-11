from xml.dom import minidom
import os
import datetime

class LionDBAudioMixIn():
    def accept_all_temp_audio(self, langid):
        """copy the audio uris from the tempaudio table to the permanent table for the given language.
        note that the file copying must be done by hand."""
        request = """SELECT xmlid FROM tempaudio WHERE langid="%s" """ % langid
        self.execute_query(request)
        for row in self.cursor.fetchall():
            self.accept_temp_audio(langid, row[0])
    
    def clear_all_temp_audio(self, langid):
        """clear all rows in the tempaudio table for the given language"""
        request = """DELETE FROM tempaudio WHERE langid="%s" """ % langid
        self.execute_query(request)
    
    def accept_temp_audio(self, langid, xmlid):
        """copy a single audio uri from the tempaudio table to the permanent language table
        note that the file copying must be done by hand."""
        request = """SELECT audiouri FROM tempaudio WHERE xmlid="%s" and langid="%s" """ \
            % (xmlid, langid)
        self.execute_query(request)
        if self.cursor.rowcount == 0:
            self.warn("No audio found.")
            return
        
        audio_dir_prefix = self.config["main"]["audio_dir_prefix"]
        if not audio_dir_prefix.endswith("/"): audio_dir_prefix += "/"
        audiofile = audio_dir_prefix + os.path.basename(self.cursor.fetchone()[0])
        self.trace_msg("Saving audio to language table as %s" % audiofile)    
        request = """UPDATE %s SET audiouri="%s" WHERE xmlid="%s" """ \
            % (self.make_table_name(langid), audiofile, xmlid)
        self.execute_query(request)
        self.clear_temp_audio(langid, xmlid)
    
    def clear_temp_audio(self, langid, xmlid):
        """clear a single row from the tempaudio table for the given language"""
        request = """DELETE FROM tempaudio WHERE xmlid="%s" and langid="%s" """ \
            % (xmlid, langid)
        self.execute_query(request)
    
    def import_audio_prompts(self, langid, ncx, audio_is_temporary=False, simulate_only=False):
        """Fill up the database with prompts file names. We use the NCX file
        from the Obi export and match the navPoint text label with textstrings
        in the DB."""
        self.trace_msg("Getting audio prompts from NCX")
        try:
            dom = minidom.parse(ncx)
        except Exception, e:
            self.die("""Couldn't open "%s" (%s)""" % (ncx, e))
        self.execute_query("SELECT xmlid, textstring FROM " +
                self.make_table_name(langid))
        db_items = self.cursor.fetchall()
        xml_labels = dom.getElementsByTagNameNS(
            "http://www.daisy.org/z3986/2005/ncx/", "navLabel")
        self.trace_msg("Got %d labels for %d strings" %
            (xml_labels.__len__(), db_items.__len__()))
        count = 0
        warnings = []
        for xml_label, db_item in zip(xml_labels, db_items):
            count+=1
            db_xmlid = db_item[0]
            db_text = db_item[1]
            xml_text = xml_label.getElementsByTagNameNS(
                "http://www.daisy.org/z3986/2005/ncx/", "text")[0].firstChild.data
            xml_audio_src = xml_label.getElementsByTagNameNS(
                "http://www.daisy.org/z3986/2005/ncx/", "audio")[0].getAttribute("src")
            if xml_text == db_text and xml_audio_src != "":
                if simulate_only == True:
                    self.trace_msg("Found audio for xmlid=%s: %s (%s)" % (db_xmlid, xml_audio_src, db_text))
                else:
                    # if we're writing permanent audio uris to the language table
                    if audio_is_temporary == False:
                        audio_dir_prefix = self.config["main"]["audio_dir_prefix"]
                        if not audio_dir_prefix.endswith("/"): audio_dir_prefix += "/"
                        xml_audio_src = audio_dir_prefix + xml_audio_src
                        self.execute_query("""UPDATE %s SET audiouri="%s" WHERE xmlid="%s" """ %
                            (self.make_table_name(langid), xml_audio_src, db_xmlid))
                
                    # or we're writing to the temp audio table
                    else:
                        a, b = self.get_tempaudio_paths(langid)
                        self.write_tempaudio(db_xmlid, langid, b + xml_audio_src)
            
            else:
                self.warn("""At item #%d, id=%s, no match between db string and ncx label\n*%s*\n*%s*\n""" %
                        (count, db_xmlid, db_text, xml_text))
                warnings.append((db_xmlid, xml_audio_src, db_text, xml_text))
        return warnings

    def write_tempaudio(self, xmlid, langid, file):
        # update the tempaudio table
        # does this have an entry already?
        request = """SELECT id FROM tempaudio WHERE xmlid="%s" and langid="%s" """ % \
            (xmlid, langid)
        self.execute_query(request)
        # if so, just update it
        if self.cursor.rowcount > 0:
            request = """UPDATE tempaudio SET audiouri="%(audiouri)s" WHERE 
                xmlid="%(xmlid)s" AND langid="%(langid)s" """  % \
                {"audiouri": file, "xmlid": xmlid, "langid": langid}
        # otherwise create a new entry
        else:
            request = """INSERT INTO tempaudio (audiouri, xmlid, langid) VALUES
                ("%(audiouri)s", "%(xmlid)s", "%(langid)s" ) """ % \
                {"audiouri": file, "xmlid": xmlid, "langid": langid}
        self.execute_query(request)

    def get_tempaudio_paths(self, langid):
        temp_audio_dir = self.config["main"]["temp_audio_dir"]
        temp_audio_uri = self.config["main"]["temp_audio_uri"]
        
        # calculate the filesystem path to the temporary file storage
        if not temp_audio_dir.endswith("/"): temp_audio_dir += "/"
        save_to_dir =  temp_audio_dir + langid + "/"

        # this is the URI used to read the temporary file back from the web server
        # we'll link to the temp file until it gets integrated into the permanent fileset (done manually for now)
        if not temp_audio_uri.endswith("/"): temp_audio_uri += "/"
        www_dir = temp_audio_uri + langid + "/"
        return save_to_dir, www_dir
    
    def generate_audio(self, langid, dir):
        """Generate all the audio prompts. This needs to be run on a computer with a TTS that can be invoked via command line.
        Here we use the "say" command on OSX.  All files must be uploaded to SVN manually. """
        
        # get all the prompts
        table = self.make_table_name(langid)
        self.execute_query("SELECT xmlid, textstring FROM " + table)
        strings = self.cursor.fetchall()
        
        os.popen("mkdir %s" % dir)
        os.popen("rm -rf %s*.aiff" % dir)
        
        for s in strings:
            # adjust the text, make an audio recording, and add the filename to the DB
            xmlid, text = s
            filename = "%s_%s" % (langid, xmlid)
            outfile = dir + filename
            outfile_web = "./audio/" + filename
            tempfile = dir + "tempaudio"
            
            text1 = self.correct_pronunciation(text)
            if (text1 != text):
                print "%s ==> %s" % (text, text1)
            text = text1
            # record the TTS
            os.popen("""say -o %s.aiff "%s" """ % (tempfile, text))
            #convert to MP3        
            os.popen("""lame %s.aiff %s.mp3""" % (tempfile, outfile))
            os.popen("""rm -rf %s.aiff""" % tempfile)
            # todo: trim the file.  sox will do it, but it cuts it too close to the end
            # for now, we will use audacity externally
            # see http://groups.google.com/group/linux.debian.bugs.dist/browse_thread/thread/a5bbb6588cd77634
            
            self.execute_query("""UPDATE %s SET audiouri="%s.mp3" WHERE xmlid="%s" """ % (table, outfile_web, xmlid))
            print text
            print xmlid
            print ""
    
    def correct_pronunciation(self, text):
        """return a version of the text formatted for use with OSX TTS"""
        text_mod = text.replace("DAISY", "Daisy")
        text_mod = text_mod.replace("OK", "okay")
        text_mod = text_mod.replace("AMIS", "[[inpt PHON]]_AO+mIY>.[[inpt TEXT]]")
        text_mod = text_mod.replace("Max.", "Maximum")
        text_mod = text_mod.replace("Copyright (c) ", "Copyright ")
        text_mod = text_mod.replace("Ctrl", "Control")
        text_mod = text_mod.replace("%s", "")
        text_mod = text_mod.replace("++", "plus plus")
        text_mod = text_mod.replace("+-", "plus minus")
        return text_mod
        
    def archive_audio(self, langid, audio_dir, svn=False):
        """move unreferenced audio clips from audio_dir into a subfolder"""
        # this conflicts with minidom
        import pysvn
        
        # create an svn client
        if svn == True: 
            svn_client = pysvn.Client()
        
        # make a directory for the archived unused files
        folder = "../unused_audio_" + str(datetime.date.today())
        subdir = os.path.join(audio_dir, folder)
        if not os.path.exists(subdir) or not os.path.isdir(subdir):
            os.mkdir(subdir)
        
        # find a list of audio uris that are in use
        table = self.make_table_name(langid)
        self.execute_query("SELECT audiouri FROM " + table)
        strings = self.cursor.fetchall()
        # adjust the list
        db_filelist = []
        for s in strings:
            f = s[0]
            if f != None:
                db_filelist.append(f.replace("./audio/", ""))
        
        disk_filelist = []
        # get a list of all audio files in the directory
        for f in os.popen("""ls %s*mp3""" % audio_dir):
            audio_file = f.replace("\n", "")
            audio_file = os.path.basename(audio_file) 
            disk_filelist.append(audio_file)
        
        # first make sure that all the required audio files are there
        for f in db_filelist:
            if f not in disk_filelist:
                self.warn("DB file reference %s not found in physical directory" % (f, ))
        
        count_unused = 0
        count_used = 0
        # check the disk filelist against the database filelist
        # move unreferenced files to a subdirectory
        for f in disk_filelist:
            # the full path (disk_filelist has only filenames for easy comparison against the db)
            disk_file = os.path.join(audio_dir, f)
            if f not in db_filelist:
                count_unused+=1
                # remove the end of line character from the file name
                instr = """cp "%s" "%s" """ % (disk_file, subdir)
                os.popen(instr)
                # optionally reflect the changes in subversion
                if svn == True:
                    svn_client.remove(disk_file)
                else:
                    instr = """rm "%s" """ % disk_file
                    os.popen(instr)
            else:
                count_used += 1
        
        if svn == True:
            svn_client.add(subdir)
            svn_client.checkin(audio_dir, "DAISY Lion audio archiving: moved unreferenced files to %s" % subdir)
        
        self.trace_msg("%d unused files moved to %s; %d files currently in use" % (count_unused, subdir, count_used))
        
    def import_audio_by_number(self, langid, audio_dir):
        # make sure each ID has an audio file 
        table = self.make_table_name(langid)
        self.execute_query("SELECT xmlid FROM " + table)
        rows = self.cursor.fetchall()
        count_found = 0
        count_not_found = 0
        for r in rows:
            id = r[0]
            f = "%s.mp3" % id
            disk_file = os.path.join(audio_dir, f)
            if os.path.isfile(disk_file) == True:
                # add the file reference to the DB
                # but make sure it's a relative path.  we can assume the form of ./audio/file.mp3
                audiouri = "./audio/%s" % f
                self.execute_query("""UPDATE %s SET audiouri="%s" WHERE xmlid="%s" """ % 
                    (table, audiouri, id))
                count_found += 1
            else:
                count_not_found += 1
        
        self.trace_msg("Audio imported for %s" % langid)
        self.trace_msg("Added %d references; did not find references for %d items" % 
            (count_found, count_not_found))
    
    def check_audio(self, langid, audio_dir):
        """are all DB-referenced audio clips existing?"""
        # find a list of audio uris that are in use
        table = self.make_table_name(langid)
        self.execute_query("SELECT xmlid, audiouri FROM " + table)
        strings = self.cursor.fetchall()
        # adjust the list
        db_filelist = []
        for s in strings:
            f = s[1]
            if f != None:
                db_filelist.append((s[0], f.replace("./audio/", "")))
        
        disk_filelist = []
        # get a list of all audio files in the directory
        for f in os.popen("""ls %s*mp3""" % audio_dir):
            audio_file = f.replace("\n", "")
            audio_file = os.path.basename(audio_file) 
            disk_filelist.append(audio_file)
        
        missing_file_count = 0
        # first make sure that all the required audio files are there
        for id,f in db_filelist:
            if f not in disk_filelist:
                self.warn("DB file reference %s not found in physical directory (id=%s)" % (f,id))
                missing_file_count += 1
        
        count_unused = 0
        count_used = 0
        # check the disk filelist against the database filelist
        for f in disk_filelist:
            # the full path (disk_filelist has only filenames for easy comparison against the db)
            disk_file = os.path.join(audio_dir, f)
            if f not in [f for id, f in db_filelist]:
                count_unused+=1
            else:
                count_used += 1
        
            
        self.execute_query("SELECT xmlid, textstring FROM %s WHERE audiouri is null" % table)
        missing_audio = self.cursor.fetchall()
        missing_audio_count = 0
        for xmlid, textstring in missing_audio:
            self.warn("Missing audio entries in the DB for *%s* (id = %s)" % (textstring, xmlid))
            missing_audio_count += 1
        
        print "===========\n==Summary=="
        print "%d unused files found; %d files currently in use" % (count_unused, count_used)
        if count_unused > 0:
            print "Suggest to run archive_audio.py script to move unused files out of the way."
        
        print "Missing audio entries in the DB for %d items" % missing_audio_count
        print "Missing physical files for %d items" % missing_file_count
    

def clean_audio_file_names(self, langid, audiodir):
    """rename audio files, removing unacceptable characters.
    uses the language table, not the tempaudio table"""
    return
