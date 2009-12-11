class LionDBUserLangMgmtMixIn():
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
        self.__remove_user_from_database(username)
    
    def get_user_info(self, langid):
        """get information about the user for this language"""
        request = """SELECT users.realname, users.username, users.password, users.email,
        users.lastlogin, languages.langname from users, languages 
        where users.langid="%(langid)s" and languages.langid="%(langid)s" """ % \
        {"langid": langid}
        self.execute_query(request)
        return self.cursor.fetchone()
    
    
    def add_language(self, langid, langname, username, password, realname,
        email, mnemonics, accelerators, langid_short):
        """Add a new language and a user for that language"""
        if self.check_language(langid) != False:
            self.die("Language already exists.")
            return

        if self.check_username(username) != False:
            self.die("Username already exists.")
            return

        self.__add_language_to_database(langid, langname, username, password,
            realname, email,
            self.__get_app_value(mnemonics, "translate_mnemonics"),
            self.__get_app_value(accelerators, "translate_accelerators"),
            langid_short)


    def remove_language(self, langid):
        """Remove a language and the user associated with it"""
        if self.check_language(langid) == False:
            self.die("Language not found.")
            return
        self.__remove_language_from_database(langid)
        self.trace_msg("Language %s deleted!" % langid)

    def list_all_languages(self, order_by_login_time = False, order_by_work_todo = False):
        """list all languages and their associated users.
        option to put the last-logged-in user first or to order by the amount of remaining work.
        otherwise in alpha order by langid."""
        
        if order_by_work_todo == True:
            all_langs = self.list_all_languages()
            todo = []
            for l in all_langs:
                work = self.get_number_todo(l[0]) + self.get_number_new(l[0])
                todo.append(work)
            # sort the all_langs list according to the values in todo
            combined = zip(todo, all_langs)
            combined.sort(reverse=True)
            return combined
            
        if order_by_login_time == True:
            request = """SELECT languages.langid, languages.langname, users.realname, users.username, users.password, 
                users.lastlogin FROM languages LEFT OUTER JOIN users ON users.langid=languages.langid 
                ORDER BY users.lastlogin DESC"""
            self.execute_query(request)        
            return self.cursor.fetchall()
            
        # the default case
        request = """SELECT languages.langid, languages.langname, users.realname, users.username, users.password 
            FROM languages LEFT OUTER JOIN users ON users.langid=languages.langid ORDER BY users.langid"""  
        self.execute_query(request)
        return self.cursor.fetchall()
    
    def list_langtable_diffs(self, langid1, langid2):
        """see if one table is longer than the other, and return a list of A not in B"""
        table1 = self.make_table_name(langid1)
        table2 = self.make_table_name(langid2)
        
        request = "SELECT (SELECT count(*) from %s) - (SELECT count(*) from %s) AS diff_rows" % (table1, table2)
        self.execute_query(request)
        diff = self.cursor.fetchone()[0]
        if diff == 0:
            return None
        elif diff < 0:
            longer = table2
            shorter = table1
        else:
            longer = table1
            shorter = table2
        
        request = """SELECT %(longer)s.xmlid, %(longer)s.textstring from %(longer)s 
            LEFT JOIN %(shorter)s ON %(shorter)s.xmlid = %(longer)s.xmlid 
            WHERE %(shorter)s.xmlid is NULL""" % {"longer": longer, "shorter": shorter}
        self.execute_query(request)
        return (self.make_id_from_table_name(longer), self.make_id_from_table_name(shorter),
            self.cursor.fetchall())
    
    def get_new_todo(self, langid):
        """return the xmlid, textstring, and status of items marked new/todo"""
        table = self.make_table_name(langid)
        request = "SELECT xmlid, textstring, status FROM %s WHERE status > 1" % table
        self.execute_query(request)
        return self.cursor.fetchall()
    
    def get_number_todo(self, langid):
        """get the number of items marked TODO"""
        return self.__get_count_by_status(langid, 2)
        
    def get_number_complete(self, langid):
        """get the number of items marked DONE"""
        return self.__get_count_by_status(langid, 1)
        
    def get_number_new(self, langid):
        """get the number of items marked NEW"""
        return self.__get_count_by_status(langid, 3)
    
    def __get_count_by_status(self, langid, status):
        table = self.make_table_name(langid)
        request = "SELECT count(*) FROM %s WHERE STATUS=%d" % (table, status)
        self.execute_query(request)
        return self.cursor.fetchone()[0]
        
    def __add_language_to_database(self, langid, langname, username, password,
        realname, email, mnemonics, accelerators, langid_short):
        """add the new language and new user"""
        # add the language to the languages table
        if langid_short == None:
            self.execute_query("""INSERT INTO languages
            (langid, langname, translate_mnemonics, translate_accelerators)
            VALUES ("%(id)s", "%(name)s", %(mnemonics)s, %(accelerators)s)"""\
                % {"id": langid, "name": langname, "mnemonics": mnemonics,
                    "accelerators": accelerators})
        else:
            self.execute_query("""INSERT INTO languages
            (langid, langid_short, langname, translate_mnemonics,
            translate_accelerators)
            VALUES ("%(id)s", "%(short)s", "%(name)s", %(mnemonics)s,
            %(accelerators)s)"""\
                % {"id": langid, "short": langid_short, "name": langname,
                    "mnemonics": mnemonics, "accelerators": accelerators})

        self.__add_user_to_database(langid, username, password, realname, email)

        # create the new table as a copy of the master language table
        table = self.make_table_name(langid)
        self.execute_query("CREATE TABLE %s SELECT * from %s" % (table, self.get_masterlang_table()))
        # make sure the id column is still the primary key
        self.execute_query("""ALTER TABLE %s MODIFY COLUMN id 
            INT UNSIGNED NOT NULL AUTO_INCREMENT FIRST, ADD PRIMARY KEY(id)""" % table)
        
        # flag all "TODO" and clear some fields
        self.execute_query("UPDATE %s SET status=3, audiouri=NULL, remarks=NULL" % table)

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
        
        #clear any entries in the tempaudio table that use this langid
        self.execute_query("""DELETE FROM tempaudio WHERE langid="%s" """ % langid)
    
    def __add_user_to_database(self, langid, username, password, realname, email):
        """add user to the users table.  their associated language should already exist"""
        self.execute_query("""INSERT INTO users (username, realname, password, \
            email, langid) VALUES ("%(u)s", "%(r)s", "%(p)s", "%(e)s", "%(lid)s")""" \
            % {"u": username, "r": realname, "p": password, "e": email, "lid": langid})    

    def __remove_user_from_database(self, username):
        """remove a user but not their language"""
        self.execute_query("""DELETE FROM users WHERE username="%s" """ % username)

    def __get_app_value(self, initial, field):
        """Get the default application value for a field and return it if
        the initial value is None; otherwise, return the supplied initial
        value."""
        if initial == None:
            self.execute_query("SELECT %s FROM application WHERE appid='%s'" \
                % (field, self.config["main"]["target_app"]))
            value, = self.cursor.fetchone()
            self.trace_msg("Using default value %s for %s" % (value, field))
            return value
        else:
            self.trace_msg("Using supplied value %s for %s" % (initial, field))
            return initial
