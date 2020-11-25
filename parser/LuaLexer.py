from sly import Lexer, Parser
import re

class LuaLexer(Lexer):
    tokens = { BEGININCLUDE, ENDINCLUDE, FILENAME, CODE_LINE}
    BEGININCLUDE = r'-- #begininclude\s(\S+)'
    ENDINCLUDE = r'-- #endinclude\s(\S+)'
    CODE_LINE = r'.+'

    @_(r'\n+')
    def newline(self,t):
      self.lineno += t.value.count('\n')

    def error(self, t):
        print("Illegal character '%s' at index %i" % (t.value[0], self.index))
        self.index += 1

class LuaParser(Parser):
    tokens = LuaLexer.tokens

    precedence = (
    )

    # parse this lua section into 

    def __init__(self):
        self.includes = {}

    # Treat a whole block as an atomic unit
    @_('begin_include code_block end_include')
    def code_block(self, p):
      if p.begin_include != p.end_include:
        raise Exception("Includes do not match", p.begin_include, p.end_include) 

      self.includes[p.begin_include] = p.code_block
      return "-- #include %s" % p.begin_include

    @_('CODE_LINE CODE_LINE')
    def code_block(self, p):
      print("two lines of code: %s, %s", (p.CODE_LINE0, p.CODE_LINE1))
      return p.CODE_LINE0 + '\n' + p.CODE_LINE1

    @_('CODE_LINE')
    def code_block(self, p):
      print("one line of code: %s", p.CODE_LINE)
      return p.CODE_LINE

    @_('BEGININCLUDE')
    def begin_include(self, p):
      return re.split(r'-- #begininclude\s+', p.BEGININCLUDE)[1]

    @_('ENDINCLUDE FILENAME')
    def end_include(self, p):
      return re.split(r'-- #endinclude\s*', p.ENDINCLUDE)[1]