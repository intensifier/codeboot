# File: Grammar_novice_actions.py

{
"allowed_modes": {"exec": "file_input",
                  "eval": "eval_input",
                  "single": "single_input"}

,"gen_prefix": "py_"
,"gen_parse_prefix": "py_parse_"

,"prelude":
"""from pyinterp.zast._zast import *

def set_end_ast(ast, end_ast):
    return set_end(ast, end_ast.end_lineno, end_ast.end_col_offset)

def set_ctx(targets, ctx):
    for i in range(len(targets)):
        set_ctx1(targets[i], ctx)

def set_ctx1(t, ctx):
    t.ctx = ctx
    if isinstance(t, Tuple):
        set_ctx(t.elts, ctx)
    elif isinstance(t, List):
        set_ctx(t.elts, ctx)

def check_assignable(ts, t):
    if isinstance(t, Constant):
        val = t.value
        if val is False:
            py_syntax_error_ast(ts, t, 'cannot assign to False')
        elif val is True:
            py_syntax_error_ast(ts, t, 'cannot assign to True')
        elif val is None:
            py_syntax_error_ast(ts, t, 'cannot assign to None')
#TODO: enable when Ellipsis implemented
#        elif val is Ellipsis:
#            py_syntax_error_ast(ts, t, 'cannot assign to Ellipsis')
        else:
            py_syntax_error_ast(ts, t, 'cannot assign to literal')
    elif isinstance(t, BinOp) or isinstance(t, UnaryOp) or isinstance(t, BoolOp):
        py_syntax_error_ast(ts, t, 'cannot assign to operator')
    elif isinstance(t, Tuple):
        for i in range(len(t.elts)):
            check_assignable(ts, t.elts[i])
    elif isinstance(t, List):
        for i in range(len(t.elts)):
            check_assignable(ts, t.elts[i])
    elif isinstance(t, Dict):
        py_syntax_error_ast(ts, t, 'cannot assign to dict display')
    elif isinstance(t, Call):
        py_syntax_error_ast(ts, t, 'cannot assign to function call')
    elif isinstance(t, IfExp):
        py_syntax_error_ast(ts, t, 'cannot assign to conditional expression')
    elif isinstance(t, Compare):
        py_syntax_error_ast(ts, t, 'cannot assign to comparison')
    elif isinstance(t, Lambda):
        py_syntax_error_ast(ts, t, 'cannot assign to lambda')

def py_syntax_error_ast(ts, ast, msg):
    if ts.context and dict_has(ts.context, 'syntaxError'):
        ts.context.syntaxError(ast.lineno-1, ast.col_offset, ast.end_lineno-1, ast.end_col_offset, msg)

def parse_function_signature(ts, posonly_and_default, args_and_defaults, vararg, kwonly_and_defaults, kwarg):
    posonlyargs = []
    args = []
    defaults = []
    for pair in posonly_and_default:
        posonlyargs.append(pair[0])
        def_val = pair[1]
        if def_val is None:
            if len(defaults) > 0:
                return py_syntax_error(ts, "non-default argument follows default argument")
        else:
            defaults.append(def_val)

    for pair in args_and_defaults:
        args.append(pair[0])
        def_val = pair[1]
        if def_val is None:
            if len(defaults) > 0:
                return py_syntax_error(ts, "non-default argument follows default argument")
        else:
            defaults.append(def_val)

    kwonlyargs = []
    kw_defaults = []
    for pair in kwonly_and_defaults:
        kwonlyargs.append(pair[0])
        kw_defaults.append(pair[1])

    return arguments(args, posonlyargs, vararg, kwonlyargs, kw_defaults, kwarg, defaults)
"""



,"single_input: stmt ENDMARKER.":
    ["return Module(stmt1,[])"] ### should be  ["return Interactive(stmt1)"]


,"file_input: stmts ENDMARKER.":
   ["return Module(stmts1,[])"]


,"eval_input: .testlist NEWLINE* ENDMARKER":
    ["as_list = False"]
,"eval_input: testlist NEWLINE* ENDMARKER.":
    ["return Expression(testlist1)"]


,"stmts: .(NEWLINE | stmt)*":
   ["stmts = []",""]
,"stmts: (NEWLINE | stmt.)*":
   ["stmts.extend(stmt1)"]
,"stmts: (NEWLINE | stmt)*.":
   ["return stmts"]


,"funcdef: .'def' NAME parameters ['->' test] ':' [TYPE_COMMENT] func_body_suite":
   ["lineno = get_lineno(ts); col_offset = get_col_offset(ts)\n"
    "type_comment = None"]
,"funcdef: 'def' .NAME parameters ['->' test] ':' [TYPE_COMMENT] func_body_suite":
   ["name = token(ts)"]
,"funcdef: 'def' NAME parameters ['->' test] ':' [TYPE_COMMENT] func_body_suite.":
   ["ast = FunctionDef(name, parameters1, func_body_suite1, [], None, type_comment)\n"
    "set_start(ast, lineno, col_offset)\n"
    "set_end_ast(ast, func_body_suite1[-1])\n"
    "return ast"]


,"parameters: '(' .[varargslist] ')'":
   ["varargslist1 = None"]
,"parameters: '(' [varargslist] ')'.":
   ["if varargslist1 is None:\n"
    "    return arguments([], [], None, [], [], None, [])\n"
    "else:\n"
    "    return varargslist1"]


,"typedargslist: .NAME (',' NAME)*":
   ["a = arg(token(ts),None,None)\n"
    "set_start_end_1token(ts, a)\n"
    "args = [a]"]
,"typedargslist: NAME (',' .NAME)*":
   ["a = arg(token(ts),None,None)\n"
    "set_start_end_1token(ts, a)\n"
    "args.append(a)"]
,"typedargslist: NAME (',' NAME)*.":
   ["return arguments(args, [], None, [], [], None, [])"]


,"simple_arg: .'NAME' ['=' test]":
    ["a = arg(token(ts), None, None); default_ = None\n"
     "set_start_end_1token(ts, a)"]
,"simple_arg: 'NAME' ['=' test.]":
    ["default_ = test1"]
,"simple_arg: 'NAME' ['=' test].":
    ["return [a, default_]"]

,"kwargs: '**' .'NAME' [',']":
    ["a = arg(token(ts), None, None)\n"
     "set_start_end_1token(ts, a)"]
,"kwargs: '**' 'NAME' [','].":
    ["return a"]

,"args: '*' .['NAME'] [args_tail]":
    ["vararg = None"]
,"args: '*' [.'NAME'] [args_tail]":
    ["vararg = set_start_end_1token(ts, arg(token(ts), None, None))"]
,"args: '*' ['NAME'] .[args_tail]":
    ["kw_args = None"]
,"args: '*' ['NAME'] [args_tail.]":
    ["kw_args = args_tail1"]
,"args: '*' ['NAME'] [args_tail].":
    ["if kw_args is None:\n"
     "    return [vararg, [], None]\n"
     "else:\n"
     "    return list_concat([vararg], kw_args) # [vararg, kw_only, kwarg]"]

,"args_tail: ',' args_tail_after_comma.":
    ["return args_tail_after_comma1"]

,"args_tail_after_comma: simple_arg [',' args_tail_after_comma.]":
    ["args_tail_after_comma1[0].append(simple_arg1) # must be reversed later\n"
     "return args_tail_after_comma1"]
,"args_tail_after_comma: simple_arg [',' args_tail_after_comma].":
    ["return [[simple_arg1], None]"]
,"args_tail_after_comma: kwargs.":
    ["return [[], kwargs1]"]

,"varargslist_before_slash: args.":
    ["return list_concat([[], []], args1), False"]
,"varargslist_before_slash: kwargs.":
    ["return [[], [], None, [], kwargs1], False  # [posonly, args, vararg, kw_only, kwargs]"]
,"varargslist_before_slash: simple_arg. [varargslist_before_slash_tail]":
    ["varargslist_before_slash_tail1 = None"]
,"varargslist_before_slash: simple_arg [varargslist_before_slash_tail].":
    ["if varargslist_before_slash_tail1 is None:\n"
     "    return [[], [simple_arg1], None, [], None], False\n"
     "else:\n"
     "    tail = varargslist_before_slash_tail1[0]\n"
     "    before_slash = varargslist_before_slash_tail1[1]\n"
     "    if before_slash:\n"
     "        tail[0].append(simple_arg1)\n"
     "    else:\n"
     "        tail[1].append(simple_arg1)\n"
     "    return varargslist_before_slash_tail1"]

,"varargslist_before_slash_tail: ',' [varargslist_before_slash. | '/' [args | kwargs | ',' [varargslist_after_slash]]]":
    ["return varargslist_before_slash1"]
,"varargslist_before_slash_tail: ',' [varargslist_before_slash | '/' [args. | kwargs | ',' [varargslist_after_slash]]]":
    ["return list_concat([[], []], args1), True"]
,"varargslist_before_slash_tail: ',' [varargslist_before_slash | '/' [args | kwargs. | ',' [varargslist_after_slash]]]":
    ["return [[], [], None, [], kwargs1], True"]
,"varargslist_before_slash_tail: ',' [varargslist_before_slash | '/' [args | kwargs | ',' [varargslist_after_slash.]]]":
    ["return varargslist_after_slash1, True"]
,"varargslist_before_slash_tail: ',' [varargslist_before_slash | '/' [args | kwargs | ',' [varargslist_after_slash]].]":
    ["return [[], [], None, [], None], True"]


,"varargslist_after_slash: simple_arg. [varargslist_after_slash_tail]":
    ["varargslist_after_slash_tail1 = None"]
,"varargslist_after_slash: simple_arg [varargslist_after_slash_tail].":
    ["if varargslist_after_slash_tail1 is None:\n"
     "    return [[], [simple_arg1], None, [], None] # [posonly, args, vararg, kw_only, kwargs]\n"
     "else:\n"
     "    varargslist_after_slash_tail1[1].append(simple_arg1)\n"
     "    return varargslist_after_slash_tail1"]


,"varargslist_after_slash_tail: ',' [varargslist_after_slash. | args | kwargs]":
    ["return varargslist_after_slash1"]
,"varargslist_after_slash_tail: ',' [varargslist_after_slash | args. | kwargs]":
    ["return list_concat([[], []], args1)"]
,"varargslist_after_slash_tail: ',' [varargslist_after_slash | args | kwargs.]":
    ["return [[], [], None, [], kwargs1]"]
,"varargslist_after_slash_tail: ',' [varargslist_after_slash | args | kwargs].":
    ["return [[], [], None, [], None] # [posonly, args, vararg, kw_only, kwargs]"]


,"varargslist: varargslist_before_slash.":
    ["parsed_signature = varargslist_before_slash1[0]  # second element indicates if a slash was seen, it is no longer needed at this point\n"
     "posonly_and_default = list_reversed(parsed_signature[0])\n"
     "args_and_defaults = list_reversed(parsed_signature[1])\n"
     "vararg = parsed_signature[2]\n"
     "kwonly_and_defaults = list_reversed(parsed_signature[3])\n"
     "kwarg = parsed_signature[4]\n"
     "return parse_function_signature(ts, posonly_and_default, args_and_defaults, vararg, kwonly_and_defaults, kwarg)"]


,"func_body_suite: simple_stmt.":
   ["return simple_stmt1"]

,"func_body_suite: NEWLINE [TYPE_COMMENT NEWLINE] INDENT. stmt+ DEDENT":
   ["stmts = []"]
,"func_body_suite: NEWLINE [TYPE_COMMENT NEWLINE] INDENT stmt.+ DEDENT":
   ["stmts.extend(stmt1)"]
,"func_body_suite: NEWLINE [TYPE_COMMENT NEWLINE] INDENT stmt+ DEDENT.":
   ["return stmts"]


,"stmt: simple_stmt.":
   ["return simple_stmt1"]

,"stmt: compound_stmt.":
   ["return [compound_stmt1]"]


,"simple_stmt: small_stmt NEWLINE.":
   ["return [small_stmt1]"]


,"small_stmt: expr_stmt.":
   ["return expr_stmt1"]

,"small_stmt: del_stmt.":
   ["return del_stmt1"]

,"small_stmt: pass_stmt.":
   ["return pass_stmt1"]

,"small_stmt: flow_stmt.":
   ["return flow_stmt1"]

,"small_stmt: import_stmt.":
   ["return import_stmt1"]

,"small_stmt: global_stmt.":
   ["return global_stmt1"]

,"small_stmt: nonlocal_stmt.":
   ["return nonlocal_stmt1"]

,"small_stmt: assert_stmt.":
   ["return assert_stmt1"]


,"expr_stmt: .test":
   ["lineno = get_lineno(ts); col_offset = get_col_offset(ts)"]
,"expr_stmt: test.":
   ["ast = Expr(test1)\n"
    "return set_start_end(ts, lineno, col_offset, ast)"]


,"expr_stmt: .testlist_star_expr (annassign | augassign (yield_expr|testlist) | [('=' (yield_expr|testlist_star_expr))+ [TYPE_COMMENT]] )":
   ["lineno = get_lineno(ts); col_offset = get_col_offset(ts)"]
,"expr_stmt: testlist_star_expr. (annassign | augassign (yield_expr|testlist) | [('=' (yield_expr|testlist_star_expr))+ [TYPE_COMMENT]] )":
   ["targets = [testlist_star_expr1]\n"
    "type_comment = None"]
,"expr_stmt: testlist_star_expr (annassign | augassign (yield_expr|.testlist) | [('=' (yield_expr|testlist_star_expr))+ [TYPE_COMMENT]] )":
   ["as_list = False"]
,"expr_stmt: testlist_star_expr (annassign | augassign (yield_expr|testlist) | [('=' (yield_expr|testlist_star_expr))+. [TYPE_COMMENT]] )":
   ["ast = Assign(targets, testlist_star_expr2, type_comment)\n"
    "set_ctx(targets, Store())\n"
    "return set_start_end(ts, lineno, col_offset, ast)"]
,"expr_stmt: testlist_star_expr (annassign | augassign (yield_expr|testlist) | [('=' (yield_expr|testlist_star_expr))+ [TYPE_COMMENT]]. )":
   ["ast = Expr(testlist_star_expr1)\n"
    "return set_start_end(ts, lineno, col_offset, ast)"]


,"star_expr: .'*' expr":
   ["lineno = get_lineno(ts); col_offset = get_col_offset(ts)"]
,"star_expr: '*' expr.":
   ["ast = Starred(expr1, Load())\n"
    "return set_start_end(ts, lineno, col_offset, ast)"]


,"del_stmt: .'del' exprlist":
   ["lineno = get_lineno(ts); col_offset = get_col_offset(ts)"]
,"del_stmt: 'del' .exprlist":
   ["as_list = True"]
,"del_stmt: 'del' exprlist.":
   ["ast = Delete(exprlist1[0])\n"
    "set_ctx(exprlist1[0], Del())\n"
    "return set_start_end(ts, lineno, col_offset, ast)"]


,"pass_stmt: .'pass'":
   ["ast = set_start_end_1token(ts, Pass())"]
,"pass_stmt: 'pass'.":
   ["return ast"]


,"flow_stmt: break_stmt.":
   ["return break_stmt1"]

,"flow_stmt: continue_stmt.":
   ["return continue_stmt1"]

,"flow_stmt: return_stmt.":
   ["return return_stmt1"]

,"flow_stmt: raise_stmt.":
   ["return raise_stmt1"]

,"flow_stmt: yield_stmt.":
   ["return yield_stmt1"]


,"break_stmt: .'break'":
   ["ast = set_start_end_1token(ts, Break())"]
,"break_stmt: 'break'.":
   ["return ast"]


,"continue_stmt: .'continue'":
   ["ast = set_start_end_1token(ts, Continue())"]
,"continue_stmt: 'continue'.":
   ["return ast"]


,"return_stmt: .'return' [testlist_star_expr]":
   ["lineno = get_lineno(ts); col_offset = get_col_offset(ts)\n"
    "value = None"]
,"return_stmt: 'return' [testlist_star_expr.]":
   ["value = testlist_star_expr1\n"]
,"return_stmt: 'return' [testlist_star_expr].":
   ["ast = Return(value)\n"
    "return set_start_end(ts, lineno, col_offset, ast)"]


,"yield_stmt: .yield_expr":
   ["lineno = get_lineno(ts); col_offset = get_col_offset(ts)"]
,"yield_stmt: yield_expr.":
   ["ast = Expr(yield_expr1)\n"
    "return set_start_end(ts, lineno, col_offset, ast)"]

,"yield_expr: .'yield' [yield_arg]":
   ["lineno = get_lineno(ts); col_offset = get_col_offset(ts)"]
,"yield_expr: 'yield' [yield_arg.]":
   ["return yield_arg1"]
,"yield_expr: 'yield' [yield_arg].":
   ["ast = Yield(None)\n"
    "return set_start_end(ts, lineno, col_offset, ast)"]


,"augassign: '+='.":   ["return Add()"]

,"augassign: '-='.":   ["return Sub()"]

,"augassign: '*='.":   ["return Mult()"]

,"augassign: '@='.":   ["return MatMult()"]

,"augassign: '/='.":   ["return Div()"]

,"augassign: '%='.":   ["return Mod()"]

,"augassign: '&='.":   ["return BitAnd()"]

,"augassign: '|='.":   ["return BitOr()"]

,"augassign: '^='.":   ["return BitXor()"]

,"augassign: '<<='.":  ["return LShift()"]

,"augassign: '>>='.":  ["return RShift()"]

,"augassign: '**='.":  ["return Pow()"]

,"augassign: '//='.":  ["return FloorDiv()"]


,"raise_stmt: .'raise' [test ['from' test]]":
   ["lineno = get_lineno(ts); col_offset = get_col_offset(ts)\n"
    "exc = None\n"
    "cause = None"]
,"raise_stmt: 'raise' [test. ['from' test]]":
   ["exc = test1"]
,"raise_stmt: 'raise' [test ['from' test.]]":
   ["cause = test2"]
,"raise_stmt: 'raise' [test ['from' test]].":
   ["ast = Raise(exc, cause)\n"
    "return set_start_end(ts, lineno, col_offset, ast)"]


,"test: .or_test ['if' or_test 'else' test]":
   ["lineno = get_lineno(ts); col_offset = get_col_offset(ts)"]
,"test: or_test ['if' or_test 'else' test.]":
   ["ast = IfExp(or_test2, or_test1, test1)\n"
    "return set_start_end(ts, lineno, col_offset, ast)"]
,"test: or_test ['if' or_test 'else' test].":
   ["return or_test1"]


,"test: lambdef.":
   ["return lambdef1"]


,"lambdef: .'lambda' [varargslist] ':' test":
   ["lineno = get_lineno(ts); col_offset = get_col_offset(ts)\n"
    "args = None"]
,"lambdef: 'lambda' [varargslist.] ':' test":
   ["args = varargslist1"]
,"lambdef: 'lambda' [varargslist] ':' test.":
   ["if args is None:\n"
    "    args = arguments([], [], None, [], [], None, [])\n"
    "ast = Lambda(args, test1)\n"
    "return set_start_end(ts, lineno, col_offset, ast)"]


,"or_test: .and_test ('or' and_test)*":
   ["lineno = get_lineno(ts); col_offset = get_col_offset(ts)"]
,"or_test: and_test. ('or' and_test)*":
   ["asts = [and_test1]"]
,"or_test: and_test ('or' and_test.)*":
   ["asts.append(and_test2)"]
,"or_test: and_test ('or' and_test)*.":
   ["if len(asts) == 1:\n"
    "    return asts[0]\n"
    "else:\n"
    "    ast = BoolOp(Or(), asts)\n"
    "    return set_start_end(ts, lineno, col_offset, ast)"]


,"and_test: .not_test ('and' not_test)*":
   ["lineno = get_lineno(ts); col_offset = get_col_offset(ts)"]
,"and_test: not_test. ('and' not_test)*":
   ["asts = [not_test1]"]
,"and_test: not_test ('and' not_test.)*":
   ["asts.append(not_test2)"]
,"and_test: not_test ('and' not_test)*.":
   ["if len(asts) == 1:\n"
    "    return asts[0]\n"
    "else:\n"
    "    ast = BoolOp(And(), asts)\n"
    "    return set_start_end(ts, lineno, col_offset, ast)"]


,"not_test: .'not' not_test":
   ["lineno = get_lineno(ts); col_offset = get_col_offset(ts)"]
,"not_test: 'not' not_test.":
   ["ast = UnaryOp(Not(), not_test1)\n"
    "return set_start_end(ts, lineno, col_offset, ast)"]


,"not_test: comparison.":
   ["return comparison1"]


,"comparison: .expr (comp_op expr)*":
   ["lineno = get_lineno(ts); col_offset = get_col_offset(ts)"]
,"comparison: expr. (comp_op expr)*":
   ["ops = []\n"
    "comparators = []"]
,"comparison: expr (comp_op expr.)*":
   ["ops.append(comp_op1)\n"
    "comparators.append(expr2)"]
,"comparison: expr (comp_op expr)*.":
   ["if len(ops) == 0:\n"
    "    return expr1\n"
    "else:\n"
    "    ast = Compare(expr1, ops, comparators)\n"
    "    return set_start_end(ts, lineno, col_offset, ast)"]


,"comp_op: '<'.":          ["return Lt()"]

,"comp_op: '>'.":          ["return Gt()"]

,"comp_op: '>='.":         ["return GtE()"]

,"comp_op: '<='.":         ["return LtE()"]

,"comp_op: '=='.":         ["return Eq()"]

,"comp_op: '!='.":         ["return NotEq()"]

,"comp_op: '<>'.":         ["return NotEq()"]

,"comp_op: 'is' ['not'.]": ["return IsNot()"]

,"comp_op: 'is' ['not'].": ["return Is()"]

,"comp_op: 'in'.":         ["return In()"]

,"comp_op: 'not' 'in'.":   ["return NotIn()"]


,"expr: .xor_expr ('|' xor_expr)*":
   ["lineno = get_lineno(ts); col_offset = get_col_offset(ts)"]
,"expr: xor_expr. ('|' xor_expr)*":
   ["ast = xor_expr1"]
,"expr: xor_expr ('|' xor_expr.)*":
   ["ast = BinOp(ast, BitOr(), xor_expr2)\n"
    "set_start_end(ts, lineno, col_offset, ast)"]
,"expr: xor_expr ('|' xor_expr)*.":
   ["return ast"]


,"xor_expr: .and_expr ('^' and_expr)*":
   ["lineno = get_lineno(ts); col_offset = get_col_offset(ts)"]
,"xor_expr: and_expr. ('^' and_expr)*":
   ["ast = and_expr1"]
,"xor_expr: and_expr ('^' and_expr.)*":
   ["ast = BinOp(ast, BitXor(), and_expr2)\n"
    "set_start_end(ts, lineno, col_offset, ast)"]
,"xor_expr: and_expr ('^' and_expr)*.":
   ["return ast"]


,"and_expr: .shift_expr ('&' shift_expr)*":
   ["lineno = get_lineno(ts); col_offset = get_col_offset(ts)"]
,"and_expr: shift_expr. ('&' shift_expr)*":
   ["ast = shift_expr1"]
,"and_expr: shift_expr ('&' shift_expr.)*":
   ["ast = BinOp(ast, BitAnd(), shift_expr2)\n"
    "set_start_end(ts, lineno, col_offset, ast)"]
,"and_expr: shift_expr ('&' shift_expr)*.":
   ["return ast"]


,"shift_expr: .arith_expr (('<<'|'>>') arith_expr)*":
   ["lineno = get_lineno(ts); col_offset = get_col_offset(ts)"]
,"shift_expr: arith_expr. (('<<'|'>>') arith_expr)*":
   ["ast = arith_expr1"]
,"shift_expr: arith_expr (.('<<'|'>>') arith_expr)*":
   ["if ts.token == LEFTSHIFT:\n"
    "    op = LShift()\n"
    "else:\n"
    "    op = RShift()"]
,"shift_expr: arith_expr (('<<'|'>>') arith_expr.)*":
   ["ast = BinOp(ast, op, arith_expr2)\n"
    "set_start_end(ts, lineno, col_offset, ast)"]
,"shift_expr: arith_expr (('<<'|'>>') arith_expr)*.":
   ["return ast"]


,"arith_expr: .term (('+'|'-') term)*":
   ["lineno = get_lineno(ts); col_offset = get_col_offset(ts)"]
,"arith_expr: term. (('+'|'-') term)*":
   ["ast = term1"]
,"arith_expr: term (.('+'|'-') term)*":
   ["if ts.token == PLUS:\n"
    "    op = Add()\n"
    "else:\n"
    "    op = Sub()"]
,"arith_expr: term (('+'|'-') term.)*":
   ["ast = BinOp(ast, op, term2)\n"
    "set_start_end(ts, lineno, col_offset, ast)"]
,"arith_expr: term (('+'|'-') term)*.":
   ["return ast"]


,"term: .factor (('*'|'@'|'/'|'%'|'//') factor)*":
   ["lineno = get_lineno(ts); col_offset = get_col_offset(ts)"]
,"term: factor. (('*'|'@'|'/'|'%'|'//') factor)*":
   ["ast = factor1"]
,"term: factor (.('*'|'@'|'/'|'%'|'//') factor)*":
   ["if ts.token == STAR:\n"
    "    op = Mult()\n"
    "elif ts.token == SLASH:\n"
    "    op = Div()\n"
    "elif ts.token == AT:\n"
    "    op = MatMult()\n"
    "elif ts.token == DOUBLESLASH:\n"
    "    op = FloorDiv()\n"
    "else:\n"
    "    op = Mod()"]
,"term: factor (('*'|'@'|'/'|'%'|'//') factor.)*":
   ["ast = BinOp(ast, op, factor2)\n"
    "set_start_end(ts, lineno, col_offset, ast)"]
,"term: factor (('*'|'@'|'/'|'%'|'//') factor)*.":
   ["return ast"]


,"factor: .('+'|'-'|'~') factor":
   ["lineno = get_lineno(ts); col_offset = get_col_offset(ts)\n"
    "if ts.token == PLUS:\n"
    "    op = UAdd()\n"
    "elif ts.token == MINUS:\n"
    "    op = USub()\n"
    "else:\n"
    "    op = Invert()"]
,"factor: ('+'|'-'|'~') factor.":
   ["ast = UnaryOp(op, factor1)\n"
    "return set_start_end(ts, lineno, col_offset, ast)"]


,"factor: power.":
   ["return power1"]


,"power: .atom_expr ['**' factor]":
   ["lineno = get_lineno(ts); col_offset = get_col_offset(ts)"]
,"power: atom_expr ['**' factor.]":
   ["ast = BinOp(atom_expr1, Pow(), factor1)\n"
    "return set_start_end(ts, lineno, col_offset, ast)"]
,"power: atom_expr ['**' factor].":
   ["return atom_expr1"]


,"atom_expr: .[AWAIT] atom trailer*":
   ["lineno = get_lineno(ts); col_offset = get_col_offset(ts)\n"
    "has_await = False"
   ]
,"atom_expr: [.AWAIT] atom trailer*":
   ["has_await = True"]
,"atom_expr: [AWAIT] atom. trailer*":
   ["ast = atom1"]
,"atom_expr: [AWAIT] atom trailer.*":
   ["ast = trailer1"]
,"atom_expr: [AWAIT] atom trailer*.":
   ["if has_await:\n"
    "    ast = Await(ast)\n"
    "    set_start_end(ts, lineno, col_offset, ast)\n"
    "return ast"]


,"yield_arg": ",lineno,col_offset"


,"yield_arg: 'from' test.":
   ["ast = YieldFrom(test1)\n"
    "return set_start_end(ts, lineno, col_offset, ast)"]

,"yield_arg: testlist_star_expr.":
   ["ast = Yield(testlist_star_expr1)\n"
    "return set_start_end(ts, lineno, col_offset, ast)"]


,"global_stmt: .'global' NAME (',' NAME)*":
   ["lineno = get_lineno(ts); col_offset = get_col_offset(ts)"]
,"global_stmt: 'global' .NAME (',' NAME)*":
   ["names = [token(ts)]"]
,"global_stmt: 'global' NAME (',' .NAME)*":
   ["names.append(token(ts))"]
,"global_stmt: 'global' NAME (',' NAME)*.":
   ["ast = Global(names)\n"
    "return set_start_end(ts, lineno, col_offset, ast)"]


,"nonlocal_stmt: .'nonlocal' NAME (',' NAME)*":
   ["lineno = get_lineno(ts); col_offset = get_col_offset(ts)"]
,"nonlocal_stmt: 'nonlocal' .NAME (',' NAME)*":
   ["names = [token(ts)]"]
,"nonlocal_stmt: 'nonlocal' NAME (',' .NAME)*":
   ["names.append(token(ts))"]
,"nonlocal_stmt: 'nonlocal' NAME (',' NAME)*.":
   ["ast = Nonlocal(names)\n"
    "return set_start_end(ts, lineno, col_offset, ast)"]


,"assert_stmt: .'assert' test [',' test]":
   ["lineno = get_lineno(ts); col_offset = get_col_offset(ts)"]
,"assert_stmt: 'assert' test. [',' test]":
   ["msg = None"]
,"assert_stmt: 'assert' test [',' test.]":
   ["msg = test2"]
,"assert_stmt: 'assert' test [',' test].":
   ["ast = Assert(test1, msg)\n"
    "return set_start_end(ts, lineno, col_offset, ast)"]


,"import_stmt: import_name.":
   ["return import_name1"]


,"import_name: .'import' dotted_as_names":
   ["lineno = get_lineno(ts); col_offset = get_col_offset(ts)"]
,"import_name: 'import' dotted_as_names.":
   ["ast = Import(dotted_as_names1)\n"
    "return set_start_end(ts, lineno, col_offset, ast)"]


,"dotted_as_names: .dotted_as_name (',' dotted_as_name)*":
   ["lineno = get_lineno(ts); col_offset = get_col_offset(ts)"]
,"dotted_as_names: dotted_as_name. (',' dotted_as_name)*":
   ["names = [dotted_as_name1]"]
,"dotted_as_names: dotted_as_name (',' dotted_as_name.)*":
   ["names.append(dotted_as_name2)"]
,"dotted_as_names: dotted_as_name (',' dotted_as_name)*.":
   ["return names"]


,"dotted_as_name: dotted_name. ['as' NAME]":
   ["asname = None"]
,"dotted_as_name: dotted_name ['as' .NAME]":
   ["asname = token(ts)"]
,"dotted_as_name: dotted_name ['as' NAME].":
   ["return alias(dotted_name1, asname)"]


,"dotted_name: .NAME ('.' NAME)*":
   ["dotted_name = token(ts)"]
,"dotted_name: NAME ('.' .NAME)*":
   ["dotted_name = dotted_name + '.' + token(ts)"]
,"dotted_name: NAME ('.' NAME)*.":
   ["return dotted_name"]


,"compound_stmt: if_stmt.":     ["return if_stmt1"]

,"compound_stmt: while_stmt.":  ["return while_stmt1"]

,"compound_stmt: for_stmt.":    ["return for_stmt1"]

,"compound_stmt: try_stmt.":    ["return try_stmt1"]

,"compound_stmt: with_stmt.":    ["return with_stmt1"]

,"compound_stmt: funcdef.":     ["return funcdef1"]

,"compound_stmt: classdef.":    ["return classdef1"]

,"compound_stmt: decorated.":   ["return decorated1"]

,"compound_stmt: async_stmt.":  ["return async_stmt1"]


,"if_stmt: .'if' namedexpr_test ':' suite ('elif' namedexpr_test ':' suite)* ['else' ':' suite]":
   ["lineno = get_lineno(ts); col_offset = get_col_offset(ts)"]
,"if_stmt: 'if' namedexpr_test ':' suite. ('elif' namedexpr_test ':' suite)* ['else' ':' suite]":
   ["branches = [(lineno, col_offset, namedexpr_test1, suite1)]"]
,"if_stmt: 'if' namedexpr_test ':' suite (.'elif' namedexpr_test ':' suite)* ['else' ':' suite]":
   ["lineno = get_lineno(ts); col_offset = get_col_offset(ts)"]
,"if_stmt: 'if' namedexpr_test ':' suite ('elif' namedexpr_test ':' suite.)* ['else' ':' suite]":
   ["branches.append((lineno, col_offset, namedexpr_test2, suite2))"]
,"if_stmt: 'if' namedexpr_test ':' suite ('elif' namedexpr_test ':' suite)* .['else' ':' suite]":
   ["orelse = []"]
,"if_stmt: 'if' namedexpr_test ':' suite ('elif' namedexpr_test ':' suite)* ['else' ':' suite.]":
   ["orelse = suite3"]
,"if_stmt: 'if' namedexpr_test ':' suite ('elif' namedexpr_test ':' suite)* ['else' ':' suite].":
   ["while True:\n"
    "    branch = branches.pop()\n"
    "    lineno = branch[0]\n"
    "    col_offset = branch[1]\n"
    "    test = branch[2]\n"
    "    body = branch[3]\n"
    "    ast = If(test, body, orelse)\n"
    "    set_start(ast, lineno, col_offset)\n"
    "    set_end_ast(ast, (orelse if len(orelse) > 0 else body)[-1])\n"
    "    if len(branches) > 0:\n"
    "        orelse = [ast]\n"
    "    else:\n"
    "        return ast"]


,"while_stmt: .'while' namedexpr_test ':' suite ['else' ':' suite]":
   ["lineno = get_lineno(ts); col_offset = get_col_offset(ts)"]
,"while_stmt: 'while' namedexpr_test ':' suite .['else' ':' suite]":
   ["suite2 = []"]
,"while_stmt: 'while' namedexpr_test ':' suite ['else' ':' suite].":
   ["ast = While(namedexpr_test1, suite1, suite2)\n"
    "set_start(ast, lineno, col_offset)\n"
    "set_end_ast(ast, (suite2 if len(suite2) > 0 else suite1)[-1])\n"
    "return ast"]


,"for_stmt: .'for' exprlist 'in' testlist ':' [TYPE_COMMENT] suite ['else' ':' suite]":
   ["lineno = get_lineno(ts); col_offset = get_col_offset(ts)\n"
    "type_comment = None"]
,"for_stmt: 'for' .exprlist 'in' testlist ':' [TYPE_COMMENT] suite ['else' ':' suite]":
   ["as_list = False"]
,"for_stmt: 'for' exprlist. 'in' testlist ':' [TYPE_COMMENT] suite ['else' ':' suite]":
   ["check_assignable(ts, exprlist1)"]
,"for_stmt: 'for' exprlist 'in' .testlist ':' [TYPE_COMMENT] suite ['else' ':' suite]":
   ["as_list = False"]
,"for_stmt: 'for' exprlist 'in' testlist ':' [TYPE_COMMENT] suite .['else' ':' suite]":
   ["suite2 = []"]
,"for_stmt: 'for' exprlist 'in' testlist ':' [TYPE_COMMENT] suite ['else' ':' suite].":
   ["set_ctx1(exprlist1, Store())\n"
    "ast = For(exprlist1, testlist1, suite1, suite2, type_comment)\n"
    "set_start(ast, lineno, col_offset)\n"
    "set_end_ast(ast, (suite2 if len(suite2) > 0 else suite1)[-1])\n"
    "return ast"]

,"with_stmt: .'with' with_item (',' with_item)* ':' [TYPE_COMMENT] suite":
    ["lineno = get_lineno(ts); col_offset = get_col_offset(ts)\n"
     "type_comment = None\n"
     "withitems = []"]
,"with_stmt: 'with' with_item. (',' with_item)* ':' [TYPE_COMMENT] suite":
    ["withitems.append(with_item1)"]
,"with_stmt: 'with' with_item (',' with_item.)* ':' [TYPE_COMMENT] suite":
    ["withitems.append(with_item2)"]
,"with_stmt: 'with' with_item (',' with_item)* ':' [TYPE_COMMENT] suite.":
    ["ast = With(withitems, suite1, type_comment)\n"
     "return set_start_end(ts, lineno, col_offset, ast)"]

,"with_item: .test ['as' expr]":
    ["expr1 = None"]
,"with_item: test ['as' expr.]":
    ["check_assignable(ts, expr1)\n"
     "set_ctx1(expr1, Store())"]
,"with_item: test ['as' expr].":
    ["return withitem(test1, expr1)"]

,"try_stmt: .'try' ':' suite (finally_block | (handlers_list ['else' ':' suite] [finally_block]))":
    ["lineno = get_lineno(ts); col_offset = get_col_offset(ts)"]
,"try_stmt: 'try' ':' suite (finally_block. | (handlers_list ['else' ':' suite] [finally_block]))":
    ["ast = Try(suite1, [], [], finally_block1)\n"
     "return set_start_end(ts, lineno, col_offset, ast)"]
,"try_stmt: 'try' ':' suite (finally_block | (handlers_list ['else' ':' suite] [finally_block]))":
    ["handlers.append(except_block1)"]
,"try_stmt: 'try' ':' suite (finally_block | (handlers_list .['else' ':' suite] [finally_block]))":
    ["suite2 = []"]
,"try_stmt: 'try' ':' suite (finally_block | (handlers_list ['else' ':' suite] .[finally_block]))":
    ["finally_block2 = []"]
,"try_stmt: 'try' ':' suite (finally_block | (handlers_list ['else' ':' suite] [finally_block].))":
    ["ast = Try(suite1, handlers_list1, suite2, finally_block2)\n"
     "return set_start_end(ts, lineno, col_offset, ast)"]

,"handlers_list: except_block. except_block *":
    ["handlers = [except_block1]"]
,"handlers_list: except_block except_block. *":
    ["handlers.append(except_block2)"]
,"handlers_list: except_block except_block *.":
    ["return handlers"]

,"except_block: .'except' [test ['as' NAME]] ':' suite":
    ["lineno = get_lineno(ts); col_offset = get_col_offset(ts); name = None; type = None"]
,"except_block: 'except' [test. ['as' NAME]] ':' suite":
    ["type = test1"]
,"except_block: 'except' [test ['as' .NAME]] ':' suite":
    ["name = token(ts)"]
,"except_block: 'except' [test ['as' NAME]] ':' suite.":
    ["ast = ExceptHandler(type, name, suite1)\n"
     "return set_start_end(ts, lineno, col_offset, ast)"]

,"finally_block: 'finally' ':' suite.":
    ["return suite1"]

,"testlist": ",as_list"


,"testlist: .test (',' test)* [',']":
   ["lineno = get_lineno(ts); col_offset = get_col_offset(ts)"]
,"testlist: test .(',' test)* [',']":
   ["tests = [test1]\n"
    "dangling_comma = False",
    ""]
,"testlist: test (',' test.)* [',']":
   ["tests.append(test2)"]
,"testlist: test (',' test)* [','.]":
   ["dangling_comma = True"]
,"testlist: test (',' test)* [','].":
   ["if as_list:\n"
    "    return (tests, dangling_comma or len(tests) != 1)\n"
    "elif len(tests) == 1 and not dangling_comma:\n"
    "    return test1\n"
    "else:\n"
    "    ast = Tuple(tests, Load())\n"
    "    return set_start_end(ts, lineno, col_offset, ast)"]


,"namedexpr_test: .test [':=' test]":
   ["lineno = get_lineno(ts); col_offset = get_col_offset(ts)"]
,"namedexpr_test: test .[':=' test]":
   ["test2 = None"]
,"namedexpr_test: test [':=' test].":
   ["if test2 is None:\n"
    "    return test1\n"
    "else:\n"
    "    return test2"]


,"suite: simple_stmt.":
   ["return simple_stmt1"]

,"suite: NEWLINE INDENT. stmt+ DEDENT":
   ["stmts = []"]
,"suite: NEWLINE INDENT stmt.+ DEDENT":
   ["stmts.extend(stmt1)"]
,"suite: NEWLINE INDENT stmt+ DEDENT.":
   ["return stmts"]


,"testlist_star_expr: .(test|star_expr) (',' (test|star_expr))* [',']":
   ["lineno = get_lineno(ts); col_offset = get_col_offset(ts)"]
,"testlist_star_expr: (test.|star_expr) (',' (test|star_expr))* [',']":
   ["test_or_star_expr1 = test1"]
,"testlist_star_expr: (test|star_expr.) (',' (test|star_expr))* [',']":
   ["test_or_star_expr1 = star_expr1"]
,"testlist_star_expr: (test|star_expr) .(',' (test|star_expr))* [',']":
   ["tests = [test_or_star_expr1]\n"
    "dangling_comma = False",
    ""]
,"testlist_star_expr: (test|star_expr) (',' (test.|star_expr))* [',']":
   ["tests.append(test2)"]
,"testlist_star_expr: (test|star_expr) (',' (test|star_expr.))* [',']":
   ["tests.append(star_expr2)"]
,"testlist_star_expr: (test|star_expr) (',' (test|star_expr))* [','.]":
   ["dangling_comma = True"]
,"testlist_star_expr: (test|star_expr) (',' (test|star_expr))* [','].":
   ["if len(tests) == 1 and not dangling_comma:\n"
    "    return test_or_star_expr1\n"
    "else:\n"
    "    ast = Tuple(tests, Load())\n"
    "    return set_start_end(ts, lineno, col_offset, ast)"]


,"exprlist": ",as_list"


,"exprlist: .(expr|star_expr) (',' (expr|star_expr))* [',']":
   ["lineno = get_lineno(ts); col_offset = get_col_offset(ts)"]
,"exprlist: (expr.|star_expr) (',' (expr|star_expr))* [',']":
   ["expr_or_star_expr1 = expr1"]
,"exprlist: (expr|star_expr.) (',' (expr|star_expr))* [',']":
   ["expr_or_star_expr1 = star_expr1"]
,"exprlist: (expr|star_expr) .(',' (expr|star_expr))* [',']":
   ["exprs = [expr_or_star_expr1]\n"
    "dangling_comma = False",
    ""]
,"exprlist: (expr|star_expr) (',' (expr.|star_expr))* [',']":
   ["expr_or_star_expr2 = expr2"]
,"exprlist: (expr|star_expr) (',' (expr|star_expr.))* [',']":
   ["expr_or_star_expr2 = star_expr2"]
,"exprlist: (expr|star_expr) (',' (expr|star_expr).)* [',']":
   ["exprs.append(expr_or_star_expr2)"]
,"exprlist: (expr|star_expr) (',' (expr|star_expr))* [','.]":
   ["dangling_comma = True"]
,"exprlist: (expr|star_expr) (',' (expr|star_expr))* [','].":
   ["if as_list:\n"
    "    return (exprs, dangling_comma or len(exprs) != 1)\n"
    "elif len(exprs) == 1 and not dangling_comma:\n"
    "    return expr_or_star_expr1\n"
    "else:\n"
    "    ast = Tuple(exprs, Load())\n"
    "    return set_start_end(ts, lineno, col_offset, ast)"]


,"subscriptlist: .subscript (',' subscript)* [',']":
   ["lineno = get_lineno(ts); col_offset = get_col_offset(ts)"]
,"subscriptlist: subscript .(',' subscript)* [',']":
   ["subscripts = [subscript1]\n"
    "has_slice = isinstance(subscript1, Slice)\n"
    "dangling_comma = False",
    ""]
,"subscriptlist: subscript (',' subscript.)* [',']":
   ["subscripts.append(subscript2)\n"
    "has_slice = has_slice or isinstance(subscript2, Slice)\n"]
,"subscriptlist: subscript (',' subscript)* [','.]":
   ["dangling_comma = True"]
,"subscriptlist: subscript (',' subscript)* [','].":
   ["if len(subscripts) == 1 and not dangling_comma:\n"
    "    return subscripts[0]\n"
    "elif has_slice:\n"
    "    ast = ExtSlice(subscripts)\n"
    "    return set_start_end(ts, lineno, col_offset, ast)\n"
    "else:\n"
    "    items = []\n"
    "    for s in items:\n"
    "        items.append(s.value)\n"
    "    ast = Tuple(items, Load())\n"
    "    set_start_end(ts, lineno, col_offset, ast)\n"
    "    ast = Index(ast)\n"
    "    return set_start_end(ts, lineno, col_offset, ast)"]


,"trailer": ",lineno,col_offset,ast"

,"trailer: '('. [arglist] ')'":
   ["arglist1 = [[], []]"]
,"trailer: '(' [arglist]. ')'":
   ["ast = Call(ast, arglist1[0], arglist1[1])"]
,"trailer: '(' [arglist] ')'.":
   ["return set_start_end(ts, lineno, col_offset, ast)"]

,"trailer: '[' subscriptlist. ']'":
   ["ast = Subscript(ast, subscriptlist1, Load())"]
,"trailer: '[' subscriptlist ']'.":
   ["return set_start_end(ts, lineno, col_offset, ast)"]

,"trailer: '.' .NAME":
   ["ast = Attribute(ast, token(ts), Load())"]
,"trailer: '.' NAME.":
   ["return set_start_end(ts, lineno, col_offset, ast)"]


,"atom: .'(' [yield_expr|testlist_comp] ')'":
   ["lineno = get_lineno(ts); col_offset = get_col_offset(ts)"]
,"atom: '(' .[yield_expr|testlist_comp] ')'":
   ["x = ([], True)"]
,"atom: '(' [yield_expr.|testlist_comp] ')'":
   ["x = ([yield_expr1], False)"]
,"atom: '(' [yield_expr|.testlist_comp] ')'":
   ["as_list = True"]
,"atom: '(' [yield_expr|testlist_comp.] ')'":
   ["x = testlist_comp1"]
,"atom: '(' [yield_expr|testlist_comp] ')'.":
   ["if x[1]:\n"
    "    ast = Tuple(x[0], Load())\n"
    "    set_start_end(ts, lineno, col_offset, ast)\n"
    "else:\n"
    "    ast = x[0][0]\n"
    "return ast"]

,"atom: .'[' [testlist_comp] ']'":
   ["lineno = get_lineno(ts); col_offset = get_col_offset(ts)"]
,"atom: '[' .[testlist_comp] ']'":
   ["ast = None"]
,"atom: '[' [.testlist_comp] ']'":
   ["as_list = True"]
,"atom: '[' [testlist_comp.] ']'":
   ["ast = List(testlist_comp1[0], Load())"]
,"atom: '[' [testlist_comp] ']'.":
   ["if ast is None:\n"
    "    ast = List([], Load())\n"
    "return set_start_end(ts, lineno, col_offset, ast)"]

,"atom: .'{' [dictorsetmaker] '}'":
   ["lineno = get_lineno(ts); col_offset = get_col_offset(ts)"]
,"atom: '{' .[dictorsetmaker] '}'":
   ["ast = None"]
,"atom: '{' [dictorsetmaker.] '}'":
   ["ast = dictorsetmaker1"]
,"atom: '{' [dictorsetmaker] '}'.":
   ["if ast is None:\n"
    "    ast = Dict([], [])\n"
    "return set_start_end(ts, lineno, col_offset, ast)"]


,"atom: .NAME":     ["ast = set_start_end_1token(ts, Name(token(ts), Load()))"]
,"atom: NAME.":     ["return ast"]


,"atom: .NUMBER":   ["ast = set_start_end_1token(ts, Constant(get_value(ts), None))"]
,"atom: NUMBER.":   ["return ast"]


,"atom: .STRING+":  ["lineno = get_lineno(ts); col_offset = get_col_offset(ts)\n"
                     "end_lineno = 0\n"
                     "end_col_offset = 0\n"
                     "value = None\n"
                     "current_kind = get_kind(ts)\n",
                     "temp = get_value(ts)\n"
                     "temp_kind = get_kind(ts)\n"
                     "if value is None:\n"
                     "    value = temp\n"
                     "elif current_kind != temp_kind:\n"
                     "    py_syntax_error(ts, 'cannot mix bytes and nonbytes literals')\n"
                     "else:\n"
                     "    value += temp\n"
                     "end_lineno = get_end_lineno(ts)\n"
                     "end_col_offset = get_end_col_offset(ts)\n"]
,"atom: STRING+.":  ["ast = Constant(value, None)\n"
                     "ast.lineno = lineno\n"
                     "ast.col_offset = col_offset\n"
                     "ast.end_lineno = end_lineno\n"
                     "ast.end_col_offset = end_col_offset\n"
                     "return ast"]


,"atom: .'...'":    ["ast = set_start_end_1token(ts, Constant(..., None))"]
,"atom: '...'.":    ["return ast"]


,"atom: .'None'":   ["ast = set_start_end_1token(ts, Constant(None, None))"]
,"atom: 'None'.":   ["return ast"]


,"atom: .'True'":   ["ast = set_start_end_1token(ts, Constant(True, None))"]
,"atom: 'True'.":   ["return ast"]


,"atom: .'False'":  ["ast = set_start_end_1token(ts, Constant(False, None))"]
,"atom: 'False'.":  ["return ast"]


,"testlist_comp": ",as_list"


,"testlist_comp: testlist.":
   ["return testlist1"]


,"argument: .test ['=' test]": ["lineno = get_lineno(ts); col_offset = get_col_offset(ts)"]
,"argument: test ['=' test.]": ["if isinstance(test1, Name):\n"
                                "    ast = keyword(test1.id, test2)\n"
                                "    return set_start_end(ts, lineno, col_offset, ast)\n"
                                "else:\n"
                                "    return py_syntax_error(ts, 'expression cannot contain assignment, perhaps you meant \"==\"?')"]
,"argument: test ['=' test].": ["return test1"]
,"argument: .'**' test": ["lineno = get_lineno(ts); col_offset = get_col_offset(ts)"]
,"argument: '**' test.": ["ast = keyword(None, test1)\n"
                          "return set_start_end(ts, lineno, col_offset, ast)"]
,"argument: .'*' test": ["lineno = get_lineno(ts); col_offset = get_col_offset(ts)"]
,"argument: '*' test.": ["ast = Starred(test1, Load())\n"
                          "return set_start_end(ts, lineno, col_offset, ast)"]


,"arglist: .argument (',' argument)* [',']": ["only_keywords = False; only_kwargs = False\n"
                                              "args = []; keywords = []"]
,"arglist: argument. (',' argument)* [',']": ["if isinstance(argument1, keyword):\n"
                                              "    only_kwargs = argument1.arg is None\n"
                                              "    only_keywords = not only_kwargs\n"
                                              "    keywords.append(argument1)\n"
                                              "else:\n"
                                              "    args.append(argument1)"]
,"arglist: argument (',' argument.)* [',']": ["if isinstance(argument2, keyword):\n"
                                              "    is_kwarg = argument2.arg is None\n"
                                              "    only_kwargs = only_kwargs or is_kwarg\n"
                                              "    only_keywords = only_keywords or not is_kwarg\n"
                                              "    keywords.append(argument2)\n"
                                              "elif isinstance(argument2, Starred):\n"
                                              "    if only_kwargs:\n"
                                              "        return py_syntax_error(ts, 'iterable argument unpacking follows keyword argument unpacking')\n"
                                              "    else:\n"
                                              "        args.append(argument2)\n"
                                              "else:\n"
                                              "    if only_keywords:\n"
                                              "        return py_syntax_error(ts, 'positional argument follows keyword argument')\n"
                                              "    else:\n"
                                              "        args.append(argument2)"]
,"arglist: argument (',' argument)* [','].":
   ["return args, keywords"]


,"subscript: test.":
   ["return Index(test1)"]






############## to support new grammar rules (closer to Grammar3.8a4.py)

,"atom_expr: .atom trailer*":
   ["lineno = get_lineno(ts); col_offset = get_col_offset(ts)\n"]
,"atom_expr: atom. trailer*":
   ["ast = atom1"]
,"atom_expr: atom trailer.*":
   ["ast = trailer1"]
,"atom_expr: atom trailer*.":
   ["return ast"]


,"atom: .'(' [testlist_comp] ')'":
   ["lineno = get_lineno(ts); col_offset = get_col_offset(ts)"]
,"atom: '(' .[testlist_comp] ')'":
   ["x = ([], True)"]
,"atom: '(' [.testlist_comp] ')'":
   ["as_list = True"]
,"atom: '(' [testlist_comp.] ')'":
   ["x = testlist_comp1"]
,"atom: '(' [testlist_comp] ')'.":
   ["if x[1]:\n"
    "    ast = Tuple(x[0], Load())\n"
    "    set_start_end(ts, lineno, col_offset, ast)\n"
    "else:\n"
    "    ast = x[0][0]\n"
    "return ast"]


,"testlist_comp": ",as_list"


,"testlist_comp: .namedexpr_test (',' namedexpr_test)* [',']":
   ["lineno = get_lineno(ts); col_offset = get_col_offset(ts)"]
,"testlist_comp: namedexpr_test .(',' namedexpr_test)* [',']":
   ["namedexpr_tests = [namedexpr_test1]\n"
    "dangling_comma = False",
    ""]
,"testlist_comp: namedexpr_test (',' namedexpr_test.)* [',']":
   ["namedexpr_tests.append(namedexpr_test2)"]
,"testlist_comp: namedexpr_test (',' namedexpr_test)* [','.]":
   ["dangling_comma = True"]
,"testlist_comp: namedexpr_test (',' namedexpr_test)* [','].":
   ["if as_list:\n"
    "    return (namedexpr_tests, dangling_comma or len(namedexpr_tests) != 1)\n"
    "elif len(namedexpr_tests) == 1 and not dangling_comma:\n"
    "    return namedexpr_test1\n"
    "else:\n"
    "    ast = Tuple(namedexpr_tests, Load())\n"
    "    return set_start_end(ts, lineno, col_offset, ast)"]


,"namedexpr_test: test.":
   ["return test1"]


,"simple_stmt: small_stmt. (';' small_stmt)* [';'] NEWLINE":
   ["small_stmts = [small_stmt1]"]
,"simple_stmt: small_stmt (';' small_stmt.)* [';'] NEWLINE":
   ["small_stmts.append(small_stmt2)"]
,"simple_stmt: small_stmt (';' small_stmt)* [';'] NEWLINE.":
   ["return small_stmts"]


,"expr_stmt: .testlist_star_expr (augassign testlist | [('=' testlist_star_expr)+ [TYPE_COMMENT]] )":
   ["lineno = get_lineno(ts); col_offset = get_col_offset(ts)"]
,"expr_stmt: testlist_star_expr. (augassign testlist | [('=' testlist_star_expr)+ [TYPE_COMMENT]] )":
   ["target = testlist_star_expr1\n"
    "type_comment = None"]
,"expr_stmt: testlist_star_expr (augassign .testlist | [('=' testlist_star_expr)+ [TYPE_COMMENT]] )":
   ["check_assignable(ts, target)\n"
    "as_list = False"]
,"expr_stmt: testlist_star_expr (augassign testlist. | [('=' testlist_star_expr)+ [TYPE_COMMENT]] )":
   ["ast = AugAssign(target, augassign1, testlist1)\n"
    "set_ctx1(target, Store())\n"
    "return set_start_end(ts, lineno, col_offset, ast)"]
,"expr_stmt: testlist_star_expr (augassign testlist | [('=' .testlist_star_expr)+ [TYPE_COMMENT]] )":
   ["check_assignable(ts, target)\n"
    "as_list = False"]
,"expr_stmt: testlist_star_expr (augassign testlist | [('=' testlist_star_expr)+. [TYPE_COMMENT]] )":
   ["check_assignable(ts, target)\n"
    "ast = Assign([target], testlist_star_expr2, type_comment)\n"
    "set_ctx1(target, Store())\n"
    "return set_start_end(ts, lineno, col_offset, ast)"]
,"expr_stmt: testlist_star_expr (augassign testlist | [('=' testlist_star_expr)+ [TYPE_COMMENT]] ).":
   ["ast = Expr(testlist_star_expr1)\n"
    "return set_start_end(ts, lineno, col_offset, ast)"]


,"testlist_star_expr: .test (',' test)* [',']":
   ["lineno = get_lineno(ts); col_offset = get_col_offset(ts)"]
,"testlist_star_expr: test. (',' test)* [',']":
   ["test1 = test1"]
,"testlist_star_expr: test .(',' test)* [',']":
   ["tests = [test1]\n"
    "dangling_comma = False",
    ""]
,"testlist_star_expr: test (',' test.)* [',']":
   ["tests.append(test2)"]
,"testlist_star_expr: test (',' test)* [','.]":
   ["dangling_comma = True"]
,"testlist_star_expr: test (',' test)* [','].":
   ["if len(tests) == 1 and not dangling_comma:\n"
    "    return test1\n"
    "else:\n"
    "    ast = Tuple(tests, Load())\n"
    "    return set_start_end(ts, lineno, col_offset, ast)"]



,"funcdef: .'def' NAME parameters ':' [TYPE_COMMENT] func_body_suite":
   ["lineno = get_lineno(ts); col_offset = get_col_offset(ts)\n"
    "type_comment = None"]
,"funcdef: 'def' .NAME parameters ':' [TYPE_COMMENT] func_body_suite":
   ["name = token(ts)"]
,"funcdef: 'def' NAME parameters ':' [TYPE_COMMENT] func_body_suite.":
   ["ast = FunctionDef(name, parameters1, func_body_suite1, [], None, type_comment)\n"
    "set_start(ast, lineno, col_offset)\n"
    "set_end_ast(ast, func_body_suite1[-1])\n"
    "return ast"]


,"classdef: .'class' NAME ['(' [arglist] ')'] ':' suite":
   ["lineno = get_lineno(ts); col_offset = get_col_offset(ts)\n"]
,"classdef: 'class' .NAME ['(' [arglist] ')'] ':' suite":
   ["name = token(ts)"]
,"classdef: 'class' NAME .['(' [arglist] ')'] ':' suite":
   ["bases, keywords = [[], []]"]
,"classdef: 'class' NAME ['(' [arglist.] ')'] ':' suite":
   ["bases, keywords = arglist1"]
,"classdef: 'class' NAME ['(' [arglist] ')'] ':' suite.":
   ["ast = ClassDef(name, bases, keywords, suite1, [])\n"
    "set_start(ast, lineno, col_offset)\n"
    "set_end_ast(ast, suite1[-1])\n"
    "return ast"]


,"subscript: test [.subscript_tail]":
   ["lower = test1"]
,"subscript: test [subscript_tail.]":
   ["return subscript_tail1"]
,"subscript: test [subscript_tail].":
   ["return Index(test1)"]


,"subscript: .subscript_tail":
   ["lower = None"]
,"subscript: subscript_tail.":
   ["return subscript_tail1"]


,"subscript_tail": ",lower"


,"subscript_tail: ':' .[test] [sliceop]":
   ["test1 = None"]
,"subscript_tail: ':' [test] .[sliceop]":
   ["sliceop1 = None"]
,"subscript_tail: ':' [test] [sliceop].":
   ["return Slice(lower, test1, sliceop1)"]


,"sliceop: ':' [test.]":
    ["return test1"]
,"sliceop: ':' [test].":
    ["return None"]


,"exprlist: .expr (',' expr)* [',']":
   ["lineno = get_lineno(ts); col_offset = get_col_offset(ts)"]
,"exprlist: expr .(',' expr)* [',']":
   ["exprs = [expr1]\n"
    "dangling_comma = False",
    ""]
,"exprlist: expr (',' expr.)* [',']":
   ["exprs.append(expr2)"]
,"exprlist: expr (',' expr)* [','.]":
   ["dangling_comma = True"]
,"exprlist: expr (',' expr)* [','].":
   ["if as_list:\n"
    "    return (exprs, dangling_comma or len(exprs) != 1)\n"
    "elif len(exprs) == 1 and not dangling_comma:\n"
    "    return expr1\n"
    "else:\n"
    "    ast = Tuple(exprs, Load())\n"
    "    return set_start_end(ts, lineno, col_offset, ast)"]


,"dictorsetmaker: (.test ':' test) (',' (test ':' test))* [',']":
   ["lineno = get_lineno(ts); col_offset = get_col_offset(ts)"]
,"dictorsetmaker: (test ':' test) .(',' (test ':' test))* [',']":
   ["keys = [test1]\n"
    "values = [test2]",
    ""]
,"dictorsetmaker: (test ':' test) (',' (test ':' test.))* [',']":
   ["keys.append(test3)\n"
    "values.append(test4)"]
,"dictorsetmaker: (test ':' test) (',' (test ':' test))* [','].":
   ["ast = Dict(keys, values)\n"
    "return set_start_end(ts, lineno, col_offset, ast)"]




}
