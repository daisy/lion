# this is a standalone script that can be given to users who want to generate their prompts with SAPI
# the prompts will be in wav format on their computer, named after the IDs of each prompt
"""
Run this script from this directory, or compile as an EXE using py2exe.

This script depends on the following files:
prompts.html : an html-formatted list of all prompts.  this file should come from the lion website.
pronunciation.txt : pronunciation rules for the TTS.

This script will read all the headings in prompts.html, apply the pronunciation rules, and use sapi2wav to generate
audio files for all prompts.  The audio files are named for the IDs of the prompts.
"""
import sys
import os
from xml.dom import minidom, Node
import fileinput

PRONUNCIATION_RULES = []

def main():
    # sys.setdefaultencoding may be deleted by site.py,  so bring it back:
    reload(sys)
    if hasattr(sys,"setdefaultencoding"):
        sys.setdefaultencoding("utf-8")
    if os.path.isdir("audio") == False:
        os.mkdir("audio")
    parse_pronunciation_rules()
    doc = minidom.parse("prompts.html")
    for elem in doc.getElementsByTagName("h1"):
        if not elem.firstChild or elem.firstChild.nodeType != Node.TEXT_NODE:
            continue
        tmp = elem.firstChild.wholeText
        textstring = "\"%s\"" % correct_pronunciation(tmp)
        filename = "./audio/%s.wav" % elem.getAttribute("id") 
        print "%s : %s" % (filename, tmp)
        os.popen("sapi2wav.exe %s 1 -t %s" % (filename, textstring))


def correct_pronunciation(text):
    """return a version of the text formatted for use with OSX TTS"""
    text_mod = text
    for rule in PRONUNCIATION_RULES:
        text_mod = text_mod.replace(rule[0], rule[1])
    return text_mod


def parse_pronunciation_rules():
    f = open("pronunciation.txt").read()
    pairs = f.split("#")
    for p in pairs:
        if p != "\n":
            PRONUNCIATION_RULES.append(p.replace("\n", "").split("->"))

    
if __name__ == "__main__":
    main()