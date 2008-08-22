import os
os.sys.path.append("./templates")
from templates import translate, error, login, xhtml

def parse_key_masks(keys):
    """Take something like 'Ctrl+0' and isolate 'Ctrl+' and 'O'.  Return both parts.  Account for 'Ctrl++' and Space
    (in AMIS, you can't change Space, so we can treat it like a keymask) """
    if keys == "Space":
        return keys, ""
    
    last_part=""
    if keys.endswith("+") == True:
        # reverse the string, replace the last '+' with another letter, but remember what we did
        keys = keys[::-1]
        keys = keys.replace("+", "x", 1)
        last_part = "+"
    keys = keys[::-1]
    pos = keys.rfind("+")
    if pos == -1:
        return "", keys
    else:
        if last_part == "":
            last_part = keys[pos+1:len(keys)]
        return keys[0:pos+1], last_part


def main():
    mask, letter = parse_key_masks("Ctrl++")
    print mask
    print letter
    
    

if __name__ == "__main__": main()
        