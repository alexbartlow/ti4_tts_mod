import unittest
import copy
import sys, os
parent_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, parent_path)
import unpack
from textwrap import dedent

class TestUnpack(unittest.TestCase):
  def subject(self, _files):
    def write_dir(dirname):
      return True
    def write_file(filename, content):
      _files[filename] = content
    
    return unpack.Unpack({ 'write_dir': write_dir, 'write_file': write_file, 'cwd': 'test'})

  def assertUnpacked(self, _input, expectedOutput, expectedFiles):
    actualFiles = {}
    actualOutput = self.subject(actualFiles).unpack(copy.deepcopy(_input), [])
    self.assertEqual(expectedOutput, actualOutput, "output - expected: %s, got: %s" % (expectedOutput, actualOutput))
    self.assertEqual(expectedFiles, actualFiles, "files - expected: %s, got: %s" % (expectedFiles, actualFiles))

  def test_unpacks_scripts_to_files(self):
    _input = [
      {
        "Nickname": "noScript",
        "LuaScript": ""
      },
      {
        "Nickname": "hasScript",
        "LuaScript": "-- I have a script"
      }
    ]

    _output = [
      {
        "Nickname": "noScript",
        "LuaScript": ""
      },
      {
        "Nickname": "hasScript",
        "LuaScript": "#include test/hasScript.ttslua"
      }
    ]

    _files = {
      "test/hasScript.ttslua": "-- I have a script"
    }

    self.assertUnpacked(_input, _output, _files)

  def test_unpack_skips_include_only_files(self):
      _input = {
        "Nickname": "only_have_includes",
        "LuaScript": """-- #begininclude includeOnly.ttslua
-- I am includeOnly.ttslua
-- #endinclude includeOnly.ttslua"""
      }

      _output = {
        "Nickname": "only_have_includes",
        "LuaScript": "#include includeOnly.ttslua"
      }

      _files = {
        "test/includeOnly.ttslua": "-- I am includeOnly.ttslua"
      }

      self.assertUnpacked(_input, _output, _files)

  def test_unpacks_includes_and_inlines(self):
    _input = {
      "Nickname": "includes_and_code",
      "LuaScript": """-- #begininclude include.ttslua
-- I am include.ttslua
-- #endinclude include.ttslua
-- I am inline"""
    }

    _output = {
      "Nickname": "includes_and_code",
      "LuaScript": """#include test/includes_and_code.ttslua"""
    }

    _files = {
      'test/include.ttslua': "-- I am include.ttslua",
      'test/includes_and_code.ttslua': '#include include.ttslua\n-- I am inline'
    }

    self.assertUnpacked(_input, _output, _files)

  def test_unpacks_nested_objects(self):
    _input = {
      "Nickname": "Parent",
      "LuaScript": """-- #begininclude parent.ttslua
-- I am the parent
-- #endinclude parent.ttslua""",
      "ContainedObjects": [
        {
          "Nickname": "Child1",
          "LuaScript": """-- #begininclude child_one.ttslua
-- I am child1
-- #endinclude child_one.ttslua"""
        }
      ]
    }

    _output = {
      "Nickname": "Parent",
      "LuaScript": "#include parent.ttslua",
      "ContainedObjects": [
        {
          "Nickname": "Child1",
          "LuaScript": "#include child_one.ttslua"
        }
      ]
    }

    _files = {
      'test/parent.ttslua': "-- I am the parent",
      'test/Parent/child_one.ttslua': '-- I am child1'
    }

    self.assertUnpacked(_input, _output, _files)

  def test_extract_absolute_includes(self):
    _input = {
      "Nickname": "Parent",
      "LuaScript": """-- #begininclude parent.ttslua
-- I am the parent
-- #endinclude parent.ttslua""",
      "ContainedObjects": [
        {
          "Nickname": "Child1",
          "LuaScript": """-- #begininclude <child_one.ttslua>
-- I am child1
-- #endinclude <child_one.ttslua>"""
        }
      ]
    }

    _output = {
      "Nickname": "Parent",
      "LuaScript": "#include parent.ttslua",
      "ContainedObjects": [
        {
          "Nickname": "Child1",
          "LuaScript": "#include <child_one.ttslua>"
        }
      ]
    }

    _files = {
      'test/parent.ttslua': "-- I am the parent",
      'test/child_one.ttslua': '-- I am child1'
    }

    self.assertUnpacked(_input, _output, _files)

  def test_unpack_extracts_nested_include_statements(self):
    None

  def test_unpack_extracts_old_include_statements(self):
    None

  def test_unpack_extracts_nested_old_include_statements(self):
    None
    
if __name__ == "__main__":
  unittest.main()

