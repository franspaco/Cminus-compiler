
# Archivo de prueba de Parser.py
from globalTypes import *
from Parser import globales, parser

from semantica import semantica

from cgen import codeGen

with open('bubblesort.cm', 'r') as f:
    programa = f.read()     # lee todo el archivo a compilar
progLong = len(programa)   # longitud original del programa
programa = programa + '$'   # agregar un caracter $ que represente EOF
posicion = 0       # posición del caracter actual del string
# función para pasar los valores iniciales de las variables globales
globales(programa, posicion, progLong)

import sys

graph = True if len(sys.argv)>1 else False

# Nota: se agrega una segunda bandera para crear el arbol grafico
AST = parser(False, graph)
semantica(AST, False)
codeGen(AST, "output.asm")
