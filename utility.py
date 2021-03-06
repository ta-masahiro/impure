# -*- coding: utf-8 -* 
UTILITY_VER = 'v0.10 20.07.09'
#import copy
import math
#import cmath
import operator 
from fractions import Fraction
import sys
import os
import time
from termcolor import colored,cprint

def _list( * x):return list(x)
def _list_set(L, i, v):
    L[i] = v
    return v
def _dict(keys = None, vals = None):
    if keys is None:return {}
    elif isinstance(keys, list) and isinstance(vals, list):
        return dict(zip(map(lambda x: tuple(x) if isinstance(x, list) else x, keys), vals))
    else:return {keys:vals}
def _dict_set(D, k, v):
    #print(D, k, v)
    if isinstance(k, list):k = tuple(k)
    D[k] = v
    return v
def _dict_ref(D, k):
        return D[tuple(k)] if isinstance(k, list) else D[k]
def _dict_items(d):
    return list(d.items)
def _dict_keys(d):
    return list(d.keys())
def _dict_values(d):
    return list(d.values())
def isin(D, k):return k in D
def _dict_isin(D, k):
        if isinstance(k, list):k = tuple(k)
        return k in D
def _pop(L):return L.pop()
def _push(L, v):
    L.append(v)
    return L
def _ins(L, i, v):L.insert(i, v)
def _del(L, i):del L[i]
def _range(*arg):
    return list(range(*arg))
def _close(f):
    f.close()
def _readline(f):
    return f.readline()
def _print_n(*args):
    print(*args,end="")
def _print_f( *args):
    print(args[0].format(*args[1:]), end = '')
def _time():
    return time.time()
def _system(str):
    os.system(str)
def _forget(key):
    del G[key]
def _type(obj):return type(obj)
G = {'_':None, 'push':_push, 'pop':_pop, 'isin':isin, 'dict_isin':_dict_isin, 'range':_range, 'str':str,'dict_items':_dict_items, 'dict_keys':_dict_keys, 
        'Fraction':Fraction, 'printn':print, 'print':_print_n, 'printf':_print_f, 'input':input,'int':int,'len':len, 'list':_list, 'dict_values':_dict_values, 
        'list_set':_list_set, 'dict':_dict, 'dict_set':_dict_set, 'dict_ref':_dict_ref, 'open':open, 'close':_close,'stdin':sys.stdin, 'stdout':sys.stdout, 
        'time':_time, '_time':True, '_code':True, 'readline':_readline, 'cprint':cprint,'colored':colored, 'exit':sys.exit, 'system':_system, 'forget':_forget, 
        'ins':_ins, 'del':_del, 'type':_type}
G.update(vars(operator))
G.update(vars(math))
G['__G__'] = G
