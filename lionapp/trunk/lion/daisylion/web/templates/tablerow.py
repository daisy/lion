#!/usr/bin/env python




##################################################
## DEPENDENCIES
import sys
import os
import os.path
try:
    import builtins as builtin
except ImportError:
    import __builtin__ as builtin
from os.path import getmtime, exists
import time
import types
from Cheetah.Version import MinCompatibleVersion as RequiredCheetahVersion
from Cheetah.Version import MinCompatibleVersionTuple as RequiredCheetahVersionTuple
from Cheetah.Template import Template
from Cheetah.DummyTransaction import *
from Cheetah.NameMapper import NotFound, valueForName, valueFromSearchList, valueFromFrameOrSearchList
from Cheetah.CacheRegion import CacheRegion
import Cheetah.Filters as Filters
import Cheetah.ErrorCatchers as ErrorCatchers

##################################################
## MODULE CONSTANTS
VFFSL=valueFromFrameOrSearchList
VFSL=valueFromSearchList
VFN=valueForName
currentTime=time.time
__CHEETAH_version__ = '2.4.4'
__CHEETAH_versionTuple__ = (2, 4, 4, 'development', 0)
__CHEETAH_genTime__ = 1348528239.652581
__CHEETAH_genTimestamp__ = 'Mon Sep 24 16:10:39 2012'
__CHEETAH_src__ = 'tablerow.tmpl'
__CHEETAH_srcLastModified__ = 'Thu Dec  8 06:01:44 2011'
__CHEETAH_docstring__ = 'Autogenerated by Cheetah: The Python-Powered Template Engine'

if __CHEETAH_versionTuple__ < RequiredCheetahVersionTuple:
    raise AssertionError(
      'This template was compiled with Cheetah version'
      ' %s. Templates compiled before version %s must be recompiled.'%(
         __CHEETAH_version__, RequiredCheetahVersion))

##################################################
## CLASSES

class tablerow(Template):

    ##################################################
    ## CHEETAH GENERATED METHODS


    def __init__(self, *args, **KWs):

        super(tablerow, self).__init__(*args, **KWs)
        if not self._CHEETAH__instanceInitialized:
            cheetahKWArgs = {}
            allowedKWs = 'searchList namespaces filter filtersLib errorCatcher'.split()
            for k,v in KWs.items():
                if k in allowedKWs: cheetahKWArgs[k] = v
            self._initCheetahInstance(**cheetahKWArgs)
        

    def pagenum(self, **KWS):



        ## CHEETAH: generated from #def $pagenum at line 15, col 1.
        trans = KWS.get("trans")
        if (not trans and not self._CHEETAH__isBuffering and not callable(self.transaction)):
            trans = self.transaction # is None unless self.awake() was called
        if not trans:
            trans = DummyTransaction()
            _dummyTrans = True
        else: _dummyTrans = False
        write = trans.response().write
        SL = self._CHEETAH__searchList
        _filter = self._CHEETAH__currentFilter
        
        ########################################
        ## START - generated method body
        
        write(u'''0
''')
        
        ########################################
        ## END - generated method body
        
        return _dummyTrans and trans.response().getvalue() or ""
        

    def respond(self, trans=None):



        ## CHEETAH: main method generated for this template
        if (not trans and not self._CHEETAH__isBuffering and not callable(self.transaction)):
            trans = self.transaction # is None unless self.awake() was called
        if not trans:
            trans = DummyTransaction()
            _dummyTrans = True
        else: _dummyTrans = False
        write = trans.response().write
        SL = self._CHEETAH__searchList
        _filter = self._CHEETAH__currentFilter
        
        ########################################
        ## START - generated method body
        
        # 
        # Template variables:
        # 
        # 	searchList = a row with these fields:
        # 		xmlid, textstring, status, remarks, ref_string, our_remarks, audiouri
        # 
        # 	instructions = what the translator should do
        # 	handler = the function to handle the form submission
        # 	width = the width of the text box for the translation
        # 	height = the height of the text box for the translation
        # 	langid = the id of the language being translated into
        # 	error = error with data input
        # 	audio_support = whether to show the audio upload field
        if VFFSL(SL,"status",True) == 1: # generated from line 18, col 1
            ok = "checked"
            todo = ""
            classattr = "ok"
        elif VFFSL(SL,"status",True) == 2: # generated from line 22, col 1
            todo = "checked"
            ok = ""
            classattr = "todo"
        elif VFFSL(SL,"status",True) == 3: # generated from line 26, col 1
            classattr = "new"
            todo = ""
            ok = ""
        write(u'''<tr>
<form action="save_data" method="POST" enctype="multipart/form-data">
<td width="30%%" valign="top">
\t<p class="refstring">''')
        _v = VFFSL(SL,"ref_string",True) # u'$ref_string' on line 34, col 23
        if _v is not None: write(_filter(_v, rawExpr=u'$ref_string')) # from line 34, col 23.
        write(u'''</p>
''')
        if VFFSL(SL,"our_remarks",True) != None and VFFSL(SL,"our_remarks",True) != "": # generated from line 35, col 2
            write(u'''\t\t<div class="comments">
\t\t\t<p class="instructions">Our remarks:</p>
\t\t\t<p>''')
            _v = VFFSL(SL,"our_remarks",True) # u'$our_remarks' on line 38, col 7
            if _v is not None: write(_filter(_v, rawExpr=u'$our_remarks')) # from line 38, col 7.
            write(u'''</p>
\t\t</div>
''')
        write(u'''</td>
<td id="''')
        _v = VFFSL(SL,"xmlid",True) # u'$xmlid' on line 42, col 9
        if _v is not None: write(_filter(_v, rawExpr=u'$xmlid')) # from line 42, col 9.
        write(u'''" valign="top">
''')
        if VFFSL(SL,"error",True) != None and VFFSL(SL,"error",True) != "": # generated from line 43, col 2
            write(u'''\t\t<p class="error">''')
            _v = VFFSL(SL,"error",True) # u'$error' on line 44, col 20
            if _v is not None: write(_filter(_v, rawExpr=u'$error')) # from line 44, col 20.
            write(u'''</p>
''')
        write(u'''
\t<p class="instructions">''')
        _v = VFFSL(SL,"instructions",True) # u'$instructions' on line 47, col 26
        if _v is not None: write(_filter(_v, rawExpr=u'$instructions')) # from line 47, col 26.
        write(u'''  Remember to <em>Save</em>.</p>
\t<textarea name="translation" cols="''')
        _v = VFFSL(SL,"width",True) # u'$width' on line 48, col 37
        if _v is not None: write(_filter(_v, rawExpr=u'$width')) # from line 48, col 37.
        write(u'''" rows="''')
        _v = VFFSL(SL,"height",True) # u'$height' on line 48, col 51
        if _v is not None: write(_filter(_v, rawExpr=u'$height')) # from line 48, col 51.
        write(u'''" class="''')
        _v = VFFSL(SL,"classattr",True) # u'$classattr' on line 48, col 67
        if _v is not None: write(_filter(_v, rawExpr=u'$classattr')) # from line 48, col 67.
        write(u'''">''')
        _v = VFFSL(SL,"textstring",True) # u'$textstring' on line 48, col 79
        if _v is not None: write(_filter(_v, rawExpr=u'$textstring')) # from line 48, col 79.
        write(u'''</textarea>
    <p>Remarks from you:</p>
\t<textarea class="remarks" name="remarks" cols="64" rows="2">''')
        _v = VFFSL(SL,"remarks",True) # u'$remarks' on line 50, col 62
        if _v is not None: write(_filter(_v, rawExpr=u'$remarks')) # from line 50, col 62.
        write(u'''</textarea>
  <p class="xmlid">''')
        _v = VFFSL(SL,"xmlid",True) # u'$xmlid' on line 51, col 20
        if _v is not None: write(_filter(_v, rawExpr=u'$xmlid')) # from line 51, col 20.
        write(u'''</p>
</td>
''')
        if VFFSL(SL,"self.audio_support",True) == True: # generated from line 53, col 1
            write(u'''<td valign="top">
''')
            if VFFSL(SL,"audiouri",True) != None and len(VFFSL(SL,"audiouri",True)) > 0: # generated from line 55, col 2
                write(u'''\t \t<p><a href="''')
                _v = VFFSL(SL,"audiouri",True) # u'$audiouri' on line 56, col 16
                if _v is not None: write(_filter(_v, rawExpr=u'$audiouri')) # from line 56, col 16.
                write(u'''">Audio (click to play)</a></p>
''')
            write(u'''    Choose an MP3 file:
\t<input type="file" name="audiofile" value="Browse"/>
\t<p class="instructions">''')
            _v = VFFSL(SL,"audionotes",True) # u'$audionotes' on line 60, col 26
            if _v is not None: write(_filter(_v, rawExpr=u'$audionotes')) # from line 60, col 26.
            write(u'''</p>
</td>
''')
        else: # generated from line 62, col 1
            #  a dummy audiofile so as not to alter the function signature
            write(u'''\t<input type="hidden" name="audiofile" value=""/>
''')
        write(u'''<td valign="top">
\t<p>Status:</p>
\t<input name="status" type="radio" ''')
        _v = VFFSL(SL,"ok",True) # u'$ok' on line 68, col 36
        if _v is not None: write(_filter(_v, rawExpr=u'$ok')) # from line 68, col 36.
        write(u''' value="1"/>&nbsp;<span class="ok">OK</span><br/>
\t<input name="status" type="radio" ''')
        _v = VFFSL(SL,"todo",True) # u'$todo' on line 69, col 36
        if _v is not None: write(_filter(_v, rawExpr=u'$todo')) # from line 69, col 36.
        write(u''' value="2"/>&nbsp;<span class="todo">TODO</span><br/>
</td>
<td valign="bottom">
\t<input type="submit" value="Save" style="align: bottom"/>
\t<input type="hidden" name="xmlid" value="''')
        _v = VFFSL(SL,"xmlid",True) # u'$xmlid' on line 73, col 43
        if _v is not None: write(_filter(_v, rawExpr=u'$xmlid')) # from line 73, col 43.
        write(u'''"/>
\t<input type="hidden" name="langid" value="''')
        _v = VFFSL(SL,"langid",True) # u'$langid' on line 74, col 44
        if _v is not None: write(_filter(_v, rawExpr=u'$langid')) # from line 74, col 44.
        write(u'''"/>
\t<input type="hidden" name="pagenum" value="''')
        _v = VFFSL(SL,"pagenum",True) # u'$pagenum' on line 75, col 45
        if _v is not None: write(_filter(_v, rawExpr=u'$pagenum')) # from line 75, col 45.
        write(u'''"/>
</td>
</form>
</tr>
''')
        
        ########################################
        ## END - generated method body
        
        return _dummyTrans and trans.response().getvalue() or ""
        
    ##################################################
    ## CHEETAH GENERATED ATTRIBUTES


    _CHEETAH__instanceInitialized = False

    _CHEETAH_version = __CHEETAH_version__

    _CHEETAH_versionTuple = __CHEETAH_versionTuple__

    _CHEETAH_genTime = __CHEETAH_genTime__

    _CHEETAH_genTimestamp = __CHEETAH_genTimestamp__

    _CHEETAH_src = __CHEETAH_src__

    _CHEETAH_srcLastModified = __CHEETAH_srcLastModified__

    _mainCheetahMethod_for_tablerow= 'respond'

## END CLASS DEFINITION

if not hasattr(tablerow, '_initCheetahAttributes'):
    templateAPIClass = getattr(tablerow, '_CHEETAH_templateClass', Template)
    templateAPIClass._addCheetahPlumbingCodeToClass(tablerow)


# CHEETAH was developed by Tavis Rudd and Mike Orr
# with code, advice and input from many other volunteers.
# For more information visit http://www.CheetahTemplate.org/

##################################################
## if run from command line:
if __name__ == '__main__':
    from Cheetah.TemplateCmdLineIface import CmdLineIface
    CmdLineIface(templateObj=tablerow()).run()


