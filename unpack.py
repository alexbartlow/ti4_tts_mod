import json
import os
import io
import urllib.parse
import re

class Unpack():
    def __init__(self, opts):
        if "cwd" in opts:
            self._cwd = opts['cwd']
        else:
            self._cwd = os.getcwd()
        if "write_file" in opts:
            self._write_file = opts['write_file']
        else:
            self._write_file = None
        if "mkdir" in opts:
            self._mkdir = opts['mkdir']
        else:
            self._mkdir = None

    def write_file(self, file, content):
        if self._write_file == None:
            with io.open(file, 'w', encoding='utf-8') as f:
                f.write(re.sub('\r\n', '\n', content))
        else:
            self._write_file(file, content)

    def mkdir(self, path):
        if self._mkdir == None:
            try:
                os.makedirs(os.path.join(self._cwd, *path))
            except (FileExistsError):
                pass
        else:
            self._mkdir(path)

    def unpack(self, dict_or_ary, path):
        if type(dict_or_ary) is dict:
            self.unpack_dict(dict_or_ary, path)
        elif type(dict_or_ary) is list:
            self.unpack_array(dict_or_ary, path)
        return dict_or_ary

    def extract_inline_text(self, file_content, path):
        all_include_or_blank_line = re.match(r"""\A # the beginning of the text
        \A
            (?:
                ^(?:\#include\s.* # an include line
                |
                \s* # a blank line
                )\n?$
            )+ # any number of times
        \Z # The end of the text""", file_content, re.M | re.X)
        if all_include_or_blank_line != None:
            # If the entire text is made up of empty or include lines, then it does not need to be extracted
            return file_content
        else:
            # If there exists ANY inline code, then extract this into its own ttslua file
            file_name = os.path.join(self._cwd, *path) + ".ttslua"
            self.write_file(file_name, file_content)
            return "#include %s" % file_name

    def handle_includes(self, lua, path):
        def handle_match(matchdata):
            file_name = matchdata.group(1)
            file_content = matchdata.group(2)
            content_after_stripping_includes = self.handle_includes(file_content, path)

            self.write_file(os.path.join(self._cwd, *path[:-1], file_name), content_after_stripping_includes)
            return '#include %s' % file_name

        return re.sub(r'^-- #begininclude (\S+)\n(.+)\n-- #endinclude \1', handle_match, lua, re.M)
    
    def unpack_dict(self, my_dict, path):
        path_name = my_dict["Nickname"] if 'Nickname' in my_dict else my_dict['GUID']
        path.append(urllib.parse.quote_plus(path_name))
        if my_dict['LuaScript'] != "":
            self.mkdir(path[:-1])
            file_content = self.handle_includes(my_dict['LuaScript'], path)
            file_content = self.extract_inline_text(file_content, path)
            my_dict['LuaScript'] = file_content

        if 'ContainedObjects' in my_dict:
            self.unpack_array(my_dict['ContainedObjects'], path)

        path.pop()

    def unpack_array(self, ary, path):
        for my_object in ary:
            self.unpack_dict(my_object, path)
        return ary

if __name__ == '__main__':
    with io.open("base_mod.json", 'r', encoding='utf-8') as f:
        data = json.load(f)
        cwd = __file__
        path = ["ObjectStates"]
        unpack(data["ObjectStates"], path)

        with io.open("mod_with_includes.json", 'w') as json_file:
            json.dump(data, json_file, indent=4)