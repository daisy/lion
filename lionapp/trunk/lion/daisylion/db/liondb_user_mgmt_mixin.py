class LionDBUserMgmtMixIn():
    def add_user(self, langid, username, password, realname, email):
        """Add a user for an existing language"""
        if self.check_language(langid) == False:
            self.die("Language does not exist")
            return

        if self.check_username(username) != False:
            self.die("Username already exists")
            return

        self.__add_user_to_database(langid, username, password, realname, email)

    def remove_user(self, username):
        """Remove a user but not their language"""
        if self.check_username(username) == False:
            self.die("User does not exist")
            return

        # safety check
        can_remove = self.force
        if self.force == False:
            rly = raw_input("Do you REALLY want to remove a user?  Type your answer (yes/no) ")
            if rly == "yes":
                can_remove = True
            else:
                can_remove = False

        if can_remove == True:    
            self.__remove_user_from_database(username)    

    def add_language(self, langid, langname, username, password, realname, email):
        """Add a new language and a user for that language"""
        if self.check_language(langid) != False:
            self.die("Language already exists.")
            return

        if self.check_username(username) != False:
            self.die("Username already exists.")
            return

        self.__add_language_to_database(langid, langname, username, password, realname, email)


    def remove_language(self, langid):
        """Remove a language and the user associated with it"""
        if self.check_language(langid) == False:
            self.die("Language not found.")
            return

        # safety check
        can_remove = self.force
        if self.force == False:
            rly = raw_input("Do you REALLY want to remove a language?  This is serious.\n \
                Type your answer (definitely/no)  ")
            if rly == "definitely":
                can_remove = True
            else:
                can_remove = False
        # really delete it!
        if can_remove == True:
            self.__remove_language_from_database(langid)
            self.trace_msg("Language %s deleted!" % langid)


    def __add_language_to_database(self, langid, langname, username, password, realname, email):
        """add the new language and new user"""
        # add the language to the languages table
        self.execute_query("""INSERT INTO languages (langid, langname) VALUES \
            ("%(id)s", "%(name)s")""" % {"id": langid, "name": langname})

        self.__add_user_to_database(langid, username, password, realname, email)

        # create the new table as a copy of the master language table
        table = self.make_table_name(langid)
        self.execute_query("CREATE TABLE %s SELECT * from %s" % (table, self.get_masterlang_table()))

        # flag all "TODO" and clear some fields
        self.execute_query("UPDATE %s SET textflag=3, audioflag=2, \
            audiodata=NULL, audiouri=NULL, remarks=NULL" % table)

    def __remove_language_from_database(self, langid):
        """remove the language from the database"""
        # remove the user for this language
        self.execute_query("""SELECT username FROM users WHERE langid="%s" """ % langid)
        user = self.cursor.fetchone()
        self.__remove_user_from_database(user)

        # remove the entry in the languages table
        self.execute_query("""DELETE FROM languages WHERE langid="%s" """ % langid)

        # drop the table with the language data
        table = self.make_table_name(langid)
        self.execute_query("""DROP TABLE %s""" % table)

    def __add_user_to_database(self, langid, username, password, realname, email):
        """add user to the users table.  their associated language should already exist"""
        self.execute_query("""INSERT INTO users (username, realname, password, \
            email, langid) VALUES ("%(u)s", "%(r)s", "%(p)s", "%(e)s", "%(lid)s")""" \
            % {"u": username, "r": realname, "p": password, "e": email, "lid": langid})    

    def __remove_user_from_database(self, username):
        """remove a user but not their language"""
        self.execute_query("""DELETE FROM users WHERE username="%s" """ % username)
        
