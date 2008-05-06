# add or remove a language from the database


def add_language(session, langid, langname, username, password, realname, email):
    """Add a new language and a user for that language"""
    if session.check_language(langid) != None:
        session.die("Language already exists.")
        return
    
    if session.check_username(username) != None:
        session.die("Username already exists.")
        return
    
    _add_language_to_database(session, langid, langname, username, password, realname, email)


def remove_language(session, langid, force):
    """Remove a language and the user associated with it"""
    if session.check_language(langid) == None:
        session.die("Language not found.")
        return
    
    # safety check
    can_remove = force
    if force == False:
        rly = raw_input("Do you REALLY want to remove a language?  This is serious.\n \
            Type your answer (definitely/no)  ")
        if rly == "definitely":
            can_remove = True
    
    # really delete it!
    if can_remove == True:
        _remove_language_from_database(session, langid)
        print langid
        session.trace_msg("Language %s deleted!" % langid)

    
def _add_language_to_database(session, langid, langname, username, password, realname, email):
    """add the new language and new user"""
    # add the language to the languages table
    session.execute_query("""INSERT INTO languages (langid, langname) VALUES \
        ("%(id)s", "%(name)s")""" % {"id": langid, "name": langname})
    
    # add user to the users table
    session.execute_query("""INSERT INTO users (username, realname, password, \
        email, langid) VALUES ("%(u)s", "%(r)s", "%(p)s", "%(e)s", "%(lid)s")""" \
        % {"u": username, "r": realname, "p": password, "e": email, "lid": langid})
    
    # create the new table as a copy of the english table
    table = session.make_table_name(langid)
    session.execute_query("CREATE TABLE %s SELECT * from eng_US" % table)
    
    # flag all "TODO" and clear some fields
    session.execute_query("UPDATE %s SET textflag=3, audioflag=3, \
        audiodata=NULL, audiouri=NULL, remarks=NULL" % table)

def _remove_language_from_database(session, langid):
    """remove the language from the database"""
    # remove the user for this language
    session.execute_query("""DELETE FROM users where langid="%s" """ % langid)
    
    # remove the entry in the languages table
    session.execute_query("""DELETE FROM languages WHERE langid="%s" """ \
    % langid)
    
    # drop the table with the language data
    table = session.make_table_name(langid)
    session.execute_query("""DROP TABLE %s""" % table)

