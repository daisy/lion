import re
import daisylion.db.liondb
import util

# descriptive string of valid keys
VALID_KEYS = "A-Z, Ctrl, Alt, Shift, Up, Down, Left, Right, Esc, Space, +, -"

def validate_keys(key):
    """Make sure the key falls within the valid range"""
    # A-Z
    expr = "[a-z]"
    named_keys = ("ctrl", "alt", "shift", "up", "down", "left", "right", "esc", "space", 
        "+", "-", "uparrow", "downarrow", "rightarrow", "leftarrow")
    
    p = re.compile(expr, re.IGNORECASE)
    if p.match(key) and len(key) == 1:
        return True
    if key.lower() in named_keys or key == "":
        return True
    
    return False

def get_keyboard_translation_flags(session):
    langid = util.get_user(session)["users.langid"]
    session.execute_query("""SELECT translate_mnemonics, translate_accelerators FROM
        languages WHERE langid="%s" """ % langid)
    mnem1, accel1 = session.cursor.fetchone()
    mnem2 = session.has_mnemonics()
    accel2 = session.has_accelerators()
    return (mnem1 & mnem2, accel1 & accel2)
