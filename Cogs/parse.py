import enum
import sys
from io import StringIO
from discord.ext import commands


class Emitter:
    def __init__(self):
        self.code = ""
        self.tabdepth = 0

    def add(self, code):
        self.code += code

    def addTabs(self):
        for i in range(self.tabdepth):
            self.code += "\t"

    def addline(self, code):
        self.code += code + "\n"


class Parser:
    def __init__(self, lexer, emitter):
        self.lexer = lexer
        self.emitter = emitter
        self.variables = set()

        self.curr = None
        self.nextvalue = None
        self.next()
        self.next()

    def checkcurr(self, kind):
        return kind == self.curr.type

    def checknext(self, kind):
        return kind == self.nextvalue.type

    def match(self, kind):
        if not self.checkcurr(kind):
            raise Exception("Expected " + kind.name + ", got " + self.curr.type.name + "\n")
        self.next()
        return ""

    def next(self):
        self.curr = self.nextvalue
        self.nextvalue = self.lexer.getToken()

    def program(self):
        while self.checkcurr(TokenType.nl):
            self.nl()

        while not self.checkcurr(TokenType.eof):
                self.statement()

    def statement(self):
        if self.checkcurr(TokenType.print):
            self.next()
            self.match(TokenType.stp)
            if self.checkcurr(TokenType.string):
                self.emitter.add("print(\"" + self.curr.value + "\")")
                self.next()
            else:
                self.emitter.add("print(")
                self.expression()
                self.emitter.add(")")
            self.match(TokenType.endp)
            self.nl()
        elif self.checkcurr(TokenType.IF):
            self.next()
            self.emitter.add("if ")
            self.match(TokenType.stp)
            self.comparison()
            self.match(TokenType.endp)
            self.emitter.addline(":")
            self.match(TokenType.stb)
            self.emitter.tabdepth+=1
            while not self.checkcurr(TokenType.endb):
                self.emitter.addTabs()
                self.statement()

            self.match(TokenType.endb)
            self.emitter.tabdepth-=1
        elif self.checkcurr(TokenType.WHILE):
            self.next()
            self.emitter.add("while ")
            self.match(TokenType.stp)
            self.comparison()
            self.match(TokenType.endp)
            self.emitter.addline(":")
            self.match(TokenType.stb)
            self.emitter.tabdepth+=1
            while not self.checkcurr(TokenType.endb):
                self.emitter.addTabs()
                self.statement()

            self.match(TokenType.endb)
            self.emitter.tabdepth-=1
        elif self.checkcurr(TokenType.let):
            self.next()

            if self.curr.value not in self.variables:
                self.variables.add(self.curr.value)

            self.emitter.add(self.curr.value + " = ")
            self.match(TokenType.ident)
            self.match(TokenType.set)
            self.expression()
            self.nl()
            ''' input we wont use bc its hard to code in discord bot cuz im lazy
        elif self.checkcurr(TokenType.input):
            self.next()
            if self.curr.value not in self.variables:
                self.variables.add(self.curr.value)

            self.emitter.add(self.curr.value + " = input()")
            self.match(TokenType.ident)
            self.nl()'''
        else:
            raise Exception("INVALID STATEMENT AT " + self.curr.value)


    def nl(self):
        self.match(TokenType.nl)
        self.emitter.addline("")
        while self.checkcurr(TokenType.nl):
            self.next()

    def primary(self):
        if self.par():
            return
        if self.checkcurr(TokenType.number):
            self.emitter.add(self.curr.value)
            self.next()
        elif self.checkcurr(TokenType.ident):
            if self.curr.value not in self.variables:
                raise Exception("Referencing Variable Before Initiated: " + self.curr.value + "\n")
            self.emitter.add(self.curr.value)
            self.next()
        else:
            raise Exception("Unexpected Token at " + self.curr.value + "\n")

    def unary(self):
        if self.checkcurr(TokenType.plus) or self.checkcurr(TokenType.minus):
            self.emitter.add(self.curr.value)
            self.next()
        self.primary()

    def par(self):
        if self.checkcurr(TokenType.stp):
            self.emitter.add(" ( ")
            self.next()
            self.parcalc()
            return True
        if self.checkcurr(TokenType.endp):
            self.next()
            self.emitter.add(" ) ")
            return True
        return False

    def parcalc(self):
        self.term()
        while self.checkcurr(TokenType.plus) or self.checkcurr(TokenType.minus):
            self.emitter.add(" " + self.curr.value + " ")
            self.next()
            self.term()
        if self.checkcurr(TokenType.endp):
            self.par()

    def term(self):
        self.unary()
        while self.checkcurr(TokenType.mult) or self.checkcurr(TokenType.div):
            self.emitter.add(self.curr.value)
            self.next()
            self.unary()

    def expression(self):
        self.term()
        while self.checkcurr(TokenType.plus) or self.checkcurr(TokenType.minus):
            self.emitter.add(" " + self.curr.value + " ")
            self.next()
            self.term()

    def comparison(self):  # add boolean + not operator
        self.expression()
        if (self.checkcurr(TokenType.grt)
                or self.checkcurr(TokenType.less)
                or self.checkcurr(TokenType.geq)
                or self.checkcurr(TokenType.leq)
                or self.checkcurr(TokenType.same)
                or self.checkcurr(TokenType.ne)):
            self.emitter.add(self.curr.value)
            self.next()
            self.expression()
        else:
            raise Exception("Expected comparison operator at " + self.curr.value)
        if self.checknext(TokenType.AND):
            self.emitter.add(" and ")
            self.next()
            self.comparison()
        elif self.checknext(TokenType.OR):
            self.emitter.add(" or ")
            self.next()
            self.comparison()


class TokenType(enum.Enum):
    eof = -1
    nl = 0  # ;
    number = 1  # number
    string = 2  # string
    ident = 3
    # Keywords.
    print = 103
    # input = 104 not needed in discord bot
    let = 105
    IF = 106
    ELSE = 107
    WHILE = 109
    stb = 111  # {
    endb = 112  # }
    stp = 113  # (
    endp = 114  # )
    # Operators.
    set = 201  # =
    plus = 202  # plus
    minus = 203  # minus
    mult = 204  # mulitplication
    div = 205  # division
    same = 206  # ==
    ne = 207  # !=
    less = 208  # <
    leq = 209  # <=
    grt = 210  # >
    geq = 211  # >=
    AND = 212  # &&
    OR = 213  # ||
    NOT = 214  # !


class Token:
    def __init__(self, value, type):
        self.value = value
        self.type = type

    @staticmethod
    def check(text):
        if text == "if":
            return TokenType.IF
        if text == "while":
            return TokenType.WHILE
        for kind in TokenType:
            if kind.name == text and 100 <= kind.value < 200:
                return kind
        return None


class Lexar:
    def __init__(self, input):
        self.code = input + '\n'
        self.char = '\0'
        self.pos = -1  # undef
        self.iter()

    def iter(self):
        self.pos += 1
        if self.pos < len(self.code):
            self.char = self.code[self.pos]
        else:
            self.char = '\0'

    def next(self):
        if self.pos < len(self.code) - 1:
            return self.code[self.pos + 1]
        return '\0'

    def skipspaces(self):
        while self.char == ' ' or self.char == '\t' or self.char == "\r" or self.char == "\n":
            self.iter()

    def getToken(self):
        self.skipspaces()
        token = None
        if self.char == '+':
            token = Token(self.char, TokenType.plus)
        elif self.char == '-':
            token = Token(self.char, TokenType.minus)
        elif self.char == '*':
            token = Token(self.char, TokenType.mult)
        elif self.char == '/':
            token = Token(self.char, TokenType.div)
        elif self.char == ';':
            token = Token(self.char, TokenType.nl)
        elif self.char == '\0':
            token = Token('', TokenType.eof)
        elif self.char == '{':
            token = Token('{', TokenType.stb)
        elif self.char == '}':
            token = Token('}', TokenType.endb)
        elif self.char == '(':
            token = Token('(', TokenType.stp)
        elif self.char == ')':
            token = Token(')', TokenType.endp)
        elif self.char == '=':
            if self.next() == '=':
                lastChar = self.char
                self.iter()
                token = Token(lastChar + self.char, TokenType.same)
            else:
                token = Token(self.char, TokenType.set)
        elif self.char == '>':
            if self.next() == '=':
                lastChar = self.char
                self.iter()
                token = Token(lastChar + self.char, TokenType.geq)
            else:
                token = Token(self.char, TokenType.grt)
        elif self.char == '<':
            if self.next() == '=':
                lastChar = self.char
                self.iter()
                token = Token(lastChar + self.char, TokenType.leq)
            else:
                token = Token(self.char, TokenType.less)
        elif self.char == '!':
            if self.next() == '=':
                lastChar = self.char
                self.iter()
                token = Token(lastChar + self.char, TokenType.ne)
            else:
                token = Token(self.char, TokenType.NOT)
        elif self.char == '&':
            if self.next() == '&':
                lastChar = self.char
                self.iter()
                token = Token(lastChar + self.char, TokenType.AND)
            else:
                raise Exception("Syntax error: "+self.char+self.next())
        elif self.char == '|':
            if self.next() == '|':
                lastChar = self.char
                self.iter()
                token = Token(lastChar + self.char, TokenType.OR)
            else:
                raise Exception("Syntax error: "+self.char+self.next())
        elif self.char == '\"':
            self.iter()
            start = self.pos
            while self.char != '\"':
                self.iter()
            token = Token(str(self.code[start:self.pos]), TokenType.string)
        elif self.char.isdigit():
            start = self.pos
            while self.next().isdigit():
                self.iter()
            if self.next() == '.':
                self.iter()
                if not self.next().isdigit():
                    raise Exception("Syntax error: " + self.char + self.next())
                    self.iter()
                    return token
                while self.next().isdigit():
                    self.iter()

            token = Token(self.code[start: self.pos + 1], TokenType.number)
        elif self.char.isalpha():
            start = self.pos
            while self.next().isalnum():
                self.iter()

            value = self.code[start: self.pos + 1]
            keyword = Token.check(value)
            if keyword == None:  # Identifier
                token = Token(value, TokenType.ident)
            else:  # Keyword
                token = Token(value, keyword)
        else:
            raise Exception("Syntax error: Unknown Character: "+self.char)

        self.iter()
        return token


class Parse(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, name='run')
    async def Check_Syntax(self, ctx, *, arg):
        input = Lexar(arg)
        emitter = Emitter()
        parser = Parser(input, emitter)
        '''output = ''
        token = input.getToken()
        while token.type != TokenType.eof:
            if token.type == TokenType.err:
                await ctx.send(output + "Lexar: an Error has occurred, unknown token/wrong syntax")
                return
            if token.type == TokenType.string or token.type == TokenType.number or token.type == TokenType.ident:
                output += token.value + ":"
            output += token.type.name + "\n"
            token = input.getToken()'''
        try:
            parser.program()
        except Exception as e:
            await ctx.send(str(e))
            return
        old_out=sys.stdout
        sys.stdout=new_out=StringIO()
        exec(emitter.code)
        await ctx.send(new_out.getvalue())
        sys.stdout=old_out


def setup(bot):
    bot.add_cog(Parse(bot))
