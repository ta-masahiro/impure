# -*- config: utf-8 -*- 
EVAL_VER = 'v0.10 20.07.09'
import copy
from fractions import Fraction
from hedder import *

#STOP, LDC, LD, INC, DEC, ADD, SUB, MUL, DIV, MOD, IDIV, POW, EQ, NEQ,\
#GT, LT ,GEQ, LEQ, SET, CALL, TCALL, RTN, SEL, TSEL, JOIN, VEC, VSET, \
#REF, DICT, TSET, APL, TAPL, LDF, LDICT, LDM, LDM_CL = range(36)

#INST_CODE = [
#            'STOP','LDC','LD','INC','DEC','ADD','SUB','MUL','DIV','MOD','IDIV','POW','EQ','NEQ'
#            'GT','LT','GEQ','LEQ','SET','CALL','TCALL','RTN','SEL','TSEL','JOIN','VEC','VSET',
#            'REF','DICT','TSEL','APL','TAPL','LDF','LDICT','LDM','LDM_CL',
#            ]

def eval(S, E, C, cp, R, EE, G):
    #print(S, E,C , cp, R, EE)
    while True:
        inst = C[cp]
        #print('S:', S)
        #print('C:', C[cp:])i
        #print(E)
        #if not ('z' in E[0]):
        #print(inst)
        if inst == 'STOP':
            #print(S, R)
            #return S[ - 1]
            #return S.pop()
            return S
        cp += 1
        if inst == 'LDC':
            #
            if C[cp] == []:S.append([])
            else:S.append(C[cp])
            cp += 1
        elif inst == 'LD' : # ,LD (n,m) 
            n, m = C[cp]
            #print(n,m)
            cp +=1
            if m<0:S.append(E[n][-m-1:])
            else:S.append(E[n][m])
        #elif inst == 'LD-' : # ,LD (n,m) m<0の場合を別命令にした
        #    n, m = C[cp]
        #    #print(n,m)
        #    cp +=1
        #    S.append(E[n][-m+1:])
        elif inst == 'LDG': # ,LDG val,
            val = C[cp]
            if val in G:
                S.append(G[val])
                #print("key=",val, " val=",G[val])
                #C=C[:]
                #C[cp-1]='LDC'
                #C[cp]=G[val]
                #print("change_code:",C[cp-1],C[cp])
                cp+=1
            else: raise KeyError('name '+val+' is not defined')
        elif inst == 'INC':
            S[ - 1] += 1
        elif inst == 'DEC':
            S[ - 1]  -= 1
        elif inst == 'MINUS':
            S[ - 1] =  - S[ - 1]
        elif inst == 'NOT':
            S[ - 1] = not S[ - 1]
        elif inst == 'ADD':
            S[ - 2] += S[ - 1]
            del(S[ - 1])
            #S.append(S.pop() + S.pop())
        elif inst == 'SUB':
            S[ - 2] -= S[ - 1]
            del(S[ - 1])
        elif inst == 'MUL':
            S[ - 2]  *= S[ - 1]
            del(S[ - 1])
        elif inst == 'DIV':
            if isinstance(S[ - 2], int) and isinstance(S[ - 1], int):S[ - 2] = Fraction(S[ - 2], S[ - 1])
            else:S[ - 2] /= S[ - 1]
            del(S[ - 1])
        elif inst == 'MOD':
            S[ - 2]  %= S[ - 1]
            del(S[ - 1])
        elif inst == 'IDIV':
            S[ - 2]  //= S[ - 1]
            del(S[ - 1])
        elif inst == 'POW':
            S[ - 2] = S[ - 2] ** S[ - 1]
            del(S[ - 1])
        elif inst == 'EQ':
            S[ - 2] = (S[ - 2] == S[ - 1])
            del(S[ - 1])
        elif inst == 'NEQ':
            S[ - 2] = (S[ - 2] != S[ - 1])
            del(S[ - 1])
        elif inst == 'GEQ':
            S[ - 2] = S[ - 2] >= S[ - 1]
            del(S[ - 1])
        elif inst == 'LEQ':
            S[ - 2] = S[ - 2] <= S[ - 1]
            del(S[ - 1])
        elif inst == 'GT':
            S[ - 2] = S[ - 2] > S[ - 1]
            del(S[ - 1])
        elif inst == 'LT':
            S[ - 2] = S[ - 2] < S[ - 1]
            del(S[ - 1])
        elif inst == 'IS':
            S[ - 2] = S[ - 2] is S[ - 1]
            del(S[ - 1])
        elif inst == 'IN':
            S[ - 2] = S[ - 2] in S[ - 1]
            del(S[ - 1])
        elif inst == 'AND':
            S[ - 2] = S[ - 2] & S[ - 1 ]
            del(S[ - 1])
        elif inst == 'OR':
            S[ - 2] = S[ - 2] | S[ - 1 ]
            del(S[ - 1])
        elif inst == 'XOR':
            S[ - 2] = S[ - 2] ^ S[ - 1 ]
            del(S[ - 1])
        elif inst == 'SHR':
            S[ - 2] = S[ - 2] >> S[ - 1 ]
            del(S[ - 1])
        elif inst == 'SHL':
            S[ - 2] = S[ - 2] << S[ - 1 ]
            del(S[ - 1])
        elif inst == 'BNOT':
            S[ - 1] = ~S[ - 1 ]
        elif inst == 'VEC':
            n = C[cp]
            cp += 1
            v = S[ - n:]
            del(S[ - n:])
            S.append(v)
        elif inst == 'REF':
            ref = S.pop()
            t = S.pop()
            S.append(t[ref])
        elif inst == 'SLS':
            sl_s = S.pop()
            sl_e = S.pop()
            t = S.pop()
            S.append(t[sl_s:sl_e])
        elif inst == 'TCALL': 
            n = C[cp]
            cp += 1
            fn = S.pop()
            l = []
            if n != 0:
                #l = copy.deepcopy(S[ - n:]) #deep copyはやりすぎ！要素1個1個のcopyが望ましい
                l = (S[ - n:]) 
                del(S[ - n:])
                #for i in range(n):
                #    l = [S.pop()] + l
            #if type(fn) == list and fn[0] == 'CL':
            if isinstance(fn,Userfunction):
                E = [l] + fn[2]
                C = fn[1] 
                cp = 0
            #elif type(fn) == list and fn[0] == 'CONT':
            elif isinstance(fn,Continuation):
                S, E, C, R, EE = fn[1] + l, fn[2][:], fn[3], fn[4][:], fn[5][:]
                cp = 0
            elif n == 0:S.append(fn())
            elif n == 1:S.append(fn(l[0]))
            else: S.append(fn( * l))
        elif inst == 'CALL': 
            n = C[cp]
            cp += 1
            fn = S.pop()
            l = []
            if n != 0:
                #l = copy.deepcopy(S[ - n:])
                l = S[ - n:]
                del(S[ - n:])
                #for i in range(n):
                #    l = [S.pop()] + l
            #if type(fn) == list and fn[0] == 'CL':
            if isinstance(fn,Userfunction):
                R.append([C, cp])
                EE.append(E)
                E = [l] + fn[2]
                C = fn[1] 
                cp = 0
            #elif type(fn) == list and fn[0] == 'CONT':
            elif isinstance(fn,Continuation):
                S, E, C, R, EE = fn[1] + l, fn[2][:], fn[3], fn[4][:], fn[5][:]
                #print(fn[2])
                cp = 0
            elif n == 0:S.append(fn())
            elif n == 1:S.append(fn(l[0]))
            else: S.append(fn( * l))
        elif inst == 'TAPL': 
            n = C[cp]
            cp += 1
            fn, l = S[ - n ], S[ - n + 1 : - 1] + S[ - 1]
            del(S[ - n:])
            #print(fn, l)
            #if type(fn) == list and fn[0] == 'CL':
            if isinstance(fn,Userfunction):
                E = [l] + fn[2]
                C = fn[1] 
                cp = 0
            #elif type(fn) == list and fn[0] == 'CONT':
            elif isinstance(fn,Continuation):
                S, E, C, R, EE = fn[1] + l, fn[2][:], fn[3], fn[4][:], fn[5][:]
                cp = 0
            elif n == 0:S.append(fn())
            elif n == 1:S.append(fn(l[0]))
            else: S.append(fn( * l))
        elif inst == 'APL': 
            n = C[cp]
            cp += 1
            fn, l = S[ - n ], S[ - n + 1 : - 1] + S[ - 1]
            del(S[ - n:])
            #print(fn, l)
            #if type(fn) == list and fn[0] == 'CL':
            if isinstance(fn,Userfunction):
                R.append([C, cp])
                EE.append(E)
                E = [l] + fn[2]
                C = fn[1] 
                cp = 0
            #elif type(fn) == list and fn[0] == 'CONT':
            elif isinstance(fn,Continuation):
                S, E, C, R, EE = fn[1] + l, fn[2][:], fn[3], fn[4][:], fn[5][:]
                cp = 0
            elif n == 0:S.append(fn())
            elif n == 1:S.append(fn(l[0]))
            else: S.append(fn( * l))
        elif inst == 'RTN':
            E = EE.pop()
            C, cp = R.pop()
        elif inst=='SET': # value,set (n,m)
            n, m = C[cp]
            cp += 1
            E[n][m] = S[-1]
        elif inst == 'GSET': # value, gset key 
            key = C[cp]
            val = S[ - 1]
            #print( "val = ", v)
            #print("key = ", k)
            cp += 1
            G[key] = val
        elif inst == 'VSET': # value, vec, ind, vset 
            ind = S.pop()
            vec = S.pop()
            val = S[ - 1]
            vec[ind] = val
        elif inst == 'DCL':
            k = C[cp]
            cp += 1
            E[0][k] = None
            S.append(None)
        elif inst == 'TSEL':
            p = S.pop()
            t_exp = C[cp]
            f_exp = C[cp + 1]
            cp += 2
            #R.append([C, cp])
            cp = 0
            if p is False: C = f_exp    #!!!注意!!!False以外はTrueと判断させている!!!
            else: C = t_exp
        elif inst == 'SEL':
            p = S.pop()
            t_exp = C[cp]
            f_exp = C[cp + 1]
            cp += 2
            R.append([C, cp])
            cp = 0
            if p is False: C = f_exp
            else: C = t_exp
        elif inst == 'WHILE':
            p = S.pop()
            back = C[cp]
            loop_exp = C[cp + 1]
            if p:
                R.append([C, cp - back - 1])
                #print(C[cp - back - 1])
                C = loop_exp
                cp = 0
            else:
                cp = cp + 2 
                S.append(None)
                #print(C[cp])
        elif inst == 'JOIN':
            C, cp =R.pop() 
        elif inst == 'LDF':
            k = C[cp + 1]
            #print(k)
            S.append(Userfunction(['CL', C[cp], E]))
            cp +=1 
        elif inst == 'LDICT':
            S.append(Continuation(['CONT', S[:], E[:], C[cp], R[:], EE[:]]))
            cp += 1
        elif inst == 'LDM':                                     #############################
            S.append(Macro(['MACRO', C[cp]]))
            cp += 1
        elif inst == 'LDM_CL':                                  #############################
            S.append(Macro(['MACRO_CL', C[cp], C[cp + 1], E]))
            cp += 2
        elif inst == 'DICT':
            n = C[cp]//2
            cp += 1
            d={}
            for i in range(n):
                k=S.pop()
                if isinstance(k,list):k=tuple(k)
                v=S.pop()
                d[k] = v
            S.append(d)
        elif inst == 'DROP':
            del(S[ -1])
        #elif inst == '__CODE__':
        #    S.append('Continuation!')
        else:
            print(inst)
            #print(E)
            raise KeyError('Unknown Code:' + inst)

import pickle
import sys
 
if __name__ == '__main__':
    args = sys.argv
    if len(argv)>1:
        f=open(argv[1])
        c,g = pickle.load(f)
        eval([],[g],c,0,[],[])
