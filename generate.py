# -*- conig: utf-8 -*
GENERATOR_VER = 'v0.10 20.0709'
import copy
import pdb
from parse import parser
from hedder import *
# 2項演算子
op2_list = {'+':'ADD', '-':'SUB', '*':'MUL', '/':'DIV', '%':'MOD', '//':'IDIV', '**':'POW', 
            '==':'EQ', '!=':'NEQ', '>=':'GEQ', '<=':'LEQ', '>':'GT', '<':'LT', 'is':'IS',
            'in':'IN', '&':'AND', '|':'OR', '>>':'SHR', '<<':'SHL'}
# 単項演算子
op1_list = {'!':'NOT', 'UMINUS':'MINUS', '++':'INC', '--':'DEC', '~':'BNOT'}
# 関数マクロの展開
def macrofunction_expand(macro_body, param_list):
    print("macro body:", macro_body, "\nmacro_param_list:", param_list)
    def replace(Ls, Ss, Ds): # リストLs内のリストDsをリストSsに置き換える
        for i in range(len(Ls)):
            if   Ls[i] == Ds:Ls[i] = Ss
            elif isinstance(Ls[i], list):
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
    print("macrolastast:", ast)
    return codegen(ast)
# 末尾再帰処理
def tail_codegen(ast):
    # 末尾最適化は命令の最後がfunction callの場合に末尾呼び出しに変換
    if ast[0] == 'FCALL':
        code = []
        n = len(ast[2])
        for ex in ast[2]:
            code = code + codegen(ex)
        code = code + codegen(ast[1]) + ['TCALL', n]
    elif ast[0] == 'APPLY':
        code = []
        n = len(ast[1])
        for ex in ast[1]:
            code = code + codegen(ex)
        code = code + ['TAPL', n]
    # 複式の場合は最後の命令を調べる
    elif ast[0] == 'ML':
        DCL_flg = False
        code=[]
        for i in range(len(ast[1])-1):
                ex = ast[1][i]
                if ex[0] == 'DCL':
                    DCL_flg = True
                    break
                else:
                    code = code+codegen(ex) + ['POP']
        #
        if DCL_flg == False: code = code + codegen(ast[1][-1])
        else:
            var_ast = ast[1][i]
            a_arg_ast = []      # actual argument 実引数
            d_arg_ast = []      # dummy argument 仮引数
            for ex in var_ast[1]:
                print(ex)
                if ex[0] == 'VAR':
                    a_arg_ast = a_arg_ast + [['LIT',None]]
                    d_arg_ast = d_arg_ast + [ex]
                elif ex[0] == 'SET' and ex[1][0] == 'VAR':
                    a_arg_ast = a_arg_ast + [ex[2]]
                    d_arg_ast = d_arg_ast + [ex[1]]
            new_ast = ['FCALL',['LAMBDA', d_arg_ast, ['ML',ast[1][i+1:]]], a_arg_ast]
            print(new_ast)
            code = code + tail_codegen(new_ast)
    #　または命令の最後がif式の場合に適用
    elif ast[0] == 'IF':
        code = codegen(ast[1]) + \
            ['TSEL', tail_codegen(ast[2]) + ['RTN'],  tail_codegen(ast[3]) + ['RTN']] 
    else:
        code = codegen(ast)
    return code
# コード生成
def codegen(ast):
        #
        t = ast[0]
        # 複式の場合
        if t == 'ML': # [ML [expr expr ...]]
            DCL_flg = False
            code=[]
            for i in range(len(ast[1])):
                ex = ast[1][i]
                if ex[0] == 'DCL':
                    DCL_flg = True
                    break
                else:
                    code = code+codegen(ex) + ['POP']
            #
            if DCL_flg == False: code.pop()     # 複式中に変数宣言式はなかった
                                                # 余計な最後のPOPを削除
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
                code = code + codegen(new_ast)
        # if式
        elif t == 'IF':
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
            e = tail_codegen(ast[2]) + ['RTN'] #!!!!!!! tail_callしたならret->stop??!!!
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
                # 通常の関数呼び出し   
                n = len(ast[2]) # 引数の数
                for ex in ast[2]:
                    code = code + codegen(ex)
                code = code + codegen(ast[1]) + ['CALL', n]
        # applyで関数呼び出し
        elif t == 'APPLY': # [APPLY expr_list]
            n = len(ast[1])
            code=[]
            for ex in ast[1]:
                code = code + codegen(ex)
            code =code + ['APL',n]
        elif t == 'CALLCC':
                #__CODE__ = []
                code=['LDICT','__CODE__'] + codegen(ast[1]) + ['CALL',1]
        # 予期せぬASD ID
        else:
            ast_error("Unknown")
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

from eval import eval
from utility import G

def _compile(s):
    r=Ast(parser.parse(s))
    c=codegen(r)
    return c
def _code_view(c):
    return c.view()
def _eval(c):
    V=eval([], [G], c+['STOP'], 0, [], [])
    return V

G.update({'compile':_compile, 'code_view':_code_view,'eval':_eval})
#s = "repl = lambda() while True: printn((eval(conmpile(input(">"))))[0])"
from prompt_toolkit import prompt

if __name__ == '__main__':
    pdb.set_trace()
    while True:
        try:
            #s = input('test> ')
            s = prompt('test>')
        except EOFError:
            break
        if not s:
            continue
        try:
            result = Ast(parser.parse(s))
            print("AST : = ", result.view())
        except (SyntaxError, ZeroDivisionError) as e:
            print(e.__class__.__name__, e)
            continue
        try:
            code = handle_callcc(codegen(result) + ['STOP'])
            print("CODE: = ", code.view())
        except SyntaxError as e:
            print(e.__class_.__name__, e)
            continue
        try:
            v = eval([], [G], code , 0, [], [])
            print("EVAL: = ", v[0])
        except (TypeError, IndexError, KeyError, SyntaxError, ValueError, ZeroDivisionError, FileNotFoundError) as e:
            print(e.__class__.__name__, e)
            continue
