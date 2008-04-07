def import_from_xml(session, doc, langid):
    """Import a document object (from minidom) into a table. The cursor has the
current connection to the database."""
    session.trace_msg("IMPORT FROM OBI.")

def export(session, langid, file):
    session.trace_msg("EXPORT FROM OBI.")
