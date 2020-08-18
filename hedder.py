# -*- config: utf-8 -*
HEDDER_VER = 'v0.10 20.07.09'
STOP, LDC, LD, INC, DEC, ADD, SUB, MUL, DIV, MOD, IDIV, POW, EQ, NEQ,\
GT, LT ,GEQ, LEQ, SET, CALL, TCALL, RTN, SEL, TSEL, JOIN, VEC, VSET, \
REF, DICT, TSET, APL, TAPL, LDF, LDICT, LDM, LDM_CL = range(36)

INST_CODE = [
    'STOP','LDC','LD','INC','DEC','ADD','SUB','MUL','DIV','MOD','IDIV','POW','EQ','NEQ'
    'GT','LT','GEQ','LEQ','SET','CALL','TCALL','RTN','SEL','TSEL','JOIN','VEC','VSET',
    'REF','DICT','TSEL','APL','TAPL','LDF','LDICT','LDM','LDM_CL',
    ]

def _view(self):
    #return str(list(self))
    r = '[ '
    for s in self:
        if isinstance(s, list):
            r = r + _view(s)
        elif isinstance(s, tuple):
            r = r + '(' +str(s[0])+' '+str(s[1])+') '
        else:
            r = r + str(s) + ' '
    return r + '] ' 

class Ast(list):
    def __repr__(self):
        return "<ast at"+str(hex(id(self)))+">"
    def view(self):
        return str(list(self))
    #def codegen(self):
    #    return Code(generate.codegen(self))

class Code(list):
    def __repr__(self):
        return "<code at "+str(hex(id(self)))+">"
    def view(self):
        return _view(self)
    #def exec(self,machine,env):
    #    return eval.eval([],env,self,0,[],[])

class Userfunction(list):
    def __repr__(self):
        return "<user function at "+str(hex(id(self)))+">"
    def view(self):
        return _view(self)

class Continuation(list):
    def __repr__(self):
        return "<continuation at "+str(hex(id(self)))+">"
    def view(self):
        return _view(list)

class Macro(list):
    def __repr__(self):
        if self[0] == 'MACRO_CL':
            return "<macro function at "+str(hex(id(self)))+">"
        elif self[0] == 'MACRO':
            return "<macro constant at "+str(hex(id(self)))+">"
    def view(self):
        return str(self[:3])
