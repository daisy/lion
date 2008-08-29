The DAISY Lion
==============
For creating and maintaining localized versions of DAISY software products, the DAISY Lion contains the following:

	1. A MySQL database that stores the translation data.  The database name is "lionutf8".
	2. A web interface for users to edit text strings and choose mnemonics and accelerators.  This is in the folder "lionweb".
	3. Scripts for adding new accounts and administering the dataset.  These are in the folder "managedb".
	4. Application-specific modules for database IO.  See "managedb/modules".

How to connect to the database from the shell (assuming your IP has been authorized):
mysql -h92.243.13.151 -u[username] -p[password] -A lionutf8

To run our scripts, you'll need the DB folder, which contains top-secret connection information.  Ask me where to get this.
Make sure the path to the DB folder is on your PYTHONPATH or that you added its path to your sys.path.

Your code looks like this:

from DB.connect import *
#username can be "admin", "rw", "ro" for "admin", "read-write", "read-only"
db = connect_to_db(user, hostname)

user : "admin" (ALL permissions), "ro" (SELECT), "rw" (SELECT/UPDATE/INSERT/DELETE)
hostname : "localhost", "92.243.13.151" (Gandi), or whatever the host IP is

Note that with the current server (Gandi), your IP has to be authorized in order to connect from a local machine.  Do the following:
1. Connect via SSH to 93.243.13.151
2. mysql -uroot -p[secretpassword]
3. GRANT ALL on *.* TO 'yourname'@'yourIP' IDENTIFIED BY 'your_top_secret_password';


THE USERS TABLE

mysql > DESCRIBE users;
+-----------------+--------------+------+-----+---------+-------+
| Field           | Type         | Null | Key | Default | Extra |
+-----------------+--------------+------+-----+---------+-------+
| username        | varchar(20)  | YES  |     | NULL    |       | 
| realname        | varchar(100) | YES  |     | NULL    |       | 
| password        | varchar(20)  | YES  |     | NULL    |       | 
| email           | varchar(50)  | YES  |     | NULL    |       | 
| langid          | varchar(6)   | YES  |     | NULL    |       | 
| langname        | varchar(50)  | YES  |     | NULL    |       | 
| lastlogin       | datetime     | YES  |     | NULL    |       | 
| lastactivity    | datetime     | YES  |     | NULL    |       | 
| svnpath         | varchar(255) | YES  |     | NULL    |       | 
| sessionid       | varchar(36)  | YES  |     | NULL    |       | 
| lastpage        | varchar(11)  | YES  |     | NULL    |       | 
| lastpageoptions | varchar(255) | YES  |     | NULL    |       | 
+-----------------+--------------+------+-----+---------+-------+

Note that table ids cannot be hypenated, so while the language ID will be something like "eng-US", the corresponding table will be called "eng_US"

username:
	The user's login
realname:
	Their real name
password:
	Super-secret password.  Probably unencrypted.
email:
	How to contact this person
langid:
	The language that they're working on.  Uses the hyphenated form like "eng-US"
langname:
	The name of the language that they're working on
lastlogin:
	Date/time of their last login
lastactivity:
	The last time they did anything (useful for timeouts)
svnpath:
	The full path to the svn repository for their language pack
sessionid:
	Their session id
lastpage (DEPRECATED) :
	The last page the user worked on ("main" | "mnemonics" | "accelerators")
lastpageoptions (DEPRECATED) :
	The options for the last page the user worked on (usually the view (all, new, todo) on the main page)

THE LANGUAGE TABLES

mysql > DESCRIBE eng_US;
+---------------+------------------+------+-----+---------+----------------+
| Field         | Type             | Null | Key | Default | Extra          |
+---------------+------------------+------+-----+---------+----------------+
| id            | int(10) unsigned | NO   | PRI | NULL    | auto_increment | 
| textstring    | text             | YES  |     | NULL    |                | 
| audiodata     | longblob         | YES  |     | NULL    |                | 
| audiouri      | varchar(255)     | YES  |     | NULL    |                | 
| textflag      | int(11)          | YES  |     | NULL    |                | 
| audioflag     | int(11)          | YES  |     | NULL    |                | 
| remarks       | text             | YES  |     | NULL    |                | 
| xmlid         | varchar(4)       | YES  |     | NULL    |                | 
| role          | varchar(11)      | YES  |     | NULL    |                | 
| mnemonicgroup | int(11)          | YES  |     | NULL    |                | 
| target        | varchar(4)       | YES  |     | NULL    |                | 
| actualkeys    | varchar(100)     | YES  |     | NULL    |                | 
+---------------+------------------+------+-----+---------+----------------+

Each row represents a text element from the amisAccessibleUi.xml file.

id
	The internal table id, which is managed automatically by the database.
textstring
	The text contents
audiodata (TO BE DEPRECATED) 
	The raw audio data, presumably after having been uploaded by the user
audiouri
	The path to the audiodata, relative to the language's svn directory.  the audiodata gets moved here manually after the translation is done.
textflag
	1 = ok; 2 = todo (marked by the translator); 3 = new (the corresponding english text is new/changed)
audioflag
	1 = ok; 2 = todo (marked by the translator); 3 = new (the corresponding english text is new/changed)
remarks
	Comments from the translator
xmlid
	The id on the text element in the XML file.  Assumed to be unique in the database as well.
role
	One of the following: "ACCELERATOR" | "MNEMONIC" | "MENUITEM" | "CONTROL" | "DIALOG" | "STRING"
mnemonicgroup
	This number gives the group that the mnemonic belongs to (a group is a menu or dialog screen).  Useful for detecting duplicates.
target
	Gives the text id of the item that the mnemonic or accelerator is for
actualkeys
	The programmatic keys for the shortcut or mnemonic.  For example, the textstring would say "Espacio" in Spanish, but the actual key is still "Space"

THE DB MANAGEMENT TOOLS
====
In a folder called "managedb" are tools for adding users/languages, adding/removing/changing master language table strings, exporting strings, and using module functions such as importing from XML or exporting to specific formats.

The commands
-----------

But first, common options for these commands:

application	
	The application module you are using.  E.g. "amis" or "obi"
force
	Force acceptance of drastic actions such as deleting a language account or removing a string from all tables
trace
	Print trace output
file
	A file required by the command
langid
	The ID of the language you want to work with.  Examples: eng-US, hin-IN, spa-ES.  ISO-compliant naming is used.

1. help
Print something vaguely helpful

2. export
Each application module will have its own version of export.  If there is more than one type of export, you can specify which one by using the "option" option.  For example, the AMIS module can export to its own XML format (option 1), a Microsoft RC file (2), or a DAISY book of its keyboard shortcuts (3).

export --application=amis --langid=eng-US --option=2  > data_export

there is another parameter called "extra" that can pass one additional parameter to the module's export function.  

3. import
Import a file.  This is also application module-specific.

import --application=amis --file=myxml.xml --langid=eng-US

4. add_language
Add a language account to the database.  

add_language --langid=abc-YZ --langname="Made up language" --username=abcdefg --password=lmnop --realname="Joe Translator" --email=joe@translators.com

5. remove_language
Remove a language account.  Just supply the langid.

6. remove_item
Remove any entry from the database. The langid is the master language table.  The stringid is the xmlid value of the item to remove.  The item is removed from all tables after it is removed from the master language table.

remove_item --langid=eng-US --stringid=t34

7. add_string
Add a textstring to the master language table, and update all other tables to reflect this.  The new string will be listed in the other tables as a "new" item.  The stringid is the ID for this new item.

add_string --langid=eng-US --text="The new string" --stringid=t999 

8. add_accelerator
Add an accelerator (a keyboard shortcut) to the master language table, and update all other tables to reflect this.  The new accelerator will be listed in the other tables as a "new" item.  

The textstring is the name of the accelerator, and the keys parameter gives the programmatic name of the keys.  The refid is the string ID (xmlid) of the item that this accelerator goes with.  For example, if Space is the accelerator for the Play command, then the refid would be the string id for "Play".  The stringid value here, as in other examples, is the ID for the new accelerator.

add_accelerator --langid=spa-ES --textstring="Espacio" stringid=t999 refid=t34 keys=Space

9. change_item

Change the contents of an item in the master language table.  All other tables will list this item as "to-do".

change_item --langid=eng-US --text="The changed text" --stringid=t44

10. textstrings
Get an XML-formatted list of all the textstrings in the database for a given language.  

textstrings --langid=eng-US

11. all_strings
Get an XML-formatted list of all the strings (textstrings, accelerators, mnemonics) in the database for a given language.

all_strings --langid=eng-US

12. audio_prompts 
Import audio prompts into the database audio file field from the NCX file of a book which contains one prompt per heading.  The text of the NCX must match the text of the database, otherwise this won't work.

audio_prompts --langid=eng-US --file=myfile.ncx
