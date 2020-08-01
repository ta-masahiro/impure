# -*- conig: utf-8 -*-
GENERATOR_VER = 'v0.10 20.0709'
import sys
import copy
#import pdb
from parse import parser
from hedder import *
# 2項演算子
op2_list = {'+':'ADD', '-':'SUB', '*':'MUL', '/':'DIV', '%':'MOD', '//':'IDIV', '**':'POW', 
            '==':'EQ', '!=':'NEQ', '>=':'GEQ', '<=':'LEQ', '>':'GT', '<':'LT', 'is':'IS',
            'in':'IN', '&':'AND', '|':'OR', '>>':'SHR', '<<':'SHL', '^':'XOR'}
# 単項演算子
op1_list = {'!':'NOT', 'UMINUS':'MINUS', '++':'INC', '--':'DEC', '~':'BNOT'}
# 関数マクロの展開
def macrofunction_expand(macro_body, param_list):
    #print("macro body:", macro_body, "\nmacro_param_list:", param_list)
    def replace(Ls, Ss, Ds): # リストLs内のリストDsをリストSsに置き換える
        for i in range(len(Ls)):
            if   Ls[i] == Ds:Ls[i] = Ss
            elif isinstance(Ls[i], list) and Ls[i]!=[]:
                FLG = True
                if Ls[i][0] == 'LAMBDA':    #LAMBDAの場合は処理を変える
                    for ex in Ls[i][1]:
                        if ex == Ds:
                            FLG = False
                            break
                    if FLG : replace(Ls[i][2],Ss,Ds)
                else:replace(Ls[i], Ss, Ds)
        return
    ast = copy.deepcopy(macro_body[2])
    for Ds, Ss in zip(macro_body[1], param_list):
        replace(ast, Ss, Ds)
    if G[__debug__]:print("macrolastast:", ast)
    return codegen(ast)
# コード生成
def codegen(ast, tail = False):
        #
        t = ast[0]
        # 複式の場合
        if t == 'ML': # [ML [expr expr ...]]
            DCL_flg = False
            code=[]
            for i in range(len(ast[1]) - 1):
                ex = ast[1][i]
                if ex[0] == 'DCL':
                    DCL_flg = True
                    break
                else:
                    code = code+codegen(ex) + ['POP']
            #
            if DCL_flg == False: code = code + codegen(ast[1][ - 1], tail)     # 複式中に変数宣言式はなかった
            else:
                var_ast = ast[1][i]
                a_arg_ast = []      # actual argument 実引数
                d_arg_ast = []      # dummy argument 仮引数
                for ex in var_ast[1]:
                    #print(ex)
                    if ex[0] == 'VAR':
                        a_arg_ast = a_arg_ast + [['LIT',None]]
                        d_arg_ast = d_arg_ast + [ex]
                    elif ex[0] == 'SET' and ex[1][0] == 'VAR':
                        a_arg_ast = a_arg_ast + [ex[2]]
                        d_arg_ast = d_arg_ast + [ex[1]]
                new_ast = ['FCALL',['LAMBDA', d_arg_ast, ['ML',ast[1][i+1:]]], a_arg_ast]
                #print(new_ast)
                code = code + codegen(new_ast, tail)
        # if式
        elif t == 'IF':
            if tail: 
                code = codegen(ast[1]) + \
                    ['TSEL', codegen(ast[2], True) + ['RTN'],  codegen(ast[3], True) + ['RTN']] 
            else:
                code = codegen(ast[1]) + ['SEL', codegen(ast[2]) + ['JOIN'],  codegen(ast[3]) + ['JOIN']] 
        # 代入式
        elif t == 'SET': # [SET, exp1 exp2]
            # 左辺式になれるのはベクタ参照、関数呼び出し、変数のみ
            if ast[1][0] == 'VREF':
                #code = gen(ast[2]) + gen(ast[1][1]) + gen(ast[1][2]) + ['VSET'] #!!!
                code = codegen(ast[2]) + ['LDC', ast[1][1][1]] + codegen(ast[1][2]) + ['VSET']
            elif ast[1][0] == 'FCALL':
                x = 0 
            elif ast[1][0] == 'VAR':
                code = codegen(ast[2]) + ['LDC', ast[1][1], 'SET']
            else :
                ast_error("許されない代入先です")
        # Lambda(関数)式
        elif t == 'LAMBDA': # [LAMNBDA, arg_list, expr]
            args = []
            if ast[1] != []:  
                for arg in ast[1]:
                    if   arg == '..':
                        args = args + ['..']
                    elif arg[0] == 'VAR':
                        args = args + [arg[1]]
                    else:
                        ast_error("許されない仮引数です")
            # 末尾最適化
            e = codegen(ast[2], True) + ['RTN'] #!!!!!!! tail_callしたならret->stop??!!!
            code = ['LDF'] + [e] +[args]
        # 変数宣言
        elif t == 'DCL': # [DCL [VAR ...] ...] または [ DCL [SET ...] ...]
            code = []
            n = len(ast[1])
            for ex in ast[1]:
                if   ex[0] == 'VAR':
                    code = code + ['DCL', ex[1]] + ['POP']            
                elif ex[0] == 'SET' and ex[1][0] == 'VAR':
                    code = code + ['DCL', ex[1][0], 'POP'] + codegen(ex) + ['POP']
                else: ast_error("変数宣言には許されない式です")
            code.pop() # よけいなPOPを削除
        # WHILE
        elif t == 'WHILE': # [WHILE exp1 exp2]
            code_sexp = codegen(ast[1])
            code = code_sexp + ['WHILE', len(code_sexp),  codegen(ast[2]) + ['POP', 'JOIN']]
        # 定数マクロ
        elif t=='LDM': # [LDM expr]
            # ASTのまま積む
            code=['LDM',ast[1]]
        # 関数マクロ
        elif t=='LDM_CL': #[LDM_CL arglist expr]
            # とりあえずASTをそのまま積む
            # 将来的には、code展開する部分とそのままASTで積む部分を分ける
            code=ast
        # 2項演算子
        elif t in op2_list: # [op2, expr, expr]
            lex = codegen(ast[1])
            rex = codegen(ast[2])
            code = lex + rex + [op2_list[t]]
            # 定数畳み込み
            if len(lex) == 2 and lex[0] == 'LDC' and len(rex) == 2 and rex[0] == 'LDC':
                v = eval([], [], code + ['STOP'], 0, [], [] )
                code = ['LDC', v[ - 1]]
            else:
                pass
        # 単項演算子
        elif t in op1_list: # [op1, expr]
            ex = codegen(ast[1])
            code = ex + [op1_list[t]]
            #if ast[1][0] == 'LIT':
            if len(ex) == 2 and ex[0] == 'LDC':
                v = eval([], [], code + ['STOP'], 0, [], [])
                code = ['LDC', v[ - 1]]
            else:
                pass
        # ベクタ参照
        elif t == 'VREF': #[VREF, vector, position]
            code = codegen(ast[1]) + codegen(ast[2]) + ['REF']
        # ベクタスライス
        elif t == 'SLS': # [SLS vector start end ]
            code = codegen(ast[1]) + codegen(ast[3]) + codegen(ast[2]) + ['SLS']
        # リテラル
        elif t == 'LIT': #[LIT, value]
            if isinstance(ast[1], list):ast_error("Unknown")
            code = ['LDC', ast[1]]
        # 変数
        elif t == 'VAR': # [VAR, ID]
            if isinstance(ast[1], list): ast_error("Unknown")
            code = ['LD', ast[1]]
            # 定数マクロの展開処理
            if ast[1] in G:
                m_ast = G[ast[1]]
                #print(m_ast)
                if isinstance(m_ast,list) and m_ast != [] and m_ast[0]=='MACRO':# マクロ展開時には定義さrていること
                    code=codegen(m_ast[1])
        # vectorリテラルの生成
        elif t == 'VECT': # [ VECT, expr_list]
            code = []
            n = len(ast[1])
            for ex in ast[1]:
                code = code + codegen(ex)
            code = code + ['VEC', n]
            # 定数畳み込み
            v = []
            for ex in ast[1]:
                if codegen(ex)[0] == 'LDC' :
                    v = v + [codegen(ex)[1]]
            if len(v) == n:code = ['LDC', v]
        # 辞書リテラルの生成
        elif t == 'DICT': # [DICT pair_list]
            n = len(ast[1])
            if n== 0: code = ['LDC',{}]
            else:
                code=[]
                for ex in reversed(ast[1]):
                    code = code + codegen(ex)
                code =code + ['DICT',n]
        # 関数呼び出し
        elif t == 'FCALL': # [FCALL, function, expr_list]
            code = []
            # マクロ呼び出しかチェック
            if ast[1][0] == 'VAR' and ( ast[1][1] in G ) and isinstance(G[ast[1][1]], list) and  G[ast[1][1]][0] == 'MACRO_CL':
                # マクロの場合は展開する
                code = macrofunction_expand(G[ast[1][1]], ast[2])
            else:
                n = len(ast[2])
                for ex in ast[2]:
                    code = code + codegen(ex)
                # 通常の関数呼び出し
                if tail:
                    code = code + codegen(ast[1]) + ['TCALL', n]
                else:
                    code = code + codegen(ast[1]) + ['CALL', n]
        # applyで関数呼び出し
        elif t == 'APPLY': # [APPLY expr_list]
            n = len(ast[1])
            code=[]
            for ex in ast[1]:
                code = code + codegen(ex)
            if tail : code = code + ['TAPL', n]
            else    : code =code + ['APL',n]
        elif t == 'CALLCC':
                #__CODE__ = []
                code=['LDICT','__CODE__'] + codegen(ast[1]) + ['CALL',1]
        # 予期せぬASD ID
        else:
            ast_error("Unknown AST key")
        return Code(code)

def ast_error(msg):
    raise SyntaxError(msg)

def handle_callcc(code):
    def search_item(ls,data):
        for i in range(len(ls)):
            if isinstance(ls[i], list):return search_item (ls[i], data)
            elif ls[i]  == data:return ls, i
        return False
    c = copy.deepcopy(code)
    d = search_item(c, '__CODE__')
    if not d : return Code(c)
    L, pos = d 
    L[pos] = L[pos + 6:]
    return Code(c)

from termcolor import colored, cprint
from eval import eval
from utility import G
import pickle
def _compile(s):
    r=Ast(parser.parse(s))
    c=codegen(r)
    code=handle_callcc(c+['STOP'])
    return code
def _code_view(c):
    return c.view()
def _eval(c):
    V=eval([], [G], c+['STOP'], 0, [], [])
    return V
def _load(f_name):
    with open(f_name, 'rb') as f:
        c = pickle.load(f)
    return c
def _save(c,f_name):
    with open(f_name,'wb') as f:
        pickle.dump(c,f)

G.update({'compile':_compile, 'code_view':_code_view,'eval':_eval,'load':_load,'save':_save})

s_repl = 'repl = lambda() while True: printn((eval(compile(input(colored(">","cyan")))))[0])'
s_read = 'read = lambda(f) {S="";while (s=readline(f)) != "":S+=s;S}'
s_import = 'import = lambda(f_name) eval(compile(read(f=open(f_name))))'

G[__debug__] = False

_eval(_compile(s_read))
_eval(_compile(s_import))
_eval(_compile('import("lib.py")'))
_eval(_compile(s_repl))
#_eval(_compile('repl()'))
#from prompt_toolkit import prompt
import pdb
if __name__ == '__main__':
    args = sys.argv
    if not ('-d' in args):
        # normal mode
        G[__debug__] = False
        while True:
            try:
                s=input(colored('pure> ', "cyan"))
                if not s:continue
                result = Ast(parser.parse(s))
                code = handle_callcc(codegen(result) + ['STOP'])
                V=_eval(code)
                if V[0] is None:continue
                print(V[0])
            except Exception as e:
                cprint(e.__class__.__name__  + ':' + str(e), "red")
                #print(e)
                continue
    # debug mode
    G[__debug__] = True
    pdb.set_trace()
    while True:
        s = input(colored('debug> ', 'red'))
        if not s:continue
        result = Ast(parser.parse(s))
        print("AST : = ", result.view())
        code = handle_callcc(codegen(result) + ['STOP'])
        print("CODE: = ", code.view())
        v = eval([], [G], code , 0, [], [])
        print("EVAL: = ", v[0])
