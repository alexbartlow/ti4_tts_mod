from sly import Lexer, Parser

class LuaLexer(Lexer):
    tokens: { BEGININCLUDE, ENDINCLUDE, FILENAME, WHITESPACE, CODEBLOCK}

    IDENTIFIER = r'\S+'
    BEGININCLUDE = r'-- #begininclude'
    ENDINCLUDE = r'-- #endinclude'
    CODEBLOCK = re.compile(r'.+', r.M)

    ignore_newline = r'\n+'

    def ignore_newline(self, t):
        self.lineno += t.value.count('\n')

    def error(self, t):
        print("Illegal character '%s'" % t.value[0])
        self.index += 1

class LuaParser(Parser):
    tokens = LuaLexer.tokens

    precedence = (
    )

    # parse this lua section into 

    def __init__(self)
        self.fileStack = 
        self.names = {}

    @_('begininclude CODEBLOCK endinclude')
    def include(self, p)


    @_('BEGININCLUDE FILENAME')
    def begininclude(self, p)
        return p.FILENAME

    @_('ENDINCLUDE FILENAME')
    def endinclude(self, p):
        return p.FILENAME