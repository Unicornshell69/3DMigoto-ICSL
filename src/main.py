from lexer.lexer import lexer
from parser import parser


if __name__ == "__main__":
    file = """
    [Keytest]
    key = = alt ' ]
        ; this is a comment

    condition = $active == 1 ; this is not a comment, it is an error
    $skibidi = 0,1
    if $test == true
    $skibidi = 2--1.523%2
    endif
    run = CommandListRandomShit
    """
    #with open("src\\lexer\\example.ini","r") as x:
    #    file = x.read()

    lexed = lexer(file)
    lexed.tokenize()

    print(lexed.tokens)
    print(lexed.pretty_print())