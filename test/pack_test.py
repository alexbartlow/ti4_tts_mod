import unittest
import copy
import sys, os
parent_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, parent_path)
import pack
from textwrap import dedent

class TestPack(unittest.TestCase):
  def subject(self, _files):
    def read_file(file_to_read):
      return _files[file_to_read]

    return pack.Pack({ 'read_file': read_file})

  def assertPacked(self, _input, _files, _expected):
    _packed = self.subject(_files).pack_object(copy.deepcopy(_input))
    self.assertEqual(_packed, _expected)

  def test_pack_basic_includes(self):
    _input = {
      "LuaScript": "#include myfile.ttlua"
    }
    _files = {
      "myfile.ttlua": "-- this is a basic lua file\ni+1"
    }

    _expected = {
      "LuaScript": _files['myfile.ttlua']
    }

    self.assertPacked(_input, _files, _expected)

  def test_pack_nested_object_includes(self):
    _input = {
      "LuaScript": "#include myfile.ttlua",
      "ContainedObjects": [
        {
          "LuaScript": "#include contained.ttlua"
        },
        {
          "LuaScript": "-- I am an inline script"
        }
      ]
    }

    _files = {
      "contained.ttlua": "-- i am contained.ttlua",
      "myfile.ttlua": "--i am myfile.ttlua"
    }

    _expected = {
      "LuaScript": _files["myfile.ttlua"],
      "ContainedObjects": [
        {
          "LuaScript": _files['contained.ttlua']
        },
        {
          'LuaScript': '-- I am an inline script'
        }
      ]
    }

    self.assertPacked(_input, _files, _expected)

  def test_pack_nested_include_includes(self):
    _input = {
      "LuaScript": "#include myfile.ttlua",
    }

    _files = {
      "myfile.ttlua": """
-- I am myfile.lua
-- I include another file:
-- #include otherfile.ttlua
      """.strip(),
      "otherfile.ttlua": """
-- I am otherfile.ttlua
      """.strip(),
    }

    _expected = {
      "LuaScript": dedent("""
      -- I am myfile.lua
      -- I include another file:
      -- #begininclude otherfile.ttlua
      -- I am otherfile.ttlua
      -- #endinclude otherfile.ttlua
      """).strip()
    }

    self.assertPacked(_input, _files, _expected)

if __name__ == "__main__":
  unittest.main()

