"""
Generates MIPS ASM from an AST with annotations

Notes:
Results are always expected in $t0
No register is safe, always store to stack
"""

from tree import Node

class Ins:
    @staticmethod
    def nop(comment="NOP"):
        return Ins('sll $0,$0,0', comment=comment)

    @staticmethod
    def syscall(comment=None):
        return Ins('syscall', comment=comment)

    @staticmethod
    def data():
        return Ins('.data')

    @staticmethod
    def text():
        return Ins('.text')

    @staticmethod
    def label(name):
        return Ins(name + ":", indent=False)

    @staticmethod
    def move(target, source, comment=None):
        return Ins('or', target, source, '$0', comment=comment)

    @staticmethod
    def load(target, offset='', reg='$fp', comment=None):
        return Ins('lw', target, f"{offset}({reg})", comment=comment)

    @staticmethod
    def save(source, offset='', reg='$fp', comment=None):
        return Ins('sw', source, f"{offset}({reg})", comment=comment)

    @staticmethod
    def li(target, value, comment=None):
        return Ins('li', target, value, comment=comment)

    @staticmethod
    def stackGrow(no_bytes, comment=None):
        return Ins('addiu', '$sp', '$sp', -abs(no_bytes), comment=comment)

    @staticmethod
    def stackShrink(no_bytes, comment=None):
        return Ins('addiu', '$sp', '$sp', abs(no_bytes), comment=comment)
    
    @staticmethod
    def declaration(name, *args):
        return Ins(name + ": " + " ".join([str(n) for n in args]))

    @staticmethod
    def comment(comment: str):
        return Ins('', comment=comment)

    def __init__(self, ins, *args, indent=True, comment=None, **kwargs):
        self.ins = ins
        self.args = args
        self.indent = indent
        self.comment = comment
    
    def build(self):
        indent = '    ' if self.indent else ''
        line = indent + self.ins + " " + ",".join([str(n) for n in self.args])
        if self.comment is not None and type(self.comment) is str:
            line += " "*(30 - len(line)) + "# " + self.comment
        return line + "\n"

    def __repr__(self):
        return self.build()

class ASM():
    def __init__(self):
        self.content = []
        self.identifier = 0
        self.offset_stack = []

    def genID(self):
        val = str(self.identifier)
        self.identifier += 1
        return val

    def offset_push(self, offset):
        self.offset_stack.append(offset)

    def offset_pop(self):
        self.offset_stack.pop()
    
    def offset_peek(self):
        if len(self.offset_stack) > 0:
            return self.offset_stack[-1]
        return None
    
    def add(self, ins: Ins):
        self.content.append(ins)

    def build(self):
        return ''.join([item.build() for item in self.content])


def codeGen(tree: Node, file: str):
    if tree.errors:
        print("Errors found, compilation failed!")
        return
    
    program = ASM()
    makeASM(tree, program)

    asmtxt = program.build()

    with open(file, 'w') as f:
        f.write(asmtxt)
    
    print("Compilation done!")

class UnimplementedError(Exception):
    pass

def makeASM(node: Node, asm: ASM):
    if node.nodeType == Node.PROGRAM:
        makeProgram(node, asm)
    elif node.nodeType == Node.FUNC:
        makeFunction(node, asm)
    elif node.nodeType == Node.CALL:
        makeFuncCall(node, asm)
    elif node.nodeType == Node.LITERAL:
        makeLiteral(node, asm)
    elif node.nodeType == Node.VAR:
        makeVar(node, asm)
    elif node.nodeType == Node.ASSIGN:
        makeAssign(node, asm)
    elif node.nodeType == Node.RETURN:
        makeReturn(node, asm)
    elif node.nodeType == Node.SIGM:
        makeSigma(node, asm)
    elif node.nodeType == Node.PROD:
        makeProd(node, asm)
    elif node.nodeType == Node.COMP:
        makeComparison(node, asm)
    elif node.nodeType == Node.WHILE:
        makeWhile(node, asm)
    elif node.nodeType == Node.WHILE:
        makeWhile(node, asm)
    elif node.nodeType == Node.WHILE:
        makeWhile(node, asm)
    elif node.nodeType == Node.IF:
        makeIf(node, asm)
    elif node.nodeType == Node.COMPOUND:
        makeCompound(node, asm)
    else:
        raise UnimplementedError(f"Not implemented yet: {node.nodeType}")


def makeCompound(comp: Node, asm: ASM):
    spDelta = 0
    if len(comp.declarations) > 0:
        spfpDelta = asm.offset_peek()
        for decl in comp.ST.getDeclarations():
            if decl.varcard == Node.VAR_SINGLE:
                decl.offset = spfpDelta
                spDelta -= 4
                spfpDelta -= 4
            elif decl.varcard == Node.VAR_ARRAY:
                spDelta -= 4 * decl.arrval
                spfpDelta -= 4 * decl.arrval
                decl.offset = spDelta + 4
        asm.offset_push(spfpDelta)
        asm.add(Ins('addiu', '$sp', '$sp', spDelta, comment=f"Grow stack by: {-spDelta} ({int(-spDelta/4)} words)"))
    for item in comp.body:
        makeASM(item, asm)
    if len(comp.declarations) > 0:
        asm.add(Ins('addiu', '$sp', '$sp', -spDelta, comment=f"Shrink stack by {-spDelta}"))
        asm.offset_pop()

def makeIf(ifnode: Node, asm: ASM):
    ident = asm.genID()
    makeASM(ifnode.condition, asm)
    on_false_jmp_to = 'else_' if ifnode.ifelse is not None else 'endif_'
    asm.add(Ins('beq', '$t0', '$0', on_false_jmp_to + ident, comment="Evaluate if condition"))
    asm.add(Ins.nop(comment="NOP: Wait for delay slot"))
    makeASM(ifnode.ifthen, asm)
    if ifnode.ifelse != None:
        asm.add(Ins('j', 'endif_'+ident, comment="Skip else"))
        asm.add(Ins.nop(comment="NOP: Wait for delay slot"))
        asm.add(Ins.label('else_'+ident))
        makeASM(ifnode.ifelse, asm)
    asm.add(Ins.label('endif_'+ident))


def makeWhile(wnode: Node, asm: ASM):
    ident = asm.genID()

    # If body is compound-statement alloc vars
    spDelta = 0
    if wnode.body.nodeType == Node.COMPOUND and len(wnode.body.declarations) > 0:
        spfpDelta = asm.offset_peek()
        for decl in wnode.body.ST.getDeclarations():
            if decl.varcard == Node.VAR_SINGLE:
                decl.offset = spfpDelta
                spDelta -= 4
                spfpDelta -= 4
            elif decl.varcard == Node.VAR_ARRAY:
                spDelta -= 4 * decl.arrval
                spfpDelta -= 4 * decl.arrval
                decl.offset = spDelta + 4
        asm.offset_push(spfpDelta)
        asm.add(Ins('addiu', '$sp', '$sp', spDelta, comment=f"Grow stack by: {-spDelta} ({int(-spDelta/4)} words)"))
    asm.add(Ins.label('while_' + ident))
    makeASM(wnode.condition, asm)
    asm.add(Ins('beq', '$t0', '$0', 'endwhile_' + ident, comment="Evaluate while condition"))
    asm.add(Ins.nop(comment="NOP: Wait for delay slot"))
    if wnode.body.nodeType != Node.COMPOUND:
        makeASM(wnode.body, asm)
    else:
        for item in wnode.body.body:
            makeASM(item, asm)
    asm.add(Ins('j', 'while_' + ident, comment="Jump back to while"))
    asm.add(Ins.label('endwhile_' + ident))
    asm.add(Ins.nop(comment="NOP: Wait for delay slot"))

    # If body is compound-statement de-alloc vars
    if wnode.body.nodeType == Node.COMPOUND and len(wnode.body.declarations) > 0:
        asm.add(Ins('addiu', '$sp', '$sp', -spDelta, comment=f"Shrink stack by {-spDelta}"))
        asm.offset_pop()

def makeComparison(comp: Node, asm: ASM):
    asm.add(Ins.comment("START OF COMPARISON"))
    makeASM(comp.right, asm)
    asm.add(Ins.stackGrow(4, comment="Grow stack for COMP"))
    asm.add(Ins.save('$t0', 4, '$sp', comment="Save COMP.Right to stack"))
    makeASM(comp.left, asm)
    asm.add(Ins.load('$t1', 4, '$sp', comment="Load COMP.Right to $t1"))
    asm.add(Ins.stackShrink(4, comment="Shrink stack after COMP"))
    # Left: $t0 | Right: $t1
    if comp.operation == Node.LET:
        asm.add(Ins('slt', '$t0', '$t1', '$t0', comment="$t0 = $t0 LET $t1 (pt1)"))
        asm.add(Ins('xori', '$t0', '$t0', 1, comment="$t0 = $t0 LET $t1 (pt2)"))
    elif comp.operation == Node.LT:
        asm.add(Ins('slt', '$t0', '$t0', '$t1', comment="$t0 = $t0 LT $t1"))
    elif comp.operation == Node.GT:
        asm.add(Ins('slt', '$t0', '$t1', '$t0', comment="$t0 = $t0 GT $t1"))
    elif comp.operation == Node.GET:
        asm.add(Ins('slt', '$t0', '$t0', '$t1', comment="$t0 = $t0 GET $t1 (pt1)"))
        asm.add(Ins('xori', '$t0', '$t0', 1, comment="$t0 = $t0 GET $t1 (pt2)"))
    elif comp.operation == Node.EQ:
        asm.add(Ins('subu', '$t0', '$t0', '$t1', comment="$t0 = $t0 EQ $t1 (pt1)"))
        asm.add(Ins('sltu', '$t0', '$0', '$t0', comment="$t0 = $t0 EQ $t1 (pt2)"))
        asm.add(Ins('xori', '$t0', '$t0', 1, comment="$t0 = $t0 EQ $t1 (pt3)"))
    elif comp.operation == Node.NEQ:
        asm.add(Ins('subu', '$t0', '$t0', '$t1', comment="$t0 = $t0 NEQ $t1 (pt1)"))
        asm.add(Ins('sltu', '$t0', '$0', '$t0', comment="$t0 = $t0 NEQ $t1 (pt1)"))

def makeProd(prod: Node, asm: ASM):
    asm.add(Ins.comment("START OF PROD"))
    makeASM(prod.right, asm)
    asm.add(Ins.stackGrow(4, comment="Grow stack for PROD"))
    asm.add(Ins.save('$t0', 4, '$sp', comment="Save ADD.Right to stack"))
    makeASM(prod.left, asm)
    asm.add(Ins.load('$t1', 4, '$sp', comment="Load ADD.Right to $t1"))
    asm.add(Ins.stackShrink(4, comment="Shrink stack after PROD"))
    if prod.operation == Node.MUL:
        asm.add(Ins('mult', '$t0', '$t1', comment="hilo = $t0 * $t1"))
    elif prod.operation == Node.DIV:
        asm.add(Ins('div', '$t0', '$t1', comment="hilo = $t0 / $t1"))
    asm.add(Ins('mflo', '$t0', comment="Move lo to $t0"))


def makeSigma(sigm: Node, asm: ASM):
    asm.add(Ins.comment("START OF SIGM"))
    makeASM(sigm.right, asm)
    asm.add(Ins.stackGrow(4, comment="Grow stack for SIGM"))
    asm.add(Ins.save('$t0', 4, '$sp', comment="Save ADD.Right to stack"))
    makeASM(sigm.left, asm)
    asm.add(Ins.load('$t1', 4, '$sp', comment="Load ADD.Right to $t1"))
    asm.add(Ins.stackShrink(4, comment="Shrink stack after SIGM"))
    if sigm.operation == Node.ADD:
        asm.add(Ins('addu', '$t0', '$t0', '$t1', comment="$t0 = $t0 + $t1"))
    elif sigm.operation == Node.SUB:
        asm.add(Ins('subu', '$t0', '$t0', '$t1', comment="$t0 = $t0 - $t1"))

def makeReturn(ret: Node, asm: ASM):
    makeASM(ret.value, asm)

def makeAssign(assign: Node, asm: ASM):
    makeASM(assign.value, asm)
    tosymb = assign.to.symbol
    if tosymb.varcard == Node.VAR_SINGLE:
        if tosymb.offset is None:
            asm.add(Ins('sw', '$t0', tosymb.pointer, comment=f"Save $t0 to: {tosymb.name} (Global)"))
        else:
            asm.add(Ins.save('$t0', tosymb.offset, comment=f"Save $t0 to: {tosymb.name}"))
    else:
        asm.add(Ins.stackGrow(4, comment="Grow stack for ASSIGN ARR"))
        asm.add(Ins.save('$t0', 4, '$sp', comment="Save ASSIGN VALUE to stack"))
        makeASM(assign.to.arrval, asm)
        asm.add(Ins.load('$t1', 4, '$sp', comment="Load ASSIGN VALUE to $t1"))
        asm.add(Ins.stackShrink(4, comment="Shrink stack after ASSIGN ARR"))
        asm.add(Ins('sll', '$t0', '$t0', 2, comment="Multiply offset by 4"))
        if tosymb.offset is None:
            # Var is Global
            asm.add(Ins('la', '$t2', tosymb.pointer, comment=f"Load address of {tosymb.name} to $t2 (Global)"))
        else:
            # Var is local
            if tosymb.nodeType == Node.PARAM:
                # Symbol is a param, we already have a pointer, just need to load into $t2
                asm.add(Ins.load('$t2', tosymb.offset, comment=f"Load pointer for ARRAY {tosymb.name} to $t0"))
                asm.add(Ins.nop(comment="NOP: Wait for load delay slot"))
            else:
                # Array is being referenced locally
                asm.add(Ins('addiu', '$t2', '$fp', tosymb.offset, comment=f"Load address of {tosymb.name} to $t2"))
        asm.add(Ins('addu', '$t0', '$t2', '$t0', comment="Add $t0 to $t2 to get absolute pointer."))
        asm.add(Ins.save('$t1', reg='$t0', comment="Save value to address in $t0"))

def makeVar(var: Node, asm: ASM):
    symbol = var.symbol
    if symbol.varcard == Node.VAR_SINGLE:
        # Var is single
        if symbol.offset is None:
            asm.add(Ins('lw', '$t0', symbol.pointer, comment=f"Load value of: {var.name} (Global)"))
        else:
            asm.add(Ins.load('$t0', symbol.offset, comment=f"Load value of: {var.name}"))
        asm.add(Ins.nop(comment="NOP: Wait for load delay slot"))
    else:
        # Var is array
        if var.varcard == Node.VAR_SINGLE:
            # Var is referenced as pointer
            if symbol.offset is None:
                # Var is global
                asm.add(Ins('la', '$t0', symbol.pointer, comment=f"Load address of {symbol.name} to $t0 (Global)"))
            else:
                # Var is local
                if symbol.nodeType == Node.PARAM:
                    # Symbol is a param, we already have a pointer, just need to load into $t0
                    asm.add(Ins.load('$t0', symbol.offset, comment=f"Load pointer for ARRAY {symbol.name} to $t0"))
                    asm.add(Ins.nop(comment="NOP: Wait for load delay slot"))
                else:
                    # Array is being referenced locally
                    asm.add(Ins('addiu', '$t0', '$fp', symbol.offset, comment=f"Load address of {symbol.name} to $t0"))

        elif var.varcard == Node.VAR_ARRAY:
            # Var is referenced with index => add index to pointer and return value
            makeASM(var.arrval, asm)
            asm.add(Ins('sll', '$t0', '$t0', 2, comment="Multiply offset by 4"))
            if symbol.offset is None:
                # Var is global
                asm.add(Ins('la', '$t1', symbol.pointer, comment=f"Load address of {symbol.name} to $t1 (Global)"))
            else:
                # Var is local
                if symbol.nodeType == Node.PARAM:
                    # Symbol is a param, we already have a pointer, just need to load into $t1
                    asm.add(Ins.load('$t1', symbol.offset, comment=f"Load pointer for ARRAY {symbol.name} to $t1"))
                    asm.add(Ins.nop(comment="NOP: Wait for load delay slot"))
                else:
                    # Array is being referenced locally
                    asm.add(Ins('addiu', '$t1', '$fp', symbol.offset, comment=f"Load address of {symbol.name} to $t1"))
            asm.add(Ins('addu', '$t0', '$t1', '$t0', comment="Add $t0 to $t1 to get absolute pointer."))
            asm.add(Ins.load('$t0', reg='$t0', comment="Load value to $t0"))
            asm.add(Ins.nop(comment="NOP: Wait for load delay slot"))


def makeLiteral(lit: Node, asm: ASM):
    asm.add(Ins.li('$t0', lit.value, comment=f"Load literal {lit.value} to $t0"))

def makeFuncCall(call: Node, asm: ASM):
    asm.add(Ins.comment(f"Start of call: {call.name}"))
    spDelta = -8
    for arg in call.args:
        makeASM(arg, asm)
        asm.add(Ins.save('$t0', spDelta, '$sp', comment=f"Save param #{int(-(spDelta+8)/4)} to $sp-{-spDelta}"))
        spDelta -= 4
    asm.add(Ins.save('$fp', reg='$sp', comment=f"Save $fp at top of stack."))
    asm.add(Ins.move('$fp', '$sp', comment="Move fp to sp"))
    
    asm.add(Ins('jal', call.name, comment=f"Jump and link to: {call.name}"))
    asm.add(Ins.nop())
    asm.add(Ins.load('$fp', reg='$sp', comment="Restore fp. END OF CALL"))
    asm.add(Ins.nop(comment="NOP: Wait for load delay slot"))


def makeFunction(func: Node, asm: ASM):
    if func.name == 'output':
        makeOutputFunc(func, asm)
    elif func.name == 'input':
        makeInputFunc(func, asm)
    elif func.name == 'main':
        makeMainFunc(func, asm)
    else:
        makeGenericFunction(func, asm)

def makeGenericFunction(func: Node, asm: ASM):
    asm.add(Ins.label(func.name))
    spDelta = -8
    for param in func.ST.getParams():
        param.offset = spDelta
        spDelta -= 4
    for decl in func.ST.getDeclarations():
        if decl.varcard == Node.VAR_SINGLE:
            decl.offset = spDelta
            spDelta -= 4
        elif decl.varcard == Node.VAR_ARRAY:
            spDelta -= 4 * decl.arrval
            decl.offset = spDelta + 4
    asm.offset_push(spDelta)
    asm.add(Ins('addiu', '$sp', '$sp', spDelta, comment=f"Start of {func.name}. Grow stack by: {-spDelta} ({int(-spDelta/4)} words)"))
    asm.add(Ins.save('$ra', -4, comment="Save $ra to offset -4"))

    for item in func.body:
        makeASM(item, asm)

    asm.add(Ins.load('$ra', -4, comment="Load $ra from offset -4"))
    asm.add(Ins('addiu', '$sp', '$sp', -spDelta, comment=f"Shrink stack by {-spDelta}"))
    asm.add(Ins('jr', '$ra', comment="Jump back"))
    asm.add(Ins.nop())
    asm.offset_pop()


def makeMainFunc(func: Node, asm: ASM):
    asm.add(Ins.label(func.name))
    spDelta = -4
    for decl in func.ST.getDeclarations():
        if decl.varcard == Node.VAR_SINGLE:
            decl.offset = spDelta
            spDelta -= 4
        elif decl.varcard == Node.VAR_ARRAY:
            spDelta -= 4 * decl.arrval
            decl.offset = spDelta + 4
    asm.offset_push(spDelta)
    asm.add(Ins.move('$fp', '$sp', comment="Start of MAIN. Set fp to top of stack."))
    asm.add(Ins('addiu', '$sp', '$sp', spDelta, comment=f"Grow stack by: {-spDelta} ({int(-spDelta/4)} words)"))
    asm.add(Ins.save('$ra', comment="Save $ra to offset 0"))

    for item in func.body:
        makeASM(item, asm)

    asm.add(Ins.load('$ra', comment="Load $ra from offset 0"))
    asm.add(Ins('addiu', '$sp', '$sp', -spDelta, comment=f"Shrink stack by {-spDelta}"))
    asm.add(Ins('jr', '$ra', comment="Jump back"))
    asm.add(Ins.nop())
    asm.offset_pop()

def makeInputFunc(func: Node, asm: ASM):
    asm.add(Ins.label('input'))
    asm.add(Ins('ori', '$v0', '$0', 4))
    asm.add(Ins('la', '$a0', 'out2str'))
    asm.add(Ins.syscall(comment="Print prompt"))
    asm.add(Ins('li', '$v0', 5, comment="Start of INPUT. Save 5 to $v0 for read int"))
    asm.add(Ins.syscall(comment="Read int syscall"))
    asm.add(Ins.move('$t0', '$v0', comment="Move input to $t0"))
    asm.add(Ins('jr', '$ra', comment="Jump back"))
    asm.add(Ins.nop())


def makeOutputFunc(func: Node, asm: ASM):
    asm.add(Ins.label('output'))
    asm.add(Ins.load('$a0', -8, comment="Start of OUTPUT. Load param from stack to $a0"))
    asm.add(Ins('li', '$v0', 1, comment="Load 1 to $v0 for print int"))
    asm.add(Ins.syscall(comment="Print int syscall"))
    asm.add(Ins('li', '$v0', 11, comment="Load 11 to $v0 for print char"))
    asm.add(Ins('li', '$a0', 10, comment="Load a \\n to $a0"))
    asm.add(Ins.syscall(comment="Print newline syscall"))
    asm.add(Ins('jr', '$ra', comment="Jump back"))
    asm.add(Ins.nop())

def makeProgram(node: Node, asm: ASM):
    globVars = node.ST.getDeclarations()
    funcs = node.ST.getFunctions(skipMain=False)

    asm.add(Ins.data())
    asm.add(Ins.declaration('out2str', '.asciiz', '"Input: "'))
    for var in globVars:
        var.pointer = var.name
        if var.varcard is Node.VAR_SINGLE:
            asm.add(Ins.declaration(var.name, '.word', 0))
        elif var.varcard is Node.VAR_ARRAY:
            size = var.arrval
            asm.add(Ins.declaration(var.name, '.space', 4*size))
    
    asm.add(Ins.text())
    asm.add(Ins('.globl main'))
    for func in funcs:
        makeASM(func.node, asm)

