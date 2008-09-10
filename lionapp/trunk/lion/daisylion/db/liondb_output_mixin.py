class LionDBOutputMixIn():
    def all_strings(self, langid):
        """Export all strings to stdout"""
        self.trace_msg("Export all strings to stdout")
        table = self.make_table_name(langid)
        self.execute_query("""SELECT textstring FROM """ + table + """
            where (role="STRING" or role="MENUITEM" or role="DIALOG" or \
            role="CONTROL") and translate=1""")
        strings = self.cursor.fetchall()
        print self.__stringlist_to_xml(strings, langid)
    
    def textstrings(self, langid):
        """Export all strings to stdout"""
        self.trace_msg("Export strings to stdout")
        table = self.make_table_name(langid)
        self.execute_query("SELECT textstring FROM " + table)
        strings = self.cursor.fetchall()
        print self.__stringlist_to_xml(strings, langid)
    
    def __stringlist_to_xml(self, results, langid):
        """Get all strings that have the given roles"""
        output = """<?xml version="1.0"?>\n<strings langid=\"""" + langid + "\">"
        for item in results:
            output += "<s>" + item[0].encode("utf-8") + "</s>"
        output += "</strings>"
        return output
    
