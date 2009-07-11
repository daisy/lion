from distutils.core import setup
import py2exe

setup( options = {"py2exe": {"packages": ["encodings"]}},
    zipfile = None,
    console = ["lion_audio_helper.py"] )
