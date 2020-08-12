    .data 
    .text 
    .globl main 
input: 
    li $v0,5                  # Start of INPUT. Save 5 to $v0 for read int
    syscall                   # Read int syscall
    or $t0,$v0,$0             # Move input to $t0
    jr $ra                    # Jump back
    sll $0,$0,0               # NOP
output: 
    lw $a0,-8($fp)            # Start of OUTPUT. Load param from stack to $a0
    li $v0,1                  # Load 1 to $v0 for print int
    syscall                   # Print int syscall
    li $v0,11                 # Load 11 to $v0 for print char
    li $a0,10                 # Load a \n to $a0
    syscall                   # Print newline syscall
    jr $ra                    # Jump back
    sll $0,$0,0               # NOP
main: 
    or $fp,$sp,$0             # Start of MAIN. Set fp to top of stack.
    addiu $sp,$sp,-16         # Grow stack by: 16 (4 words)
    sw $ra,($fp)              # Save $ra to offset 0
    li $t0,5                  # Load literal 5 to $t0
    sw $t0,-12($fp)           # Save $t0 to: c
    sw $t0,-8($fp)            # Save $t0 to: b
    sw $t0,-4($fp)            # Save $t0 to: a
    lw $ra,($fp)              # Load $ra from offset 0
    addiu $sp,$sp,16          # Shrink stack by 16
    jr $ra                    # Jump back
    sll $0,$0,0               # NOP
