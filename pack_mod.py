import json
import os
import io
import urllib.parse
import re

# If this dictionary has an #include for the lua script, then insert that script into the LuaScript as a one line script
def pack_object(my_object):
    if ("LuaScript" in my_object) and my_object['LuaScript'].startswith('#include '):
        print("packing #include for %s" % my_object['Nickname'])
        # include the referenced file
        path_to_include = re.sub('#include ', '', my_object['LuaScript'])
        with io.open(path_to_include, 'r', encoding='utf-8') as f:
            my_object['LuaScript'] = f.read()
    if "ContainedObjects" in my_object:
        for contained_object in my_object["ContainedObjects"]:
            pack_object(contained_object)
    
    return my_object

with io.open("mod_with_includes.json", 'r', encoding='utf-8') as f:
    data = json.load(f)
    cwd = __file__
    for my_object in data["ObjectStates"]:
        pack_object(my_object)

    with io.open("mod_packed.json", 'w') as json_file:
        json.dump(data, json_file, indent=4)