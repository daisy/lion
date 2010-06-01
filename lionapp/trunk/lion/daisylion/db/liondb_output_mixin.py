class LionDBOutputMixIn():
    def textstrings(self, langid):
        """Export all textstrings to stdout.  Exclude mnemonic and accelerator items."""
        self.trace_msg("Export all text strings to stdout")
        table = self.make_table_name(langid)
        self.execute_query("""SELECT xmlid, textstring FROM """ + table + """
            where (role="STRING" or role="MENUITEM" or role="DIALOG" or \
            role="CONTROL") and translate=1""")
        strings = self.cursor.fetchall()
        return self.__stringlist_to_xml(strings, langid)
    
    def all_strings(self, langid, start_index=0, end_index=-1):
        """Export all strings to stdout"""
        self.trace_msg("Export all strings to stdout")
        table = self.make_table_name(langid)
        self.execute_query("SELECT xmlid, textstring FROM " + table)
        strings = self.cursor.fetchall()
        if end_index == -1: 
            end_idx = len(strings)
        else:
            end_idx = end_index
        return self.__stringlist_to_xml(strings[start_index:end_idx], langid)
    
    def all_strings_length(self, langid):
        """return the length of the number of strings in the list of all strings"""
        table = self.make_table_name(langid)
        self.execute_query("SELECT xmlid, textstring FROM " + table)
        return self.cursor.rowcount
    
    def all_strings_bilingual(self, langid):
        """return all strings and also the corresponding string in the master lang table"""
        request = """SELECT %(master)s.textstring, %(translation)s.textstring 
        FROM %(master)s, %(translation)s  
        WHERE %(master)s.xmlid = %(translation)s.xmlid""" % \
        {"master": self.get_masterlang_table(), "translation": self.make_table_name(langid)}
        self.execute_query(request)
        return self.cursor.fetchall()
    
    def __stringlist_to_xml(self, results, langid):
        """Get all strings that have the given roles"""
        output = """<?xml version="1.0"?>\n<strings langid=\"""" + langid + "\">"
        for item in results:
            id_attr = ""
            if item[0] != None and item[0] != "":
                id_addr = """ id=\"%s\"""" % item[0].encode("utf-8")
            if item[1] != None and item[1] != "":    
                output += """<s%s>%s</s>""" % (id_addr, item[1].encode("utf-8"))
            else:
                output += """<s%s>%s</s>""" % (id_addr, "TODO!")
        output += "</strings>"
        return output
    
