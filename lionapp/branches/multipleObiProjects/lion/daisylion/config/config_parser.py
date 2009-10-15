import os
from ConfigParser import ConfigParser

def parse_config(file):
    """return a dictionary of all section dictionaries"""
    config = {}
    sections = get_sections(file)
    for s in sections:
        section_dict = parse_config_section(file, s)
        config[s] = section_dict
    return config

def parse_config_section(file, section):
    """Return a dictionary of options/values for the given section in the configuration file """
    config = ConfigParser()
    try:
        config.read(file)
    except e:
        os.sys.stderr.write("Error: %s" % e.msg)
        return None
    
    data = {}
    for o in config.options(section):
        value = config.get(section, o)
        # make all the true/false strings boolean
        # also convert ints to ints
        if value.lower() == "true": 
            value = True
        elif value.lower() == "false": 
            value = False
        else:
            try:
                value = int(value)
            except Exception, e:
                value = value
        data[o] = value
    
    return data

def get_sections(file):
    """return a list of all the sections"""
    config = ConfigParser()
    try:
        config.read(file)
    except e:
        os.sys.stderr.write("Error %s" % e.msg)
        return None
    
    return config.sections()
