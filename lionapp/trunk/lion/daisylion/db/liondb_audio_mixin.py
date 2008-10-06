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
    
    def import_audio_prompts(self, langid, ncx):
        """Fill up the database with prompts file names. We use the NCX file
        from the Obi export and match the navPoint text label with textstrins
        in the DB."""
        self.trace_msg("Getting audio prompts from NCX")
        try:
            dom = minidom.parse(ncx)
        except Exception, e:
            self.die("""Couldn't open "%s" (%s)""" % (ncx, e))
        self.execute_query("SELECT id, textstring FROM " +
                self.make_table_name(langid))
        strings = self.cursor.fetchall()
        labels = dom.getElementsByTagNameNS(
            "http://www.daisy.org/z3986/2005/ncx/", "navLabel")
        self.trace_msg("Got %d labels for %d strings" %
            (labels.__len__(), strings.__len__()))
        for label, string in zip(labels, strings):
            text = label.getElementsByTagNameNS(
                "http://www.daisy.org/z3986/2005/ncx/", "text")[0].firstChild.data
            audio_src = label.getElementsByTagNameNS(
                "http://www.daisy.org/z3986/2005/ncx/", "audio")[0].getAttribute("src")
            if string[1] == text and audio_src != "":
                self.execute_query("""UPDATE %s SET audiouri="%s", audioflag=1 WHERE id=%d""" %
                        (self.make_table_name(langid), audio_src, string[0]))
            else:
                self.warn("""No match between db string="%s" and ncx label="%s"?!""" %
                        (string[1], text))

