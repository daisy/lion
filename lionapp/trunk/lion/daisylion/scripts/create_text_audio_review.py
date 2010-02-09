from global_options_parser import *
from daisylion.db.liondb import LionDB

HTML5 = """<!doctype html>
<html>
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <title>%(title)s</title></head>
<body>
    <h1>%(lang)s</h1>
    <table style="border: thin black solid">%(table)s</table>
</body>
</html>"""

HTML_TR = """<tr>
    <td  style="border: thin black solid">%(xmlid)s</td>
    <td style="border: thin black solid">%(text)s</td>
    <td style="border: thin black solid; font-style:italic">%(reftext)s<td>
    <td style="border: thin black solid"><audio controls src="file://%(audio)s"/></td>
    <td>%(audiofile)s</td>
</tr>"""

def main():
    usage = """usage: %prog [options] langid localaudiodir"""
    parser = GlobalOptionsParser(usage=usage)
    (options, args) = parser.parse_args()
    parser.check_args(2, args)
    
    session = LionDB(options.config, options.trace, options.app)    
    langid, audiodir = args
    data = session.get_text_audio_data(langid, audiodir)
    
    table = ""
    for reftext, text, audio, xmlid in data:
        row = HTML_TR % {"xmlid": xmlid, "reftext": reftext, "text": text, "audio": audio, "audiofile": os.path.basename(audio)}
        table += row
    
    doc = HTML5 % {"title": "Text and audio data", "lang": langid, "table": table}
    print doc

if __name__=="__main__": main()


