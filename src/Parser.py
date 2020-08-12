
from globalTypes import *
import pprint

import plylex as lex
import plyyacc as yacc

programa = None
posicion = None
progLong = None

def globales(prog, pos, long):
    global programa
    global posicion
    global progLong
    programa = prog
    posicion = pos
    progLong = long

def parser(imprime=True, graphic_tree=False):
    # Funcion principal de parser

    # Crear el lexer
    lexer = lex.lex()
    # Crear el parser
    parser = yacc.yacc(debug=False)
    # Hacer el parser con el programa dado y utilizando el lexer creado.
    #  Este incluye la función getToken que consume el parser.
    AST = parser.parse(
        tracking=True,
        input=programa,
        lexer=lexer
    )

    # Imprimir el arbol indentado dependiendo de la bandera
    if imprime:
        print("\nResulting AST:")
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(AST)
    
    # Imprimir el arbol grafico dependiendo de la bandera
    if graphic_tree:
        try:
            import lolviz
            g = lolviz.treeviz(AST)
            g.view()
        except ModuleNotFoundError:
            print("lolviz not found! - More info at: https://github.com/parrt/lolviz")
        except Exception:
            print((
                "Could not generate graph!\n"
                "Make sure Source.gv and Source.gv.pdf are "
                "not in use."
            ))
    
    if AST is not None: AST.source = programa
    return AST
