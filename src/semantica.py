
from tree import Node

class Entry:
    def __init__(self, node: Node):
        self.pointer = None
        self.offset = None
        self.label = None
        self.node = node
        self.nodeType = node.nodeType
        self.name = node.name
        #self.lineno = node.lineno
        #self.linepos = node.linepos
        self.datatype = node.datatype
        if node.nodeType == Node.DECLARATION:
            self.varcard = node.varcard
            if node.varcard is Node.VAR_ARRAY:
                self.arrval = node.arrval
        elif node.nodeType == Node.PARAM:
            self.varcard = node.varcard
        elif node.nodeType == Node.FUNC:
            self.varcard = Node.VAR_SINGLE
            self.params = node.params
    
    def __repr__(self):
        return f"<Entry({self.name} - Kind:{self.nodeType}, Type: {self.datatype}, Card: {self.varcard})>"

class Table:
    def __init__(self, node, exhaustive=True):
        self.data = {}
        self.funcScope = None

        if node.nodeType == Node.PROGRAM:
            if exhaustive: 
                for item in node.items:
                    self.add(Entry(item))
            self.add(Entry(Node(Node.FUNC, name='input',  datatype=Node.TYPE_INT,  params=[])))
            self.add(Entry(Node(Node.FUNC, name='output', datatype=Node.TYPE_VOID, params=[
                Node(Node.PARAM, datatype=Node.TYPE_INT, varcard=Node.VAR_SINGLE)])))
        elif node.nodeType == Node.FUNC or node.nodeType == Node.COMPOUND:
            for decl in node.declarations:
                assertDeclarationCorrect(decl)
                self.add(Entry(decl))
            if node.nodeType == Node.FUNC:
                self.funcScope = Entry(node)
                for param in node.params:
                    self.add(Entry(param))
        else:
            raise Exception(f"ERROR: Unsupported node type for symbol tamble generation: {node.nodeType}")

        self.block = node.nodeType
        self.lineno = node.lineno
        self.linepos = node.linepos
    
    def setFuncScope(self, entry: Entry):
        self.funcScope = entry
    
    def add(self, entry):
        if self.contains(entry.name):
            error(entry.node, f"Name refefinition: {entry.name}")
            return
        self.data[entry.name] = entry
    
    def contains(self, name):
        return name in self.data

    def get(self, name):
        return self.data[name]

    def getDeclarations(self):
        return [entry for n,entry in self.data.items() if entry.nodeType is Node.DECLARATION]

    def getFunctions(self, skipMain=False):
        return [entry for n, entry in self.data.items() if entry.nodeType is Node.FUNC and (not skipMain or n != 'main')]

    def getParams(self):
        return [entry for n, entry in self.data.items() if entry.nodeType is Node.PARAM]

    def __repr__(self):
        scope = f"(For func: <{self.funcScope.name}>)" if self.funcScope is not None else f"Block: {self.block}"
        data = "\n" + "\n".join([f"\t{k.ljust(10)} -> {v}" for k, v in self.data.items()]) if len(self.data) > 0 else " EMPTY"
        return f"Table: {scope} ({self.lineno},{self.linepos}) {data}"


class ScopeStack:
    def __init__(self):
        self.stack = []

    def add(self, table):
        self.stack.append(table)

    @property
    def programTable(self):
        if len(self.stack)>0:
            return self.stack[0]
        return None

    def pop(self):
        self.stack.pop()

    def lookup(self, name):
        for table in reversed(self.stack):
            if table.contains(name):
                return table.get(name)
        return None

    def getFuncScope(self):
        for table in reversed(self.stack):
            if table.funcScope is not None:
                return table.funcScope
        return None


def tabla(node: Node, imprime=True, exhaustive=True):
    t = Table(node, exhaustive=exhaustive)
    if imprime: print(t)
    return t


program = None
print_tables = False
errors = 0


def semantica(tree: Node, imprime=True):
    if tree is None:
        return
    global program, print_tables
    program = tree.source.split('\n')
    print_tables = imprime
    stack = ScopeStack()
    scanTree(stack, tree)
    tree.errors = errors > 0


def error(node, message):
    global errors
    errors += 1
    print(f"ERROR: {message}")
    print(f"In line: {node.lineno}, col: {node.linepos}")
    print(f"{program[node.lineno-1]}\n{' ' * node.linepos}^\n")


def scanTree(stack: ScopeStack, node: Node):
    if node is None:
        return
    scope = node.nodeType is Node.PROGRAM or node.nodeType is Node.FUNC or node.nodeType is Node.COMPOUND
    if scope:
        table = tabla(node, imprime=print_tables, exhaustive=False)
        node.ST = table
        stack.add(table)

    # Nodes that are only explored
    if node.nodeType is Node.PROGRAM:
        for item in node.items:
            # Add item to table
            assertDeclarationCorrect(item)
            stack.programTable.add(Entry(item))
            if checkMain(item):
                node.main = item
            scanTree(stack, item)
        if not hasattr(node, 'main'):
            error(node, "Program does NOT contain main function")
        if print_tables: print(stack.programTable)
    elif node.nodeType is Node.FUNC:
        has_return = False
        for item in node.body:
            if item.nodeType is Node.RETURN:
                has_return = True
            scanTree(stack, item)
        if node.datatype is Node.TYPE_INT and not has_return:
            print(f"WARNING: Function {node.name} might not return INT")
    elif node.nodeType is Node.COMPOUND:
        for item in node.body:
            scanTree(stack, item)
    
    # Nodes that need type checking
    elif node.nodeType is Node.WHILE:
        assertWhileCorrect(stack, node)
        scanTree(stack, node.body)
    
    elif node.nodeType is Node.CALL:
        assertCallCorrect(stack, node)

    elif node.nodeType is Node.ASSIGN:
        assertAssignCorrect(stack, node)

    elif node.nodeType is Node.IF:
        assertIfCorrect(stack, node)
        scanTree(stack, node.ifthen)
        scanTree(stack, node.ifelse)

    elif node.nodeType is Node.RETURN:
        assertReturnCorrect(stack, node)

    elif node.nodeType is Node.CALL:
        assertCallCorrect(stack, node)

    elif node.nodeType is Node.VAR:
        assertReferenceCorrect(stack, node)

    elif node.nodeType is Node.SIGM or node.nodeType is Node.COMP or node.nodeType is Node.PROD:
        calcType(stack, node)

    if scope: stack.pop()


def assertDeclarationCorrect(node: Node):
    if node.nodeType == Node.FUNC:
        return
    elif node.nodeType == Node.DECLARATION:
        if node.datatype == Node.TYPE_VOID:
            error(node, "Cannot declare variable of empty type")

def checkMain(node: Node):
    if node.name != 'main' or node.nodeType != Node.FUNC or len(node.params) != 0:
        return False
    return True

def assertReturnCorrect(stack: ScopeStack, node: Node):
    funcScope = stack.getFuncScope()
    if funcScope is None:
        raise Exception("Invalid input: Return outside function!")
    expected = funcScope.datatype

    if expected is Node.TYPE_VOID and node.value is not None:
        error(node, f"Function {funcScope.name} should return type {expected}")

    elif expected is Node.TYPE_INT:
        if node.value is None:
            error(node, f"Function {funcScope.name} should return type {expected}")
        else:
            assertType(stack, node.value, expected, Node.VAR_SINGLE, vervose='return')


def assertIfCorrect(stack: ScopeStack, node: Node):
    assertType(stack, node.condition, Node.TYPE_INT, Node.VAR_SINGLE, vervose='condition')


def assertAssignCorrect(stack: ScopeStack, node: Node):
    to = node.to
    entry = stack.lookup(to.name)
    if entry is None:
        error(node, f"Could not find symbol: {to.name}")
        return None
    # Check l-value
    if entry.varcard is Node.VAR_ARRAY and to.varcard is Node.VAR_SINGLE:
        error(node.to, f"Cannot assign to an ARRAY")
        return None
    if entry.varcard is Node.VAR_ARRAY and to.varcard is Node.VAR_ARRAY:
        assertType(stack, to.arrval, Node.TYPE_INT, Node.VAR_SINGLE, vervose='array index')
    to.symbol = entry
    assertType(stack, node.value, entry.datatype, Node.VAR_SINGLE, vervose='assignment')
    return entry.datatype, Node.VAR_SINGLE
    

def assertWhileCorrect(stack: ScopeStack, node: Node):
    assertType(stack, node.condition, Node.TYPE_INT, Node.VAR_SINGLE, vervose='condition')

def assertCallCorrect(stack: ScopeStack, node: Node):
    entry = stack.lookup(node.name)
    if entry is None:
        error(node, f"Could not find symbol: {node.name}")
        return None
    if entry.nodeType is not Node.FUNC:
        error(node, f"Referenced symbol (defined as {entry.nodeType}) as a function")
        return None
    if len(node.args) != len(entry.params):
        error(node, f"Function {node.name} expects {len(entry.params)} param(s), found: {len(node.args)}")
    
    if entry.name == 'main':
        error(node, 'Function "main" cannot be called recursively.')

    for target, arg in zip(entry.params, node.args):
        assertType(stack, arg, target.datatype, target.varcard, vervose='argument')
    node.symbol = entry
    return entry


def assertReferenceCorrect(stack: ScopeStack, node: Node):
    entry = stack.lookup(node.name)
    if entry is None:
        error(node, f"Could not find symbol: {node.name}")
        return None
    if entry.nodeType is not Node.DECLARATION and entry.nodeType is not Node.PARAM:
        error(node, f"Referenced symbol (defined as {entry.nodeType}) as variable")
        return None
    if entry.varcard == Node.VAR_ARRAY and node.varcard == Node.VAR_ARRAY:
        assertType(stack, node.arrval, Node.TYPE_INT, Node.VAR_SINGLE, vervose='array index')
    node.symbol = entry
    return entry


def assertLiteralCorrect(node: Node):
    if node.value < -32768 or node.value > 32767:
        error(node, "Literal exceeds 16 bits")

def assertType(stack: ScopeStack, node, target_type, target_card, vervose: str = None):
    result = calcType(stack, node)
    if result is None:
        return
    found, fcard = result
    if found != target_type or fcard != target_card:
        vervose = f"in {vervose} " if vervose is not None else ''
        error(node, f"Type mismatch {vervose}- expected: {target_type} {target_card}, found: {found} {fcard}")


def calcType(stack: ScopeStack, node):
    
    if node.nodeType is Node.LITERAL:
        assertLiteralCorrect(node)
        return node.datatype, Node.VAR_SINGLE

    if node.nodeType is Node.VAR:
        entry = assertReferenceCorrect(stack, node)
        if entry is None:
            return None
        if entry.varcard is Node.VAR_ARRAY:
            if node.varcard is Node.VAR_ARRAY:
                cardinality = Node.VAR_SINGLE
            else:
                cardinality = Node.VAR_ARRAY
        else:
            if node.varcard is Node.VAR_ARRAY:
                error(node, "Reading variable as array")
                return None
            else:
                cardinality = Node.VAR_SINGLE

        return entry.datatype, cardinality

    if node.nodeType is Node.CALL:
        entry = assertCallCorrect(stack, node)
        if entry is None:
            return None
        return entry.datatype, entry.varcard

    if node.nodeType is Node.ASSIGN:
        result = assertAssignCorrect(stack, node)
        if result is None:
            return None
        return result[0], result[1]
        

    if node.nodeType is Node.COMP or node.nodeType is Node.SIGM or node.nodeType is Node.PROD:
        #print("HERE")
        lr = calcType(stack, node.left)
        rr = calcType(stack, node.right)
        if lr is None or rr is None:
            return None
        lt, lc = lr
        rt, rc = rr

        if lc != Node.VAR_SINGLE:
            error(node.left, f"Left operand cannot be ARRAY")
            return None
        if rc != Node.VAR_SINGLE:
            error(node.right, f"Right operand cannot be ARRAY")
            return None

        if lt == rt:
            return lt, lc
        else:
            error(node, f"Type mismatch {lt} and {rt}")
            return None


    print(f"DEBUG ERROR: calctype nodetype: {node.nodeType}")
    
