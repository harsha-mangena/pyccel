# coding: utf-8
from redbaron import RedBaron
from redbaron import StringNode, IntNode, FloatNode, ComplexNode
from redbaron import NameNode
from redbaron import AssignmentNode
from redbaron import CommentNode, EndlNode
from redbaron import ComparisonNode
from redbaron import ComparisonOperatorNode
from redbaron import UnitaryOperatorNode
from redbaron import BinaryOperatorNode, BooleanOperatorNode
from redbaron import AssociativeParenthesisNode
from redbaron import DefNode
from redbaron import ClassNode
from redbaron import TupleNode, ListNode
from redbaron import CommaProxyList
from redbaron import LineProxyList
from redbaron import NodeList
from redbaron import DotProxyList
from redbaron import ReturnNode
from redbaron import PassNode
from redbaron import DefArgumentNode
from redbaron import ForNode
from redbaron import PrintNode
from redbaron import DelNode
from redbaron import DictNode, DictitemNode
from redbaron import ForNode, WhileNode
from redbaron import IfelseblockNode, IfNode, ElseNode, ElifNode
from redbaron import DotNode, AtomtrailersNode
from redbaron import CallNode
from redbaron import CallArgumentNode
from redbaron import AssertNode
from redbaron import ExceptNode
from redbaron import FinallyNode
from redbaron import RaiseNode
from redbaron import TryNode
from redbaron import YieldNode
from redbaron import YieldAtomNode
from redbaron import BreakNode
from redbaron import GetitemNode,SliceNode




from pyccel.ast import NativeInteger, NativeFloat, NativeDouble, NativeComplex
from pyccel.ast import Nil
from pyccel.ast import Variable
from pyccel.ast import DottedName
from pyccel.ast import Assign
from pyccel.ast import Return
from pyccel.ast import Pass
from pyccel.ast import FunctionDef
from pyccel.ast import ClassDef
from pyccel.ast import For
from pyccel.ast import If
from pyccel.ast import While
from pyccel.ast import Print
from pyccel.ast import Del
from pyccel.ast import Assert
from pyccel.ast import Comment, EmptyLine
from pyccel.ast import Break
from pyccel.ast import Slice, IndexedVariable


from sympy import Symbol
from sympy import Tuple
from sympy import Add, Mul, Pow
from sympy.logic.boolalg import And, Or
from sympy.logic.boolalg import true, false
from sympy.logic.boolalg import Not
#from sympy.logic.boolalg import Boolean,
from sympy.core.relational import Eq, Ne, Lt, Le, Gt, Ge
from sympy import Integer, Float
from sympy.core.containers import Dict
from sympy.core.function import Function

# ... TODO should be moved to pyccel.ast
from sympy.core.basic import Basic

class Argument(Symbol):
    """An abstract Argument data structure."""
    pass

class ValuedArgument(Basic):
    """Represents a valued argument in the code."""

    def __new__(cls, expr, value):
        if not isinstance(expr, Argument):
            raise TypeError('Expecting an argument')
        return Basic.__new__(cls, expr, value)

    @property
    def argument(self):
        return self._args[0]

    @property
    def value(self):
        return self._args[1]

    def _sympystr(self, printer):
        sstr = printer.doprint

        argument = sstr(self.argument)
        value    = sstr(self.value)
        return '{0}={1}'.format(argument, value)
# ...

# ... utilities
from sympy import srepr
from sympy.printing.dot import dotprint

import os

def view_tree(expr):
    """Views a sympy expression tree."""

    print srepr(expr)

def export_ast(expr, filename):
    """Exports sympy AST using graphviz then convert it to an image."""

    graph_str = dotprint(expr)

    f = file(filename, 'w')
    f.write(graph_str)
    f.close()

    # name without path
    name = os.path.basename(filename)
    # name without extension
    name = os.path.splitext(name)[0]
    cmd = "dot -Tps {name}.gv -o {name}.ps".format(name=name)
    os.system(cmd)
# ...


# TODO use Double instead of Float? or add precision
def datatype_from_redbaron(node):
    """Returns the pyccel datatype of a RedBaron Node."""
    if isinstance(node, IntNode):
        return NativeInteger()
    elif isinstance(node, FloatNode):
        return NativeFloat()
    elif isinstance(node, ComplexNode):
        return NativeComplex()
    else:
        raise NotImplementedError('TODO')

def fst_to_ast(stmt):
    """Creates AST from FST."""
    if isinstance(stmt, (RedBaron,
                         CommaProxyList, LineProxyList, NodeList,
                         TupleNode, ListNode,
                         list, tuple)):
        ls = [fst_to_ast(i) for i in stmt]
        return Tuple(*ls)
    elif isinstance(stmt, DictNode):
        d = {}
        for i in stmt.value:
            if not isinstance(i, DictitemNode):
                raise TypeError('Expecting a DictitemNode')
            key   = fst_to_ast(i.key)
            value = fst_to_ast(i.value)
            # sympy does not allow keys to be strings
            if isinstance(key, str):
                raise TypeError('sympy does not allow keys to be strings')
            d[key] = value
        return Dict(d)
    elif stmt is None:
        return Nil()
    elif isinstance(stmt, str):
        return repr(stmt)
    elif isinstance(stmt, StringNode):
        return repr(stmt.value)
    elif isinstance(stmt, IntNode):
        return Integer(stmt.value)
    elif isinstance(stmt, FloatNode):
        return Float(stmt.value)
    elif isinstance(stmt, ComplexNode):
        raise NotImplementedError('ComplexNode not yet available')
    elif isinstance(stmt, AssignmentNode):
        lhs = fst_to_ast(stmt.target)
        rhs = fst_to_ast(stmt.value)
        return Assign(lhs, rhs)
    elif isinstance(stmt, NameNode):
        if stmt.value == 'None':
            return Nil()
        elif stmt.value == 'True':
            return true
        elif stmt.value == 'False':
            return false
        else:
            return Symbol(stmt.value)
    elif isinstance(stmt, DelNode):
        arg = fst_to_ast(stmt.value)
        return Del(arg)
    elif isinstance(stmt, UnitaryOperatorNode):
        target = fst_to_ast(stmt.target)
        if stmt.value == 'not':
            return Not(target)
        elif stmt.value == '+':
            return target
        elif stmt.value == '-':
            return -target
        elif stmt.value == '~':
            raise ValueError('Invert unary operator is not covered by Pyccel.')
        else:
            raise ValueError('unknown/unavailable unary operator '
                             '{node}'.format(node=type(stmt.value)))
    elif isinstance(stmt, (BinaryOperatorNode, BooleanOperatorNode)):
        first  = fst_to_ast(stmt.first)
        second = fst_to_ast(stmt.second)
        if stmt.value == '+':
            return Add(first, second)
        elif stmt.value == '*':
            return Mul(first, second)
        elif stmt.value == '-':
            second = Mul(-1, second)
            return Add(first, second)
        elif stmt.value == '/':
            second = Pow(second, -1)
            return Mul(first, second)
        elif stmt.value == 'and':
            return And(first, second)
        elif stmt.value == 'or':
            return Or(first, second)
        else:
            raise ValueError('unknown/unavailable binary operator '
                             '{node}'.format(node=type(stmt.value)))
    elif isinstance(stmt, ComparisonOperatorNode):
        if stmt.first == '==':
            return '=='
        elif stmt.first == '!=':
            return '!='
        elif stmt.first == '<':
            return '<'
        elif stmt.first == '>':
            return '>'
        elif stmt.first == '<=':
            return '<='
        elif stmt.first == '>=':
            return '>='
        else:
            raise ValueError('unknown comparison operator {}'.format(stmt.first))
    elif isinstance(stmt, ComparisonNode):
        first  = fst_to_ast(stmt.first)
        second = fst_to_ast(stmt.second)
        op     = fst_to_ast(stmt.value)
        if op == '==':
            return Eq(first, second)
        elif op == '!=':
            return Ne(first, second)
        elif op == '<':
            return Lt(first, second)
        elif op == '>':
            return Gt(first, second)
        elif op == '<=':
            return Le(first, second)
        elif op == '>=':
            return Ge(first, second)
        else:
            raise ValueError('unknown/unavailable binary operator '
                             '{node}'.format(node=type(op)))
    elif isinstance(stmt, PrintNode):
        expr = fst_to_ast(stmt.value)
        return Print(expr)
    elif isinstance(stmt, AssociativeParenthesisNode):
        return fst_to_ast(stmt.value)
    elif isinstance(stmt, DefArgumentNode):
        arg = Argument(str(stmt.target))
        if stmt.value is None:
            return arg
        else:
            value = fst_to_ast(stmt.value)
            return ValuedArgument(arg, value)
    elif isinstance(stmt, ReturnNode):
        return Return(fst_to_ast(stmt.value))
    elif isinstance(stmt, PassNode):
        return Pass()
    elif isinstance(stmt, DefNode):
        # TODO results must be computed at the decoration stage
        # TODO check all inputs and which ones would be treated in stage 1 or 2
        name        = fst_to_ast(stmt.name)
        arguments   = fst_to_ast(stmt.arguments)
        results     = []
        body        = fst_to_ast(stmt.value)
        local_vars  = []
        global_vars = []
        cls_name    = None
        hide        = False
        kind        = 'function'
        imports     = []
        return FunctionDef(name, arguments, results, body,
                           local_vars=local_vars, global_vars=global_vars,
                           cls_name=cls_name, hide=hide,
                           kind=kind, imports=imports)
    elif isinstance(stmt, ClassNode):
        name = fst_to_ast(stmt.name)
        methods = [i for i in stmt.value if isinstance(i, DefNode)]
        methods = fst_to_ast(methods)
        attributes = methods[0].arguments
        return ClassDef(name, attributes, methods)

    elif isinstance(stmt, AtomtrailersNode):
         return fst_to_ast(stmt.value)
    elif isinstance(stmt, GetitemNode):
         return fst_to_ast(stmt.value)
    elif isinstance(stmt,SliceNode):
         upper = fst_to_ast(stmt.upper)
         lower = fst_to_ast(stmt.lower)
         if upper and lower:
             return Slice(lower,upper)
         elif lower:
             return Slice(lower,None)
         elif upper:
             return Slice(None,upper)
    elif isinstance(stmt, DotProxyList):
        # TODO handle dot trailers
        # we first get the index of the call node
        s=[isinstance(i.next, DotNode) for i in stmt]
        if not any(s):
            # case of no DotNode
            # TODO fix bug of case IndexedVariable before DottedNode
            ls=[fst_to_ast(i) for i in stmt]
            name = str(ls[0])
            args = ls[1:]
            
            return IndexedVariable(name)[args]
        call = None
        ls = []
        for i, s in enumerate(stmt):
            if isinstance(s, CallNode):
                call = stmt[i]
                break
            # we only take the string representation
            # since we will use DottedName later
            #ls.append(fst_to_ast(s))
            ls.append(repr(s))
            i += 1

        # the function name (without trailer) is the previous node to the call
        if len(ls) == 1:
            name = ls[0]
        else:
            name = DottedName(*ls)

        # dots may lead to a dotted name or a call to a method
        if call is None:
            return name
        elif isinstance(call, CallNode):
            # in this case, name must be a string
            args   = fst_to_ast(call)
            f_name = str(name)
            return Function(f_name)(*args)
        else:
            raise ValueError('Expecting a method call or a dotted name')
    elif isinstance(stmt, CallNode):
        args = fst_to_ast(stmt.value)
        return args
    elif isinstance(stmt, CallArgumentNode):
        return fst_to_ast(stmt.value)
    elif isinstance(stmt, ForNode):
        target = fst_to_ast(stmt.iterator)
        iter   = fst_to_ast(stmt.target)
        body   = fst_to_ast(stmt.value)
        strict = True
        return For(target, iter, body, strict=strict)
    elif isinstance(stmt, IfelseblockNode):
        args = fst_to_ast(stmt.value)
        return If(*args)
    elif isinstance(stmt,(IfNode, ElifNode)):
        test = fst_to_ast(stmt.test)
        body = fst_to_ast(stmt.value)
        return Tuple(test, body)
    elif isinstance(stmt, ElseNode):
        test = True
        body = fst_to_ast(stmt.value)
        return Tuple(test, body)
    elif isinstance(stmt, WhileNode):
        test = fst_to_ast(stmt.test)
        body = fst_to_ast(stmt.value)
        return While(test, body)
    elif isinstance(stmt, AssertNode):
        expr = fst_to_ast(stmt.value)
        return Assert(expr)
    elif isinstance(stmt, EndlNode):
        return EmptyLine()
    elif isinstance(stmt, CommentNode):
        # TODO must check if it is a header or not
        return Comment(stmt.value)
    elif isinstance(stmt, BreakNode):
        return Break()
    elif isinstance(stmt, (ExceptNode, FinallyNode, RaiseNode, TryNode, YieldNode, YieldAtomNode)):
        # TODO add appropriate message errors and refeer to Pyccel rules
        raise NotImplementedError('{node} is not covered by pyccel'.format(node=type(stmt)))
    else:
        raise NotImplementedError('{node} not yet available'.format(node=type(stmt)))


def infere_type(expr):
    """
    type inference for expressions
    """
    d_var = {}
    d_var['datatype'] = None
    d_var['allocatable'] = None
    d_var['shape'] = None
    d_var['rank'] = None

    if isinstance(expr, Integer):
        d_var['datatype'] = 'int'
        d_var['allocatable'] = False
        d_var['rank'] = 0
        return d_var
#    elif isinstance(expr, Float):
#        # TODO choose precision
#        d_var['datatype']    = DEFAULT_TYPE
#        d_var['allocatable'] = False
#        d_var['rank']        = 0
#        return d_var
#    elif isinstance(expr, (BooleanTrue, BooleanFalse)):
#        d_var['datatype']    = NativeBool()
#        d_var['allocatable'] = False
#        d_var['rank']        = 0
#        return d_var
    else:
        raise NotImplementedError('{expr} not yet available'.format(expr=type(expr)))



def annotate(expr, **settings):
    """Annotates the AST."""
    if isinstance(expr, (list, tuple, Tuple)):
        ls = [annotate(i, **settings) for i in expr]
        return Tuple(*ls)
    elif isinstance(expr, (Integer, Float)):
        return expr
    elif isinstance(expr, Symbol):
        d_var = settings.pop('d_var', None)
        if d_var is None:
            raise NotImplementedError('TODO')
        name = expr.name
        dtype = d_var.pop('datatype')
        var = Variable(dtype, name, **d_var)
        return var
    elif isinstance(expr, Assign):
        d_var = infere_type(expr.rhs)
        settings['d_var'] = d_var
        rhs = annotate(expr.rhs, **settings)
        lhs = annotate(expr.lhs, **settings)
        return Assign(lhs, rhs, strict=False)
    else:
        raise NotImplementedError('{expr} not yet available'.format(expr=type(expr)))



def read_file(filename):
    """Returns the source code from a filename."""
    f = open(filename)
    code = f.read()
    f.close()
    return code

######################################################
if __name__ == '__main__':
    import sys

    try:
        filename = sys.argv[1]
    except:
        raise ValueError('Expecting an argument for filename')

    code = read_file(filename)
    red  = RedBaron(code)

    print('----- FST -----')
    for stmt in red:
        print stmt
    #    print type(stmt)
    print('---------------')

    # converts redbaron fst to sympy ast
    ast = fst_to_ast(red)

    #print('----- AST -----')
    #for expr in ast:
    #    print expr
#    #    print '\t', type(expr.rhs)
    #print('---------------')

    view_tree(ast)

    export_ast(ast, filename='ast_stage_1.gv')

    settings = {}
    ast = annotate(ast, **settings)

    export_ast(ast, filename='ast_stage_2.gv')
