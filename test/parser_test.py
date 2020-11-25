import unittest
import copy
import sys, os
from textwrap import dedent

from parser.LuaLexer import LuaLexer, LuaParser

class TestParser(unittest.TestCase):
  def test_parses_basic(self):
    text = 'print("Im lua code")\nprint("I am also lua code")'
    lexer = LuaLexer()
    parser = LuaParser()
    tokens = lexer.tokenize(text)

    self.assertEqual(parser.parse(tokens), text)

  def test_parse_import(self):
    text = '-- #begininclude included.ttslua\n-- I am in ttslua\n-- #endinclude included.ttslua\n'
    lexer = LuaLexer()
    parser = LuaParser()
    tokens = lexer.tokenize(text)

    self.assertEqual(parser.parse(tokens), text)


if __name__ == "__main__":
  unittest.main()