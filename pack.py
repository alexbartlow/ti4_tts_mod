import json
import os
import io
import urllib.parse
import re
from textwrap import dedent

class Pack:
    def __init__(self, opts):
        if "read_file" in opts:
            self._read_file = opts["read_file"]

    # DI for testing file reads
    def read_file(self, path):
        if self._read_file == None:
            with io.open(path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            return self._read_file(path)

    def process_includes(self, luafile):
        def include_replace(matchobj):
            return """-- #begininclude %s
%s
-- #endinclude %s""" % (matchobj.group(1), self.process_includes(self.read_file(matchobj.group(1))), matchobj.group(1))
        return re.sub(r'-- #include (.+)', include_replace, luafile)

    # If this dictionary has an #include for the lua script, then insert that script into the LuaScript as a one line script
    def pack_object(self, my_object):
        if ("LuaScript" in my_object) and my_object['LuaScript'].startswith('#include '):
            path_to_include = re.sub('#include ', '', my_object['LuaScript'])
            my_object['LuaScript'] = self.process_includes(self.read_file(path_to_include))
        if "ContainedObjects" in my_object:
            for contained_object in my_object["ContainedObjects"]:
                self.pack_object(contained_object)
        return my_object

if __name__ == "__main__":
    with io.open("mod_with_includes.json", 'r', encoding='utf-8') as f:
        data = json.load(f)
        cwd = __file__
        for my_object in data["ObjectStates"]:
            Pack({}).pack_object(my_object)

        with io.open("mod_packed.json", 'w') as json_file:
            json.dump(data, json_file, indent=4)
