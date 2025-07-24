from dataclasses import dataclass

# Actual enums would be nice
EnumCount = 0

def reset(value = 0):
    global EnumCount
    EnumCount = value
    return EnumCount

def step():
    global EnumCount
    EnumCount += 1
    return EnumCount


#! I may want to add a token for "run"
class TokenType:
    # ~ Literals
    Null = reset(0)
    Bool = step()
    Number = step()
    String = step()
    Implicit_string = step()  #filenames and shader names for example
    Enum = step() # 0,1,2,3,4

    # ~ Operators
    Not = step() #^ Be careful with this one and !=
    UnaryMinus = step()  #Should be implemented in parser if any
    Or = step()
    And = step()

    Smaller = step()
    Greater = step()
    SmallerEqual = step()
    GreaterEqual = step()

    Divide = step()
    Multiply = step()
    Add = step()
    Subtract = step()
    FloorDiv = step()
    Modulus = step()

    Exponent = step() #? idk if it exists, I didn't check

    Equals = step()
    NotEqual = step()
    LongEquals = step()
    LongNotEquals = step()

    # ~ Keywords
    # Global commandlist keywords
    Global = step()
    Local = step()
    Persist = step()
    Post = step()
    Pre = step()

    If = step()
    Elif = step() #elif or else if
    Else = step()
    Endif = step()

    # ~ Punctuation / Symbols
    Comma = step()
    Dot = step()
    Whitespace = step()    #can be \t
    LineBreak = step()     #\n or \r\n
    Equalsign = step()
    OpenBracket = step()   #unused
    CloseBracket = step()  #unused
    OpenParen = step()
    CloseParen = step()

    # ~ Special
    SectionName = step()
    Variable = step()
    Comment = step()

    Identifier = step() #keywords like hash or something
    KeyIdentifier = step() #keywords that are confirmed before an equal sign
    ValueIdentifier = step() #keywords that are confirmed right after an equal sign, unsused for now

    EOF = step()

    NOTHING = step() #This token value should never be assigned

# Generate enum names
TokenTypeNames:tuple[str] = tuple([k for k,v in vars(TokenType).items() if not k.startswith("__")  and not callable(v)])

LiteralMap = {
    "null":TokenType.Null,
    "yes":TokenType.Bool,
    "no":TokenType.Bool,
    "on":TokenType.Bool,
    "off":TokenType.Bool,
    "true":TokenType.Bool,
    "false":TokenType.Bool
}

LiteralKeys = LiteralMap.keys()

ComparisonMap = {
    "<":TokenType.Smaller,
    ">":TokenType.Greater,
    "<=":TokenType.SmallerEqual,
    ">=":TokenType.GreaterEqual,
    "==":TokenType.Equals,
    "===":TokenType.LongEquals,
    "!=":TokenType.NotEqual,
    "!==":TokenType.LongNotEquals}

ComparisonOperators = ComparisonMap.keys()

ArithmeticsMap = {
    "+":TokenType.Add,
    "-":TokenType.Subtract,
    "*":TokenType.Multiply,
    "/":TokenType.Divide,
    "//":TokenType.FloorDiv,
    "**":TokenType.Exponent,
    "%":TokenType.Modulus}

ArithmeticOperators = ArithmeticsMap.keys()

LogicalMap = {
    "||":TokenType.Or,
    "&&":TokenType.And}

LogicalOperators = LogicalMap.keys()

ConditionalMap = {
    "if":TokenType.If,
    "elif":TokenType.Elif,
    "else if":TokenType.Elif,
    "else":TokenType.Else,
    "endif":TokenType.Endif}

ConditionalKeys = ConditionalMap.keys()

KeywordMap = {
    "global":TokenType.Global,
    "local":TokenType.Local,
    "persist":TokenType.Persist,
    "pre":TokenType.Pre,
    "post":TokenType.Post}

KeywordKeys = KeywordMap.keys()

SymbolMap = {
    ",":TokenType.Comma,
    ".":TokenType.Dot,
    "=":TokenType.Equalsign,
    "!":TokenType.Not
}

SymbolKeys = SymbolMap.keys()

#^ I'd like to add newlines and whitespace in a token map instead of here eventually
NEWLINES = ("\n","\r\n")
WHITESPACES = (" ", "\t")

@dataclass
class Token:
    type: TokenType
    start: int
    value: str  #Can be none for punctutation but I'll put it anyway

    def __repr__(self):
        return f"{TokenTypeNames[self.type]}({repr(self.value)}, pos: {self.start} to {self.end})"

    @property
    def end(self) -> int:
        return self.start + len(self.value)
    

#? This token is used when a token-related function should return None. print(token.type == NULL_TOKEN.type) will not raise an exception like (token.type == None.type)
NONE_TOKEN = Token(TokenType.NOTHING,start = None, value = None)
