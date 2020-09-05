 # -*- coding: utf-8 -*
LEXER_VER = 'v0.10 20.07.08'
import ply.lex as lex
from fractions import Fraction
# token list
reserved = {'set':'SET', 'if':'IF', 'lambda':'LAMBDA','def':'DEF', 'None':'NONE', 'True':'TRUE','False':'FALSE','const':'CONST', 
         'is':'IS', 'in':'IN', 'apply':'APPLY', 'call_cc':'CALLCC', 'var':'VAR', 'while':'WHILE', 'macro':'MACRO', 'class':'CLASS'}
tokens = ['SQUOTE','COMMENT', 'STR', 'INT','HEX', 'OCT', 'BIN', 'FLOAT','FRACT', 'PLUS','MINUS','TIMES','POW', 'DIVIDE','IDIV','INC', 'DEC', 
        'LPAREN','RPAREN','LBRAC', 'RBRAC','LBRAK', 'RBRAK',  'CAMMA','COL','SEMICOL','DOT', 'DOTS', 'LET','IDIV_LET','MOD_LET','SR_LET','SL_LET',
        'ADD_LET', 'SUB_LET', 'MUL_LET', 'DIV_LET', 'COMMENT_', 'AND', 'OR','BAND','BOR','BNOT','BSR','BSL', 'HAT',
        'EQUAL','NEQ', 'GEQ', 'LEQ', 'GT', 'LT', 'NOT', 'ID', 'PERC'] + list(reserved.values())
        ## 注)
        ## TrueとFalseはreserved token扱いにしないと、「Trueee」等が「True」と「ee」に分けられてしまう

# token rules
t_SQUOTE = r"'"
t_PLUS   = r'\+'
t_MINUS  = r'-'
t_TIMES  = r'\*'
t_POW    = r'\*\*'
t_DIVIDE = r'/'
t_IDIV   = r'//'
t_INC    = r'\+\+'
t_DEC    = r'--'
t_PERC   = r'%'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRAC  = r'{'
t_RBRAC  = r'}'
t_LBRAK  = r'\['
t_RBRAK  = r'\]'
t_CAMMA  = r','
t_COL    = r':'
t_SEMICOL= r';'
t_DOT    = r'\.'
t_DOTS   = r'\.\.'
t_LET    = r'='
t_ADD_LET = r'\+='
t_SUB_LET = r'-='
t_MUL_LET = r'\*='
t_DIV_LET = r'/='
t_IDIV_LET= r'//='
t_SR_LET  = r'>>='
t_SL_LET  = r'<<='
t_MOD_LET = r'%='
t_EQUAL  = r'=='
t_NEQ    = r'!='
t_GEQ    = r'>='
t_LEQ    = r'<='
t_GT     = r'>'
t_LT     = r'<'
t_NOT    = r'!'
t_AND    = r'&&'
t_OR     = r'\|\|'
t_BAND   = r'&'
t_BOR    = r'\|'
t_BNOT   = r'\~'
t_HAT    = r'\^'
t_BSR    = r'>>'
t_BSL    = r'<<'
#
def t_FLOAT(t):
    r'\d+[eE][+-]?\d+|(\d*\.\d+|\d+\.\d*)([eE][+-]?\d+)?'
    t.value = float(t.value)
    return t
def t_FRACT(t):
    r'\d+/\d+'
    t.value =Fraction(t.value)
    return t
def t_HEX(t):
    r'0[xX][0-9a-fA-F]+'
    t.value =int(t.value, 16)
    return t
def t_OCT(t):
    r'0[oO][0-8]+'
    t.value =int(t.value, 8)
    return t
def t_BIN(t):
    r'0[bB][0-1]+'
    t.value =int(t.value, 2)
    return t
def t_INT(t):
    r'\d+'
    t.value = int(t.value)
    return t
def t_ID(t):
    r'[a-zA-Z_]\w*'
    t.type = reserved.get(t.value, 'ID')
    return t
def t_STR(t):
    r'"((\\"|[^"])*)"'
    t.value = (t.value)[1: - 1].encode().decode('unicode_escape')
    return t
def t_COMMENT(t):
    r'\#.*'
    pass
def t_COMMENT_(t):
    r'/\*[\s\S]*?\*/'
    pass
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)
t_ignore = ' \t'
def t_error(t):
     raise SyntaxError("Illegal charactor" + t.value[0])
#def t_eof(t):
#    more=input('...')
#    if more:
#        lexer.input(more)
#        return lexer.token()
#    return None

# builed lexer  
lexer = lex.lex() 

if __name__ == '__main__':
     # test
     while True:
        s=input('lextest>')
        if not s:continue
        lexer.input(s)
        while True:
            tok = lexer.token()
            if not tok:
                # no more tokens
                break
            print(tok)
