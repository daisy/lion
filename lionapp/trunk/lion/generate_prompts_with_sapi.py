# this is a standalone script that can be given to users who want to generate their prompts with SAPI
# the prompts will be in wav format on their computer, named after the IDs of each prompt
"""
Download python 2.6 for windows: http://www.python.org/download/releases/2.6.2/
Go to the DAISY Lion website and login
Choose "Record your prompts with Obi"
Press "Download" to download the list of prompts and save it in the same directory as this script.  Name the file "prompts.html"
Run this script from the command line by typing: python generate_prompts_with_sapi.py
You should now have a folder "audio" with all the prompts as WAV files.
Convert them to MP3 with the tool of your choice.
"""
import sys
import os
from xml.dom import minidom, Node
import subprocess 
# edit this list as necessary by adding new rules formatted exactly like this: (Word, Pronunciation) 
PRONUNCIATION_RULES = (
("AMIS", "ahmee"), 
("Ctrl" "Control")
# add your rule here followed by a comma
)
#end of list

def main():
    doc = minidom.parse("prompts.html")
    for elem in doc.getElementsByTagName("h1"):
        if not elem.firstChild or elem.firstChild.nodeType != Node.TEXT_NODE:
            continue
        textstring = "\"%s\"" % correct_pronunciation(elem.firstChild.wholeText)
        filename = "./audio/%s.wav" % elem.getAttribute("id") 
        os.popen("sapi2wav.exe %s 1 -t %s" % (filename, textstring))


def correct_pronunciation(text):
    """return a version of the text formatted for use with OSX TTS"""
    text_mod = text
    for rule in PRONUNCIATION_RULES:
        text_mod = text_mod.replace(rule[0], rule[1])
    return text_mod
    
if __name__ == "__main__":
    main()