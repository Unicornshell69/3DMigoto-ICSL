from .tokens import ArithmeticsMap, ArithmeticOperators, LogicalMap, LogicalOperators, ComparisonMap, ComparisonOperators, ConditionalMap, ConditionalKeys, KeywordMap, KeywordKeys, SymbolMap, SymbolKeys, LiteralMap, LiteralKeys
from .tokens import Token, TokenType, NONE_TOKEN, NEWLINES, WHITESPACES, TokenTypeNames

# The lexer is mostly used to match common keywords, find section declaration, and be unaware of unknown keywords used in key = value format
# Any unknown thing is dropped as a "Identifier"
# I should probably have some logic for the lexer to detect key identifier and value identifier
# This will help with parsing





class lexer:
    def __init__(self, source):
        self.source:str = source
        self.pos = 0
        self.length = len(source)
        self.tokens:list[Token] = []
        self.last_token = NONE_TOKEN

    def pretty_print(self) -> str:
        """Prints the token list cutely type shit"""
        text = ""
        tab = "  "
        pad = " "
        level = 0
        for token in self.tokens:
            if token.type == TokenType.LineBreak:
                text.rstrip()
                text += "\n"
                text += tab * max(0,level)
            else:
                if token.type == TokenType.If:
                    level += 1
                elif token.type == TokenType.Endif:
                    level -= 1
                    text = text[:len(text)-len(tab)]

                if token.type == TokenType.Whitespace:
                    pass
                # because I don't add the header bracket to the value, I have to add them back here
                elif token.type == TokenType.SectionName:
                    text += "["+token.value+"]"
                else:
                    text += token.value

                    if token.type != TokenType.UnaryMinus:
                        text += pad
            

        return text

    def line_col(self, pos) -> tuple[int,int]:
        "Returns line, col"
        line = 1
        col = 1
        for s in self.source[:pos]:
            if s == "\n" or s == "\r\n": 
                line += 1
                col = 1
            else:
                col += 1
        return line, col


    def eof(self) -> bool:
        return self.pos >= self.length
    
    def peek(self, offset = 0) -> str|None:
        "returns none if eof"
        if self.pos + offset < self.length:
            return self.source[self.pos + offset]
        return None
    
    def backtrack(self, n = 1) -> Token:
        """Goes backwards in the token list. Returns the NONE_TOKEN if OOB"""
        if len(self.tokens) < n:
            return NONE_TOKEN
        return self.tokens[-n]
    
    def eat(self, n = 1) -> str:
        """Advances by n, returns character at source[old:old+n]"""
        self.pos += n
        return self.source[self.pos-n:self.pos]
    
    def vomit(self, n = 1) -> str:
        """Exact opposite of eat, I don't need it but it's kinda funny"""
        self.pos -= n
        return self.source[self.pos:self.pos+n]


    def compare_string(self, string:str) -> bool:
        if self.pos + (length:=len(string)) > self.length:
            return False
        
        for i in range(length):
            if self.source[self.pos+i] != string[i]:
                return False
            
        return True

    def match(self, *symbols:str) -> bool:
        "Returns true if the source contains one of the symbols, else false"
        return any(self.compare_string(symbol) for symbol in symbols)

    def symbol(self, *symbols:str) -> str|None:
        "Returns the longest matched symbol. To avoid a None return, first check with match()"
        #Something like ** would match exponent instead of multiply
        matches = [s for s in symbols if self.compare_string(s)]
        return max(matches, key=len) if matches else None
    
    #! PLACEHOLDER. REPLACE
    def valid_variablename(self, char:str) -> bool:
        return char.isalpha() or char in ("_")
    
    def emit_warning(self,warn:str) -> None:
        print(f"[Lexer] -> Raised Warning: {warn}")

    def add_token(self, tokentype:TokenType, start:int, value:str):
        """Adds a token and updates the `last_token` variable correctly"""
        self.tokens.append(Token(tokentype, start, value))
        # Update the last token, unless it is a whitespace. Useful for checking if a token is first of line
        if tokentype != TokenType.Whitespace:
            self.last_token = self.tokens[-1]


    def tokenize(self):

        # Use of add_token() to update the last token state

        expecting_value = 0

        while not self.eof():
            start = self.pos
            c = self.peek()

            #^ Whitespaces could be handled in symbols/punctuation instead
            # ~ Skip whitespace
                #&   or \t
            if c in WHITESPACES:
                while not self.eof() and self.match(*WHITESPACES):
                    l = len(self.symbol(*WHITESPACES))
                    self.eat(l)
                self.add_token(TokenType.Whitespace, start, self.source[start:self.pos])

                if expecting_value:
                    expecting_value = 2

            # ~ Newline
                #& \r\n or \n
            elif self.match(*NEWLINES):
                nl = self.symbol(*NEWLINES)
                self.add_token(TokenType.LineBreak, start, self.eat(len(nl)))

            # ~ Comment
                #& ;this is a comment
            elif c == ";" and self.last_token.type == TokenType.LineBreak:
                # I roll back until I don't find a whitespace
                # If a linebreak is found then it is the first non-whitespace character, so a comment
                # Else I read it as ";" and continue
                while not self.eof() and self.peek() not in NEWLINES:
                    self.eat()
                self.add_token(TokenType.Comment, start, self.source[start:self.pos])

            # ~ Parenthesesesses
                #& ()
            elif self.match("("):
                self.add_token(TokenType.OpenParen, start, self.eat())
            elif self.match(")"):
                self.add_token(TokenType.CloseParen, start, self.eat())

            # ~ Header [HeaderExample]
            elif c == "[" and self.last_token.type == TokenType.LineBreak:
                i = 0
                while not self.eof() and self.source[self.pos+i] not in ("]",*NEWLINES):
                    i += 1
                
                if self.source[self.pos+i] == "]":
                    # Here I'm skipping the brackets in the header name, it's useless bloat for the parser
                    self.add_token(TokenType.SectionName,start, self.eat(i+1)[1:-1])
                    
                else:
                    self.emit_warning(f"Header unclosed at {self.line_col(self.pos+i)}, reading as identifier instead")
                    self.add_token(TokenType.Identifier,start, self.eat())

            # ~ Variable 
                #& $varvarbinks
            elif c == "$":
                self.eat()
                while not self.eof() and self.valid_variablename(self.peek()):
                    self.eat()
                self.add_token(TokenType.Variable, start, self.source[start:self.pos])

            # ~ Number
                #& This could be changed to not read dots, and have a parser case that combines TokenType.Number + TokenType.Dot + TokenType.Number
            elif c.isdigit():
                self.eat()
                while not self.eof() and self.peek().isdigit():
                    self.eat()
                # find floats
                if self.peek() == ".":
                    self.eat()
                    while not self.eof() and self.peek().isdigit():
                        self.eat()
                self.add_token(TokenType.Number, start, self.source[start:self.pos])

            # ~ Strings
                #& "used in resource sections only I think"
                #& If the string fails to find an end, it will revert back to being a single character identifier
            elif c in ("'", "\""):
                #don't forget to eat the first character
                i = 1
                while not self.eof() and self.source[self.pos+i-1] not in (c,*NEWLINES):
                    i += 1
                
                if self.source[self.pos+i] == c:
                    self.add_token(TokenType.String, start, self.eat(i))

                else:
                    self.emit_warning(f"String unclosed at {self.line_col(self.pos+i)}, reading as identifier instead")
                    self.add_token(TokenType.Identifier, start, self.eat())

            # ~ Null and Bool
                #& yes/no/on/off/true/false and null
            elif self.match(*LiteralKeys):
                literal = self.symbol(*LiteralKeys)
                ttype = LiteralMap[literal]
                self.add_token(ttype,start, self.eat(len(literal)))

            # ~ Conditionals
                #& If / elif / else if / else / endif
            elif self.match(*ConditionalKeys):
                word = self.symbol(*ConditionalKeys)
                ttype = ConditionalMap[word]
                self.eat(len(word))
                self.add_token(ttype,start,word)

            # ~ Arithmetic
                #& + - * / // ** %
            elif self.match(*ArithmeticOperators):
                operator = self.symbol(*ArithmeticOperators)
                ttype = ArithmeticsMap[operator]
                self.eat(len(operator))
                #^ Create unary minus in the parser while creating expressions
                self.add_token(ttype,start,operator)

            # ~ Comparison
                #& less than or greater than
            elif self.match(*ComparisonOperators):
                operator = self.symbol(*ComparisonOperators)
                ttype = ComparisonMap[operator]
                self.eat(len(operator))
                self.add_token(ttype,start,operator)

            # ~ Keywords
                #& pre / post / global / local / persist
            elif self.match(*KeywordKeys):
                keyword = self.symbol(*KeywordKeys)
                ttype = KeywordMap[keyword]
                self.eat(len(keyword))
                self.add_token(ttype,start,keyword)


            # Later I might add a parsing case that will combine TokenType.Not + (TokenType.EqualSign | TokenType.Equals), but parsing not seperate works too
            # ~ Logical 
                #& or / and
            elif self.match(*LogicalOperators):
                operator = self.symbol(*LogicalOperators)
                ttype = LogicalMap[operator]
                self.eat(len(operator))
                self.add_token(ttype,start,operator)


            # ~ Symbols
                #& Not, equalsign, dot, comma
            elif self.match(*SymbolKeys):
                symbol = self.symbol(*SymbolKeys)
                ttype = SymbolMap[symbol]
                self.add_token(ttype,start,self.eat(len(symbol)))


            # ~ Identifier
                #& Any keyword with no associated token
            else:
                # Fallback to generic Identifier token if nothing found, these will be checked by the parser for all the sections and their "quirks" >:(
                while not self.eof() and self.peek() not in (*NEWLINES,*WHITESPACES):
                    self.eat()
                # Detect keys here instead of inside the parser
                if self.last_token.type == TokenType.LineBreak:
                    ttype = TokenType.KeyIdentifier
                else:
                    ttype = TokenType.Identifier
                self.add_token(ttype,start,self.source[start:self.pos])


