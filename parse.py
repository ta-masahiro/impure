# -*- config: utf-8 -* 
PARSER_VER = 'v0.10 20.07.09'
import ply.yacc as yacc
from lexer import tokens
# 演算子の優先順位
precedence =  ( ('left', 'LET','ADD_LET','SUB_LET','MUL_LET','DIV_LET','IDIV_LET','SR_LET','SL_LET','MOD_LET'),
                ('left', 'OR'),
                ('left', 'AND'),
                ('right', 'NOT' ), 
                ('left', 'IS', 'IN', 'GT', 'GEQ', 'LT', 'LEQ', 'NEQ', 'EQUAL'),
                ('left', 'BOR'),
                ('left', 'BAND', 'HAT'),
                ('left', 'BSR', 'BSL'),
                ('left', 'PLUS', 'MINUS'), 
                ('left', 'TIMES', 'DIVIDE', 'PERC'),
                ('left', 'POW'), 
                ('left', 'INC', 'DEC'), 
                ('right', 'UMINUS', 'BNOT') )
# 複式
def p_expr_ml(p):
    '    expr    : LBRAC expr_list_bl RBRAC '
    p[0] = ['ML', p[2]]
# 単式
def p_expr_sg(p):
    '    expr    : factor '
    p[0] = p[1]
# if式
def p_expr_if(p):
    '''
    expr    : IF expr COL expr COL expr
            | IF expr COL expr
    '''
    if len(p) == 5: p[0] = ['IF', p[2], p[4], [] ]
    else:           p[0] = ['IF', p[2], p[4], p[6]]
# 代入式
def p_expr_set(p):
    """
    expr    : factor LET expr
            | factor ADD_LET expr
            | factor SUB_LET expr
            | factor MUL_LET expr
            | factor DIV_LET expr
            | factor IDIV_LET expr
            | factor MOD_LET expr
            | factor SR_LET expr
            | factor SL_LET expr
    """
    if   p[2] == '=' : p[0] = ['SET', p[1], p[3]]
    elif p[2] == '+=': p[0] = ['SET', p[1], ['+', p[1],p[3]]]
    elif p[2] == '-=': p[0] = ['SET', p[1], ['-', p[1],p[3]]]
    elif p[2] == '*=': p[0] = ['SET', p[1], ['*', p[1],p[3]]]
    elif p[2] == '/=': p[0] = ['SET', p[1], ['/', p[1],p[3]]]
    elif p[2] == '//=': p[0] = ['SET', p[1], ['//', p[1],p[3]]]
    elif p[2] == '%=': p[0] = ['SET', p[1], ['%', p[1],p[3]]]
    elif p[2] == '>>=': p[0] = ['SET', p[1], ['>>', p[1],p[3]]]
    elif p[2] == '<<=': p[0] = ['SET', p[1], ['<<', p[1],p[3]]]
# lambda式
def p_expr_lambda(p):
    """
    expr    : LAMBDA LPAREN RPAREN expr
            | LAMBDA LPAREN expr_list RPAREN expr
            | LAMBDA LPAREN expr_list DOTS RPAREN expr
    """
    if   len(p) == 5: p[0] = ['LAMBDA', [], p[4] ]
    elif len(p) == 6: p[0] = ['LAMBDA', p[3], p[5]]
    elif len(p) == 7: p[0] = ['LAMBDA', p[3] + ['..'], p[6]]
# ローカル変数宣言
def p_expr_dcl(p):
    '    expr    : VAR expr_list '
    p[0] = ['DCL',p[2]]
# while式
def p_expr_while(p):
    '    expr    : WHILE expr COL expr '
    p[0]=['WHILE',p[2],p[4]]
# クラス定義
def p_expr_class_def(p):
    '   expr    : CLASS expr_list '
    p[0] = ['CLASS', p[2]]
# 定数macroと関数macro
def p_expr_macro(p):
    """
    expr    : CONST expr
            | MACRO LPAREN RPAREN expr
            | MACRO LPAREN expr_list RPAREN expr
    """
    n = len(p)
    if   n == 3: p[0] = ['LDM', p[2]]
    elif n == 5: p[0] = ['LDM_CL', [], p[4]]
    elif n == 6: p[0] = ['LDM_CL', p[3], p[5]]
# 論理演算子 && ||
def p_expr_and_or(p):
    """
    expr    : expr AND expr
            | expr OR expr
    """
    if   p[2] == '&&': p[0] = ['IF', p[1], p[3], ['LIT', False]]
    elif p[2] == '||': p[0] = ['IF', p[1], ['LIT', True], p[3]]
# 2項演算子
def p_expr_2op(p):
    """
    expr    : expr PLUS expr
            | expr MINUS expr
            | expr TIMES expr
            | expr DIVIDE expr
            | expr POW expr
            | expr PERC expr
            | expr IDIV expr
            | expr IS expr
            | expr IN expr
            | expr GT expr
            | expr GEQ expr
            | expr LT expr
            | expr LEQ expr
            | expr EQUAL expr
            | expr NEQ expr
            | expr BAND expr
            | expr BOR expr
            | expr HAT expr
            | expr BNOT expr
            | expr BSR expr
            | expr BSL expr
    """
    p[0] = [p[2], p[1], p[3]]
# 左結合の単項演算子
def p_expr_1op_L(p):
    """
    expr    : NOT expr
            | BNOT expr
    """
    p[0] = [p[1], p[2]]
# 右結合の単項演算子
def p_expr_1op_R(p):
    """
    expr    : expr INC
            | expr DEC
    """
    p[0] = [p[2], p[1]]
# 単項演算子の"-"
def p_expr_UMINUS(p):
    'expr    : MINUS factor %prec UMINUS'
    p[0] = ['UMINUS', p[2]]
# 項
def p_factor(p):
    """
    factor  : nomad 
            | func_call
            | apply
            | call_cc
            | LPAREN expr RPAREN
            | property
    """
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = p[2]
# vectorの位置参照
def p_factor_vref(p):
    'factor : factor LBRAK expr RBRAK'
    p[0] = ['VREF', p[1], p[3]]
# スライス
def p_factor_slice(p):
    '''
    factor  : factor LBRAK expr COL expr RBRAK
            | factor LBRAK expr COL RBRAK
            | factor LBRAK COL expr RBRAK
            | factor LBRAK COL RBRAK
    '''
    if   len(p) == 7  :p[0] = ['SLS', p[1], p[3], p[5]]
    elif len(p) == 6  :
        if p[3] == ':':p[0] = ['SLS', p[1], ['LIT', 0], p[4]]
        else          :p[0] = ['SLS', p[1], p[3], ['LIT', None]]
    elif len(p) ==5   :p[0] = ['SLS', p[1], ['LIT', 0], ['LIT', None]]
# 単純項   
def p_nomad(p):
    """
    nomad   : lit 
            | var 
            | vector
            | dict
    """
    p[0] = p[1]
# リテラル
def p_lit(p):
    """
    lit : INT
        | HEX
        | OCT
        | BIN 
        | FLOAT 
        | FRACT 
        | STR
        | TRUE
        | FALSE
        | NONE
    """
    if   p[1] == 'True' : p[0] = ['LIT',True ]
    elif p[1] == 'False': p[0] = ['LIT',False]
    else                : p[0] = ['LIT', p[1]]
# 変数
def p_var(p):
    '    var : ID '
    p[0] = ['VAR', p[1]]
# vector
def p_vector(p):
    """
    vector  : LBRAK RBRAK
            | LBRAK expr_list RBRAK        
    """
    if len(p) == 3: p[0] = ['VECT', []]
    else: p[0] = ['VECT', p[2]]
# 辞書
def p_dict(p):
    """
    dict    : LBRAC RBRAC
            | LBRAC pair_list RBRAC
    """
    if   len(p) == 3: p[0] = ['DICT',[]]
    elif len(p) == 4: p[0] = ['DICT', p[2]]
def p_pair_list(p):
    """
    pair_list   : expr COL expr
                | pair_list CAMMA expr COL expr
    """
    if len(p) == 4: p[0] = [p[1]] + [p[3]]
    else          : p[0] = p[1] + [p[3]] + [p[5]]
# 関数呼び出し    
def p_func_call(p):
    """
    func_call   : factor LPAREN RPAREN   
                | factor LPAREN expr_list RPAREN
                | factor LPAREN expr_list DOTS RPAREN
    """
    if   len(p) == 6: p[0] = ['APPLY', [p[1]] + p[3]]
    elif len(p) == 4: p[0] = ['FCALL', p[1], []]
    else            : p[0] = ['FCALL', p[1], p[3]]
# applyによる関数呼び出し
def p_apply(p):
    '    apply   : APPLY LPAREN expr_list RPAREN '
    p[0] = ['APPLY',p[3]]
# call/cc
def p_callcc(p):
    ' call_cc : CALLCC LPAREN expr RPAREN '
    p[0] = ['CALLCC',p[3]]
# 式のリスト
def p_expr_list(p):
    """
    expr_list   : expr
                | expr_list CAMMA expr
    """
    if len(p) == 2:p[0] = [p[1]]
    else :p[0] = p[1] + [p[3]]
# 式のリスト(複式用)
def p_expr_list_bl(p):
    """
    expr_list_bl    : expr
                    | expr_list_bl SEMICOL expr
    """
    if len(p) == 2:p[0] = [p[1]]
    else :p[0] = p[1] + [p[3]]
# クラスプロパティの参照
def p_factor_property(p):
    """
    property  : factor DOT ID
    """
    p[0] = ['PROP', p[1], p[3]]
def p_error(p):
    raise SyntaxError("invalid syntax " + str(p))

parser = yacc.yacc()

if __name__ == '__main__':
    while True:
        try:
            s = input('test> ')
        except EOFError:
            break
        if not s:
            continue
        try:
            result = parser.parse(s)
            print(result)
        except SyntaxError as e:
            print(e)
            continue


