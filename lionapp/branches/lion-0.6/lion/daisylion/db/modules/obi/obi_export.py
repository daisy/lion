from xml.dom import minidom
import re

def export_resx(session, langid, dir):
    """Export strings for the language given by langid to a directory, using
    the original files as templates."""
    dir = re.sub("/$", "", dir)
    session.trace_msg("export_resx %s %s %s" % (session, langid, dir))
    session.execute_query("SELECT xmlid, textstring, role FROM %s" % langid)
    strings = {}
    mnemonics = {}
    for row in session.cursor.fetchall():
        xmlid, textstring, role = row
        m = re.match("\\w:([^:]+):(.+)", xmlid)
        if m:
            file, name = m.groups()
            if role == "STRING":
                if not strings.has_key(file): strings[file] = {}
                strings[file][name] = textstring
    for file in strings.keys():
        path_orig = dir + "/" + file + ".resx"
        path = dir + "/" + file + "." + langid + ".resx"
        session.trace_msg("* %s" % path)
        try:
            doc = minidom.parse(path_orig)
            # index data element by name for easy reference
            datas = dict(map(lambda d: (d.attributes["name"].nodeValue, d),
                doc.getElementsByTagName("data")))
            for name, textstr in strings[file].iteritems():
                session.trace_msg("  + %s=%s" % (name, textstr))
                if datas.has_key(name):
                    data = datas[name]
                    text = doc.createTextNode(textstr)
                    value = data.getElementsByTagName("value")[0]
                    if value.hasChildNodes():
                        value.normalize()
                        value.replaceChild(text, value.firstChild)
                else:
                    session.warn("No data element named %s in %s" %
                        (name, path_orig))
            f = open(path, "w")
            session.trace_msg("Writing %s" % f)
            f.write(doc.toxml())
            f.close()
        except Exception, e:
            session.die("Couldn't export %s (%s)" % (path, e), 1)
