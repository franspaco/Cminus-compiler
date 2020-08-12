

## AST NODE

class Node:
    # NODE TYPES
    PROGRAM = 'PROG'
    FUNC = 'FUNC'
    DECLARATION = 'DECL'
    COMPOUND = 'COMPOUND'
    ASSIGN = 'ASSIGN'
    IF = 'IF'
    WHILE = 'WHILE'
    CALL = 'CALL'
    VAR = 'VAR'
    SIGM = 'SIGM'
    PROD = 'PROD'
    COMP = 'COMP'
    LITERAL = 'LIT'
    PARAM = 'PARAM'
    RETURN = 'RET'

    # DATA TYPES
    TYPE_VOID = 'VOID'
    TYPE_INT = 'INT'
    TYPE_INTARRAY = 'INT[]'

    # VAR CARDINALITY
    VAR_SINGLE = 'SINGLE'
    VAR_ARRAY = 'ARRAY'

    # BINARY OPERATIONS
    ADD = 'ADD'
    SUB = 'SUB'
    MUL = 'MUL'
    DIV = 'DIV'

    LET = 'LET'
    LT  = 'LT'
    GT  = 'GT'
    GET = 'GET'
    EQ  = 'EQ'
    NEQ = 'NEQ'

    @staticmethod
    def datatype(string: str) -> int:
        return {
            'int': Node.TYPE_INT,
            'void': Node.TYPE_VOID
        }[string.lower()]

    @staticmethod
    def op(string: str) -> int:
        return {
            '+':  Node.ADD,
            '-':  Node.SUB,
            '*':  Node.MUL,
            '/':  Node.DIV,
            '<=': Node.LET,
            '<':  Node.LT,
            '>':  Node.GT,
            '>=': Node.GET,
            '==': Node.EQ,
            '!=': Node.NEQ,
        }[string.lower()]

    def __init__(self, nodeType, lineno=0, linepos=0, **kwargs):
        self.nodeType = nodeType
        self.lineno = lineno
        self.linepos = linepos

        if 'p' in kwargs:
            self.lineno =  kwargs['p'].lineno(1)
            self.linepos = kwargs['p'].linepos(1)
            del kwargs['p']

        for k,v in kwargs.items():
            setattr(self, k, v)

    def __repr__(self):
        name = f", Name: {self.name}" if hasattr(self, 'name') else ''
        return f"<Node({self.nodeType}, At:{self.lineno}:{self.linepos}{name})>"

    # def __init__(self, nodeType, *, lineno=0, linepos=0, name=None, items=None, datatype=None, varcard=None, arrval=None, operation=None, a=None, b=None):
    #     self.nodeType = nodeType
    #     self.parent = None
    #     self.lineno = lineno
    #     self.linepos = linepos
    #     self.items = items
    #     self.name = name
    #     self.datatype = datatype
    #     self.varcard = varcard
    #     self.arrval = arrval
    #     self.operation = operation
    #     self.a = a
    #     self.b = b
