from xml.dom import minidom, Node

class AmisUiDoc(minidom.Document):
    """This class extends the minidom Document class with functions related
    to the amisAccessibleUi.xml document.  It doesn't make any changes to the Lion DB or 
    to the document itself."""
    
    session = None
    
    def set_session(self, session):
        """You have to call this function first!  Ideally session would be a constructor argument, 
        but I'm not sure how to do it when we are deriving from minidom.Document because the document
        object is being created by minidom.parse, not by us directly.  However, if you don't set the session,
        nothing fatal happens."""
        self.session = session
    
    def warn(self, msg):
        """A wrapper for session.warn that checks that session has been set"""
        if self.session != None:
            self.session.warn(msg)
    
    def trace(self, msg):
        """a wrapper for session.trace_msg that checks that session has been set"""
        if self.session != None:
            self.session.trace_msg(msg)
    
    def parse_text_element(self, elem):
        """A text element that appears in the following context:
        <parent>
            <text>CDATA</text>
            <audio src="path"/>
        </parent>
        Return None in case of error, otherwise a tuple: 
            (textstring, audiosrc, xmlid, textflag, audioflag)"""
    
        if not elem.firstChild or \
            elem.firstChild.nodeType != Node.TEXT_NODE or \
            not elem.parentNode:
                return None
        text = self.escape_quotes(elem.firstChild.wholeText)
        id = elem.getAttribute("id")
        if id == "":
            self.warn('No id for text element with text = "%s"' % text)
        audio = self.get_first_child_with_tagname(elem.parentNode, "audio")
        if not audio: return None
        src = audio.getAttribute("src")
        if src == "":
            self.session.warn('No src for for audio element near text with id "%s"' % id)
        if elem.getAttribute("flag") == "new": textflag = 3
        elif elem.getAttribute("flag") == "changed": textflag = 2
        else: textflag = 1
        if audio.getAttribute("flag") == "new": audioflag = 3
        elif audio.getAttribute("flag") == "changed": audioflag = 2
        else: audioflag = 1
    
        return text, src, id, textflag, audioflag
        
    def get_all_children_with_tagname(self, elem, tagname):
        """Get the immediate children (not the grandchildren) of the element with
        the given tag name"""
        return filter(
            lambda n: n.nodeType == Node.ELEMENT_NODE and n.tagName == tagname,
            elem.childNodes)

    def get_items_in_container(self, elem):
        """For an XML element, get the actions and containers. Look one level deep
        (also look in switches)."""
        items = []
        items.extend(self.get_all_children_with_tagname(elem, "action"))
        items.extend(self.get_all_children_with_tagname(elem, "container"))
        for sw in self.get_all_children_with_tagname(elem, "switch"):
            items.extend(self.get_all_children_with_tagname(sw, "action"))
            items.extend(self.get_all_children_with_tagname(sw, "container"))
        return items

    def get_items_in_dialog(self, elm):
        """For a dialog element, get the controls"""
        items = []
        items.extend(self.get_all_children_with_tagname(elm, "control"))
        return items


    def get_targets(self, idlist):
        """from the textid of a mnemonic or accelerator, find out who it is intended for"""
        targets = []
        for xmlid in idlist:
            #the <text> element of the mnemonic or accelerator
            elm = self.get_element_by_id("text", xmlid)
            #the parent element of the mnemonic or accelerator
            parentTag = elm.parentNode.parentNode.tagName
            if parentTag == "action" or parentTag == "container" or parentTag == "control" or parentTag == "dialog":
                caption = self.get_first_child_with_tagname(elm.parentNode.parentNode, "caption")
                textid = self.get_text_id_for_caption(caption)
                targets.append(textid)
        return targets
    
    def get_first_child_with_tagname(self, elem, tagname):
        """Get first child of elem with tagname tag name."""
        for c in elem.childNodes:
            if c.nodeType == Node.ELEMENT_NODE and c.tagName == tagname:
                return c
        return None

    def get_element_by_id(self, tagname, id):
        """Workaround the absence of DTD."""
        for t in self.getElementsByTagName(tagname):
            if t.getAttribute("id") == id:
                return t

    def get_text_id_for_caption(self, elm):
        """Resolve the text for the caption element.  It might be directly nested or it might be a prompt reference.
        The permutations are:
        1. <caption>
            <text>The text</text>
            ...

        2. <caption>
            <promptItem refid="id123"/>
            means "go find the text in prompt@id='id123'"

        3. <caption>
            <promptItem>
                <text>The text</text>

        4. <caption>
            <prompt>
                <promptItem ... can be either with a refid or with nested text

        ignore all other cases.
        """
        #the obvious case #1
        text = self.get_first_child_with_tagname(elm, "text")
        #the less-obvious cases
        if text == None:
            promptItem = self.get_first_child_with_tagname(elm, "promptItem")
            if promptItem == None:
                prompt = self.get_first_child_with_tagname(elm, "prompt")
                if prompt == None: return ""
                else:
                    promptItem = self.get_first_child_with_tagname(prompt, "promptItem")
                    if promptItem == None: return ""
            #promptItem variable better have something in it at this point
            return self.get_text_id_from_prompt_item(promptItem)
        else:
            return text.getAttribute("id")

    def get_text_id_from_prompt_item(self, elm):
        """get the text out of a prompt item.  resolve references if necessary."""
        if elm == None:
            return ""

        text = self.get_first_child_with_tagname(elm, "text")
        if text != None:
            return text.getAttribute("id")
        else:
            refid = elm.getAttribute("refid")
            if refid != "":
                prompt = self.get_element_by_id("promptItem", refid)
                return self.get_text_id_from_prompt_item(prompt)
            else:
                return ""

    def printelements(self, session, elms):
        for el in elms:
            print "\t%s\n" % el.toxml()

    
    def escape_quotes(self, str):
        """Escape double quotes inside a double-quoted string.""" 
        return str.replace("\"", "\\\"")
    
    def get_audio_sibling(self, elm):
        """Get the audio sibling for this text element"""
        audios = elm.parentNode.getElementsByTagName("audio")
        if audios != None and len(audios) > 0:
            return audios[0]
        else:
            return None
    
    def get_all_text_ids(self):
        """a simple utility that returns a list of all the id values
        on text elements"""
        texts = self.getElementsByTagName("text")
        textids = []
        for t in texts:
            a = t.getAttribute("id")
            if a != None:
                textids.append(a)
        
        return textids
    

        
        