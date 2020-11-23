import json
import os
import io
import urllib.parse
import re

def unpack_dict(my_dict, path):
    path_name = my_dict["Nickname"] if 'Nickname' in my_dict else my_dict['GUID']
    path.append(urllib.parse.quote_plus(path_name))
    if my_dict['LuaScript'] != "":
        try:
            os.makedirs(os.path.join(os.getcwd(), *path[:-1]))
        except (FileExistsError):
            pass

        print('writing %s' % os.path.join(os.getcwd(), *path))

        with io.open(os.path.join(os.getcwd(), *path) + ".ttslua", "w", encoding='utf-8') as out:
            out.write(re.sub('\r\n', '\n', my_dict['LuaScript']))
        my_dict['LuaScript'] = '#include %s' % os.path.join('.', *path) + '.ttslua'

    if 'ContainedObjects' in my_dict:
        unpack_array(my_dict['ContainedObjects'], path)

    path.pop()

def unpack_array(ary, path):
    for my_object in ary:
        unpack_dict(my_object, path)
    return []

def unpack(dict_or_ary, path):
    print(type(dict_or_ary))
    if type(dict_or_ary) is dict:
        unpack_dict(dict_or_ary, path)
    elif type(dict_or_ary) is list:
        unpack_array(dict_or_ary, path)

with io.open("base_mod.json", 'r', encoding='utf-8') as f:
    print
    data = json.load(f)
    cwd = __file__
    path = ["ObjectStates"]
    unpack(data["ObjectStates"], path)

    with io.open("mod_with_includes.json", 'w') as json_file:
        json.dump(data, json_file, indent=4)