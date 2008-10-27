import os
from daisylion.db.liondb import *
import codecs
import amisxml
import fill_rc
import keys_book
import templates.AmisRCTemplate
from xml.dom import minidom, Node

def export_xml(session, file, langid):
    session.trace_msg("XML Export for %s to %s" % (langid, file))
    # use our dom instead
    minidom.Document = amisxml.AmisUiDoc
    doc = minidom.parse(file)
    doc.set_session(session)
    if doc == None:
        session.die("Document could not be parsed.")
    
    table = session.make_table_name(langid)
    session.execute_query("SELECT xmlid, textstring, actualkeys, role, audiouri FROM %s" % table)
    
    for xmlid, textstring, actualkeys, role, audiouri in session.cursor:
        if audiouri == None:
            audiouri = ""
        elm = doc.get_element_by_id("text", xmlid)
        if elm == None: 
            session.warn("Text element %s not found." % xmlid)
            continue
        
        if elm.firstChild.nodeType == Node.TEXT_NODE:
            if role == "ACCELERATOR":
                elm.firstChild.data = textstring
                elm.parentNode.setAttribute("keys", actualkeys)
            else:
                elm.firstChild.data = textstring.strip()
            audio_elm = doc.get_audio_sibling(elm)
            if audio_elm != None:
                audio_elm.setAttribute("src", audiouri)
                audio_elm.setAttribute("from", "")
        else:
            session.warn("Text element %s has no contents." % xmlid)
    docstring = doc.toxml()
    if docstring != None:
        return doc.toxml().encode("utf-8")
    else:
        return ""

def export_rc(session, langid):
    # these are template keywords
    # the microsoft #xyz statements had to be replaced with $ms_xyz in the template
    # because "#" is a special character for cheetah (the templating system)
    session.trace_msg("RC Export for %s" % (langid))
    msterms = {"ms_include": "#include",
        "ms_define": "#define",
        "ms_if": "#if",
        "ms_ifdef": "#ifdef", 
        "ms_ifndef": "#ifndef",
        "ms_endif": "#endif",
        "ms_undef": "#undef",
        "ms_pragma": "#pragma",
        "ms_else": "#else"}
    
    rc = fill_rc.FillRC(session, langid)
    t = templates.AmisRCTemplate.AmisRCTemplate(searchList=msterms)
    t.rc = rc
    return t.respond()

def export_keys_book(session, xmlfile, langid, folder, audio_source_dir):
    """Fill in the templates for the keyboard shortcuts book"""
    session.trace_msg ("Keyboard shortcuts book export for %s" % (langid))
    keys_book.export_keys_book(session, xmlfile, langid, folder)
    session.trace_msg("Saved in %s.  Just add the audio clips!" % folder)

if __name__ == "__main__":
    export_keys_book(None, "", "", "")
