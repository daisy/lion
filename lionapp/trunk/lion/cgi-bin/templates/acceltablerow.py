#!/usr/bin/env python




##################################################
## DEPENDENCIES
import sys
import os
import os.path
from os.path import getmtime, exists
import time
import types
import __builtin__
from Cheetah.Version import MinCompatibleVersion as RequiredCheetahVersion
from Cheetah.Version import MinCompatibleVersionTuple as RequiredCheetahVersionTuple
from Cheetah.Template import Template
from Cheetah.DummyTransaction import DummyTransaction
from Cheetah.NameMapper import NotFound, valueForName, valueFromSearchList, valueFromFrameOrSearchList
from Cheetah.CacheRegion import CacheRegion
import Cheetah.Filters as Filters
import Cheetah.ErrorCatchers as ErrorCatchers

##################################################
## MODULE CONSTANTS
try:
    True, False
except NameError:
    True, False = (1==1), (1==0)
VFFSL=valueFromFrameOrSearchList
VFSL=valueFromSearchList
VFN=valueForName
currentTime=time.time
__CHEETAH_version__ = '2.0.1'
__CHEETAH_versionTuple__ = (2, 0, 1, 'final', 0)
__CHEETAH_genTime__ = 1211168791.889348
__CHEETAH_genTimestamp__ = 'Mon May 19 10:46:31 2008'
__CHEETAH_src__ = 'acceltablerow.tmpl'
__CHEETAH_srcLastModified__ = 'Mon May 19 10:38:38 2008'
__CHEETAH_docstring__ = 'Autogenerated by CHEETAH: The Python-Powered Template Engine'

if __CHEETAH_versionTuple__ < RequiredCheetahVersionTuple:
    raise AssertionError(
      'This template was compiled with Cheetah version'
      ' %s. Templates compiled before version %s must be recompiled.'%(
         __CHEETAH_version__, RequiredCheetahVersion))

##################################################
## CLASSES

class acceltablerow(Template):

    ##################################################
    ## CHEETAH GENERATED METHODS


    def __init__(self, *args, **KWs):

        Template.__init__(self, *args, **KWs)
        if not self._CHEETAH__instanceInitialized:
            cheetahKWArgs = {}
            allowedKWs = 'searchList namespaces filter filtersLib errorCatcher'.split()
            for k,v in KWs.items():
                if k in allowedKWs: cheetahKWArgs[k] = v
            self._initCheetahInstance(**cheetahKWArgs)
        

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
        
        write('''
''')
        # 
        # Template variables:
        # 
        # 	searchList = a row with these fields:
        # 		xmlid, textstring, textflag, remarks, ref_string, our_remarks, thekeys, keymask
        # 
        # 	instructions = what the translator should do	
        # 	handler = the function to handle the form submission
        # 	width = the width of the text box for the translation
        # 	height = the height of the text box for the translation
        # 	langid = the id of the language being translated into
        # 	
        # Identical to tablerow except for the dataentry part.This should really be derived from tablerow but it's not working; I suspect because Cheetah #blocks can't have arguments.
        # 
        write('''
''')
        if VFFSL(SL,"textflag",True) == 1: # generated from line 18, col 1
            ok = "checked"
            todo = ""
            classattr = "ok"
        elif VFFSL(SL,"textflag",True) == 2: # generated from line 22, col 1
            todo = "checked"
            ok = ""
            classattr = "todo"
        elif VFFSL(SL,"textflag",True) == 3: # generated from line 26, col 1
            classattr = "new"
            todo = ""
            ok = ""
        write('''<tr>
<form action="save_string" method="POST">
<td width="30%%">''')
        _v = VFFSL(SL,"ref_string",True) # '$ref_string' on line 33, col 18
        if _v is not None: write(_filter(_v, rawExpr='$ref_string')) # from line 33, col 18.
        write('''</td>
<td>
    <p class="comments">''')
        _v = VFFSL(SL,"our_remarks",True) # '$our_remarks' on line 35, col 25
        if _v is not None: write(_filter(_v, rawExpr='$our_remarks')) # from line 35, col 25.
        write('''</p>
    
''')
        #  start of dataentry area
        #  this looks like KEYMASK + small textbox for entering a letter 
        if len(VFFSL(SL,"thekeys",True)) > 0: # generated from line 39, col 2
            write('''\t''')
            _v = VFFSL(SL,"instructions",True) # '$instructions' on line 40, col 2
            if _v is not None: write(_filter(_v, rawExpr='$instructions')) # from line 40, col 2.
            write(''' 
''')
        write('''\tRemember to <em>Save</em>.<br/><br/>
\tShortcut: <span class="''')
        _v = VFFSL(SL,"classattr",True) # '$classattr' on line 43, col 25
        if _v is not None: write(_filter(_v, rawExpr='$classattr')) # from line 43, col 25.
        write('''">''')
        _v = VFFSL(SL,"keymask",True) # '$keymask' on line 43, col 37
        if _v is not None: write(_filter(_v, rawExpr='$keymask')) # from line 43, col 37.
        write('''</span>
''')
        if len(VFFSL(SL,"thekeys",True)) > 0: # generated from line 44, col 2
            write('''\t<textarea id="keys_''')
            _v = VFFSL(SL,"xmlid",True) # '$xmlid' on line 45, col 21
            if _v is not None: write(_filter(_v, rawExpr='$xmlid')) # from line 45, col 21.
            write('''" name="thekeys" cols="5" rows="1" class="''')
            _v = VFFSL(SL,"classattr",True) # '$classattr' on line 45, col 69
            if _v is not None: write(_filter(_v, rawExpr='$classattr')) # from line 45, col 69.
            write('''">''')
            _v = VFFSL(SL,"thekeys",True) # '$thekeys' on line 45, col 81
            if _v is not None: write(_filter(_v, rawExpr='$thekeys')) # from line 45, col 81.
            write('''</textarea>
''')
        write('''\t<br/>
''')
        #  and then another text box for entering the label for the entire shortcut
        write('''\t<p>Now type the human-readable version of the shortcut.  For example, your language might have its own words or abbreviations for Space or Control.</p>
\t<textarea id="''')
        _v = VFFSL(SL,"xmlid",True) # '$xmlid' on line 50, col 16
        if _v is not None: write(_filter(_v, rawExpr='$xmlid')) # from line 50, col 16.
        write('''" name="translation" cols="30" rows="3" class="''')
        _v = VFFSL(SL,"classattr",True) # '$classattr' on line 50, col 69
        if _v is not None: write(_filter(_v, rawExpr='$classattr')) # from line 50, col 69.
        write('''">''')
        _v = VFFSL(SL,"textstring",True) # '$textstring' on line 50, col 81
        if _v is not None: write(_filter(_v, rawExpr='$textstring')) # from line 50, col 81.
        write('''</textarea>
\t<input type="hidden" name="keymask" value="''')
        _v = VFFSL(SL,"keymask",True) # '$keymask' on line 51, col 45
        if _v is not None: write(_filter(_v, rawExpr='$keymask')) # from line 51, col 45.
        write('''"/>
''')
        #  end of dataentry area
        write('''\t
\t<p class="comments">Remarks from you:</p>
\t<textarea class="remarks" name="remarks" cols="64" rows="2">''')
        _v = VFFSL(SL,"remarks",True) # '$remarks' on line 55, col 62
        if _v is not None: write(_filter(_v, rawExpr='$remarks')) # from line 55, col 62.
        write('''</textarea>
</td>
<td width="100px">
\t<p>Status:</p>
\t<input name="status" type="radio" ''')
        _v = VFFSL(SL,"ok",True) # '$ok' on line 59, col 36
        if _v is not None: write(_filter(_v, rawExpr='$ok')) # from line 59, col 36.
        write(''' value="1"/>
\t<span class="ok">OK</span><br/>
\t
\t<input name="status" type="radio" ''')
        _v = VFFSL(SL,"todo",True) # '$todo' on line 62, col 36
        if _v is not None: write(_filter(_v, rawExpr='$todo')) # from line 62, col 36.
        write(''' value="2"/>
\t<span class="todo">TODO</span><br/>
\t
</td>
<td>
\t<input type="submit" value="Save" style="align: bottom"/>
\t<input type="hidden" name="xmlid" value="''')
        _v = VFFSL(SL,"xmlid",True) # '$xmlid' on line 68, col 43
        if _v is not None: write(_filter(_v, rawExpr='$xmlid')) # from line 68, col 43.
        write('''"/>
\t<input type="hidden" name="langid" value="''')
        _v = VFFSL(SL,"langid",True) # '$langid' on line 69, col 44
        if _v is not None: write(_filter(_v, rawExpr='$langid')) # from line 69, col 44.
        write('''"/>
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

    _mainCheetahMethod_for_acceltablerow= 'respond'

## END CLASS DEFINITION

if not hasattr(acceltablerow, '_initCheetahAttributes'):
    templateAPIClass = getattr(acceltablerow, '_CHEETAH_templateClass', Template)
    templateAPIClass._addCheetahPlumbingCodeToClass(acceltablerow)


# CHEETAH was developed by Tavis Rudd and Mike Orr
# with code, advice and input from many other volunteers.
# For more information visit http://www.CheetahTemplate.org/

##################################################
## if run from command line:
if __name__ == '__main__':
    from Cheetah.TemplateCmdLineIface import CmdLineIface
    CmdLineIface(templateObj=acceltablerow()).run()


