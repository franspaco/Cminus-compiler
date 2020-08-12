from enum import Enum

from tree import Node



## LEXING RULES

class TokenType(Enum):
    PLUS = 'PLUS'
    MINUS = 'MINUS'
    TIMES = 'TIMES'
    DIVIDE = 'DIVIDE'
    ASSIGN = 'ASSIGN'
    LT = 'LT'
    LET = 'LET'
    GT = 'GT'
    GET = 'GET'
    EQUALS = 'EQUALS'
    NEQUALS = 'NEQUALS'
    COLON = 'COLON'
    COMMA = 'COMMA'
    LPAREN = 'LPAREN'
    RPAREN = 'RPAREN'
    LBRACK = 'LBRACK'
    RBRACK = 'RBRACK'
    LCURLY = 'LCURLY'
    RCURLY = 'RCURLY'
    COMM = 'COMM'
    ID = 'ID'
    NUM = 'NUM'
    ELSE = 'ELSE'
    IF = 'IF'
    INT = 'INT'
    RETURN = 'RETURN'
    VOID = 'VOID'
    WHILE = 'WHILE'
    ENDFILE = 'ENDFILE'
    error = 'error'
    ERROR = error


tokens_symbols = (
    'PLUS',
    'MINUS',
    'TIMES',
    'DIVIDE',
    'ASSIGN',
    'LT',
    'LET',
    'GT',
    'GET',
    'EQUALS',
    'NEQUALS',
    'COLON',
    'COMMA',
    'LPAREN',
    'RPAREN',
    'LBRACK',
    'RBRACK',
    'LCURLY',
    'RCURLY',
    'COMM',
    'ID',
    'NUM',
    'ENDFILE'
)

reserved = {
    'else':   'ELSE',
    'if':     'IF',
    'int':    'INT',
    'return': 'RETURN',
    'void':   'VOID',
    'while':  'WHILE',
}

tokens = list(tokens_symbols) + list(reserved.values())

t_ignore = " \t"

t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*(?!/)'
t_DIVIDE = r'/(?!\*)'
t_ASSIGN = r'='
t_LT = r'<'
t_LET = r'<='
t_GT = r'>'
t_GET = r'>='
t_EQUALS = r'=='
t_NEQUALS = r'!='
t_COLON = r';'
t_COMMA = r','
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACK = r'\['
t_RBRACK = r'\]'
t_LCURLY = r'\{'
t_RCURLY = r'\}'
t_ENDFILE = r'\$'


def t_COMM(t):
    r'/\*(.|\n)*?\*/'
    t.lexer.lineno += t.value.count("\n")
    last_return = t.value.rfind('\n')
    if last_return > 0:
        t.lexer.linestartpos = t.lexer.lexpos - (len(t.value) - last_return)
    # return t


def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")
    t.lexer.linestartpos = t.lexer.lexpos


def t_NUM(t):
    r'\d+(?![0-9a-zA-Z])'
    try:
        t.value = int(t.value)
    except ValueError:
        print("Integer value too large %d", t.value)
        t.value = 0
    return t


def t_ID(t):
    r'[a-zA-Z][a-zA-Z]*(?![0-9])'
    t.type = reserved.get(t.value, 'ID')    # Check for reserved words
    return t


def t_error(t):
    t.lexer.skip(1)
    print(f"\nERROR: Illegal token - line: {t.lineno}, col: {t.linepos}, character: '{t.value[0]}'")
    print(f"{t.lexer.lexdatalines[t.lineno-1]}\n{' ' * t.linepos}^\n")


## PARSING RULES

def p_root(p):
    'program : declaration_list ENDFILE'
    p[0] = Node(Node.PROGRAM, p=p, items=p[1])


def p_type_specifier(p):
    '''type_specifier : VOID 
                      | INT'''
    #p[0] = p[1]
    p[0] = Node.datatype(p[1])


def p_root_statement(p):
    '''declaration_list  : declaration
                         | declaration_list declaration'''
    if len(p) is 3:
        p[1].append(p[2])
        p[0] = p[1]
    else:
        p[0] = [(p[1])]


def p_external_declaration(p):
    '''declaration : var_declaration
                   | function_definition'''
    p[0] = p[1]


def p_var_declaration(p):
    '''var_declaration : type_specifier ID COLON'''
    p[0] = Node(Node.DECLARATION, p=p, name=p[2],
                datatype=p[1], varcard=Node.VAR_SINGLE)


def p_var_declaration_array(p):
    '''var_declaration : type_specifier ID LBRACK NUM RBRACK COLON'''
    #p[0] = ('declaration', p[1], 'array', p[2], p[4])
    p[0] = Node(Node.DECLARATION, p=p, name=p[2], datatype=p[1],
                varcard=Node.VAR_ARRAY, arrval=p[4])


def p_function_definition(p):
    '''function_definition : type_specifier ID LPAREN params RPAREN compound_statement'''
    #p[0] = ('func', p[1], p[2], p[4], p[6])
    p[0] = Node(Node.FUNC, p=p, name=p[2], datatype=p[1], params=p[4], declarations=p[6].declarations, body=p[6].body, varcard=Node.VAR_SINGLE)


def p_function_declarator_simple(p):
    '''params : param_list
              | VOID
    '''
    p[0] = p[1] if p[1] != 'void' else []


def p_param_list(p):
    '''param_list : parameter_declaration
                  | param_list COMMA parameter_declaration
    '''
    if len(p) is 4:
        p[1].append(p[3])
        p[0] = p[1]
    else:
        p[0] = [(p[1])]


def p_parameter_declaration(p):
    '''parameter_declaration : type_specifier ID
                             | type_specifier ID LBRACK RBRACK
    '''
    cardinality = Node.VAR_SINGLE if len(p) <= 3 else Node.VAR_ARRAY
    p[0] = Node(Node.PARAM, p=p, name=p[2], datatype=p[1], varcard=cardinality)


def p_compound_statement(p):
    '''compound_statement : LCURLY local_declarations statement_list RCURLY
    '''
    p[0] = Node(Node.COMPOUND, p=p, declarations=p[2], body=p[3])


def p_local_declarations(p):
    '''local_declarations : local_declarations var_declaration
                          | empty
    '''
    if p[1] is None:
        p[1] = []
    if len(p) > 2:
        p[1].append(p[2])
    p[0] = p[1]

def p_statement_list(p):
    '''statement_list : statement_list statement
                      | empty
    '''
    if p[1] is None:
        p[1] = []
    if len(p) > 2 and p[2] is not None:
        p[1].append(p[2])
    p[0] = p[1]

def p_statement(p):
    '''statement : expression_statement
                 | compound_statement
                 | selection_statement
                 | iteration_statement
                 | return_statement
    '''
    p[0] = p[1]


def p_expression_statement(p):
    '''expression_statement : expression COLON
                            | COLON
    '''
    if len(p) == 3:
        p[0] = p[1]


def p_selection_statement(p):
    '''selection_statement : IF LPAREN expression RPAREN statement
                           | IF LPAREN expression RPAREN statement ELSE statement
    '''
    else_statement = p[7] if len(p) == 8 else None
    p[0] = Node(Node.IF, p=p, condition=p[3], ifthen=p[5], ifelse=else_statement)


def p_iteration_statement(p):
    '''iteration_statement : WHILE LPAREN expression RPAREN statement'''
    p[0] = Node(Node.WHILE, p=p, condition=p[3], body=p[5])


def  p_return_statement(p):
    '''return_statement : RETURN COLON
                        | RETURN expression COLON
    '''
    p[0] = Node(Node.RETURN, p=p, value=p[2] if len(p) == 4 else None)


def p_expression(p):
    '''expression : var ASSIGN expression
                  | simple_expression
    '''
    if len(p) == 2:
        p[0] = p[1]
    elif len(p) == 4:
        p[0] = Node(Node.ASSIGN, p=p, to=p[1], value=p[3])


def p_var(p):
    '''var : ID
           | ID LBRACK expression RBRACK
    '''
    if len(p) == 2:
        p[0] = Node(Node.VAR, p=p, name=p[1], varcard=Node.VAR_SINGLE)
    else:
        p[0] = Node(Node.VAR, p=p, name=p[1], varcard=Node.VAR_ARRAY, arrval=p[3])


def p_simple_expression(p):
    '''simple_expression : additive_expression relop additive_expression
                         | additive_expression
    '''
    if len(p) == 2:
        p[0] = p[1]
    else:
        node = Node(Node.COMP, p=p, operation=p[2], left=p[1], right=p[3])
        if node.left.nodeType is Node.LITERAL and node.right.nodeType is Node.LITERAL:
            a = node.left.value
            b = node.right.value
            res = int({
                Node.LET: lambda x,y: x <= y,
                Node.LT:  lambda x,y: x <  y,
                Node.GT:  lambda x,y: x >  y,
                Node.GET: lambda x,y: x >= y,
                Node.EQ:  lambda x,y: x == y,
                Node.NEQ: lambda x,y: x != y,
            }[node.operation](a,b))
            node = Node(Node.LITERAL, p=p, datatype=Node.TYPE_INT, value=res)
        p[0] = node


def p_relop(p):
    '''relop : LT
             | LET
             | GT
             | GET
             | EQUALS
             | NEQUALS
    '''
    p[0] = Node.op(p[1])
    

def p_additive_expression(p):
    '''additive_expression : additive_expression addop term
                           | term
    '''
    if len(p) == 2:
        p[0] = p[1]
    else:
        node = Node(Node.SIGM, p=p, operation=p[2], left=p[1], right=p[3])
        if node.left.nodeType is Node.LITERAL and node.right.nodeType is Node.LITERAL:
            if node.operation is Node.ADD:
                res = node.left.value + node.right.value
            elif node.operation is Node.SUB:
                res = node.left.value - node.right.value
            node = Node(Node.LITERAL, p=p, datatype=Node.TYPE_INT, value=res)
        p[0] = node


def p_addop(p):
    '''addop : PLUS
             | MINUS
    '''
    p[0] = Node.op(p[1])


def p_term(p):
    '''term : term multop factor
            | factor
    '''
    if len(p) == 2:
        p[0] = p[1]
    else:
        node = Node(Node.PROD, p=p, operation=p[2], left=p[1], right=p[3])
        if node.left.nodeType is Node.LITERAL and node.right.nodeType is Node.LITERAL:
            if node.operation is Node.MUL:
                res = node.left.value * node.right.value
            elif node.operation is Node.DIV:
                res = node.left.value // node.right.value
            node = Node(Node.LITERAL, p=p, datatype=Node.TYPE_INT, value=res)
        p[0] = node



def p_multop(p):
    '''multop : TIMES
              | DIVIDE
    '''
    p[0] = Node.op(p[1])


def p_factor(p):
    '''factor : LPAREN expression RPAREN
              | var
              | call
              | num_lit
    '''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = p[2]

def p_num_lit(p):
    '''num_lit : NUM'''
    p[0] = Node(Node.LITERAL, p=p, datatype=Node.TYPE_INT, value=p[1])

def p_call(p):
    'call : ID LPAREN args RPAREN'
    p[0] = Node(Node.CALL, p=p, name=p[1], args=p[3])


def p_args(p):
    '''args : arg_list 
            | empty
    '''
    p[0] = p[1] if p[1] is not None else []


def p_arg_list(p):
    '''arg_list : arg_list COMMA expression
                | expression
    '''
    p[0] = list()

    if len(p) == 4:
        p[0].extend(p[1])
        p[0].append(p[3])
    else:
        p[0].append(p[1])

def p_empty(p):
    'empty :'
    pass


def p_error(t, parser):
    if t is not None:
        print_value = t.value[0] if type(t.value) is str else t.value
        print(f"\nERROR: Invalid Syntax - line: {t.lineno}, col: {t.linepos}, character: '{print_value}'")
        print(f"{t.lexer.lexdatalines[t.lineno-1]}\n{' ' * t.linepos}^\n")
        # Let yacc handle error parsing
        # The native error handling is better than panic mode with curly braces
    else:
        print("Error - EOF reached!")

