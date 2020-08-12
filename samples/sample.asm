    .data 
    out2str: .asciiz "Input: " 
    .text 
    .globl main 
input: 
    ori $v0,$0,4
    la $a0,out2str
    syscall                   # Print prompt
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
gcd: 
    addiu $sp,$sp,-16         # Start of gcd. Grow stack by: 16 (4 words)
    sw $ra,-4($fp)            # Save $ra to offset -4
                              # START OF COMPARISON
    li $t0,0                  # Load literal 0 to $t0
    addiu $sp,$sp,-4          # Grow stack for COMP
    sw $t0,4($sp)             # Save COMP.Right to stack
    lw $t0,-12($fp)           # Load value of: v
    sll $0,$0,0               # NOP: Wait for load delay slot
    lw $t1,4($sp)             # Load COMP.Right to $t1
    addiu $sp,$sp,4           # Shrink stack after COMP
    subu $t0,$t0,$t1          # $t0 = $t0 EQ $t1 (pt1)
    sltu $t0,$0,$t0           # $t0 = $t0 EQ $t1 (pt2)
    xori $t0,$t0,1            # $t0 = $t0 EQ $t1 (pt3)
    beq $t0,$0,else_0         # Evaluate if condition
    sll $0,$0,0               # NOP: Wait for delay slot
    lw $t0,-8($fp)            # Load value of: u
    sll $0,$0,0               # NOP: Wait for load delay slot
    j endif_0                 # Skip else
    sll $0,$0,0               # NOP: Wait for delay slot
else_0: 
                              # Start of call: gcd
    lw $t0,-12($fp)           # Load value of: v
    sll $0,$0,0               # NOP: Wait for load delay slot
    sw $t0,-8($sp)            # Save param #0 to $sp-8
                              # START OF SIGM
                              # START OF PROD
    lw $t0,-12($fp)           # Load value of: v
    sll $0,$0,0               # NOP: Wait for load delay slot
    addiu $sp,$sp,-4          # Grow stack for PROD
    sw $t0,4($sp)             # Save ADD.Right to stack
                              # START OF PROD
    lw $t0,-12($fp)           # Load value of: v
    sll $0,$0,0               # NOP: Wait for load delay slot
    addiu $sp,$sp,-4          # Grow stack for PROD
    sw $t0,4($sp)             # Save ADD.Right to stack
    lw $t0,-8($fp)            # Load value of: u
    sll $0,$0,0               # NOP: Wait for load delay slot
    lw $t1,4($sp)             # Load ADD.Right to $t1
    addiu $sp,$sp,4           # Shrink stack after PROD
    div $t0,$t1               # hilo = $t0 / $t1
    mflo $t0                  # Move lo to $t0
    lw $t1,4($sp)             # Load ADD.Right to $t1
    addiu $sp,$sp,4           # Shrink stack after PROD
    mult $t0,$t1              # hilo = $t0 * $t1
    mflo $t0                  # Move lo to $t0
    addiu $sp,$sp,-4          # Grow stack for SIGM
    sw $t0,4($sp)             # Save ADD.Right to stack
    lw $t0,-8($fp)            # Load value of: u
    sll $0,$0,0               # NOP: Wait for load delay slot
    lw $t1,4($sp)             # Load ADD.Right to $t1
    addiu $sp,$sp,4           # Shrink stack after SIGM
    subu $t0,$t0,$t1          # $t0 = $t0 - $t1
    sw $t0,-12($sp)           # Save param #1 to $sp-12
    sw $fp,($sp)              # Save $fp at top of stack.
    or $fp,$sp,$0             # Move fp to sp
    jal gcd                   # Jump and link to: gcd
    sll $0,$0,0               # NOP
    lw $fp,($sp)              # Restore fp. END OF CALL
    sll $0,$0,0               # NOP: Wait for load delay slot
endif_0: 
    lw $ra,-4($fp)            # Load $ra from offset -4
    addiu $sp,$sp,16          # Shrink stack by 16
    jr $ra                    # Jump back
    sll $0,$0,0               # NOP
main: 
    or $fp,$sp,$0             # Start of MAIN. Set fp to top of stack.
    addiu $sp,$sp,-12         # Grow stack by: 12 (3 words)
    sw $ra,($fp)              # Save $ra to offset 0
                              # Start of call: input
    sw $fp,($sp)              # Save $fp at top of stack.
    or $fp,$sp,$0             # Move fp to sp
    jal input                 # Jump and link to: input
    sll $0,$0,0               # NOP
    lw $fp,($sp)              # Restore fp. END OF CALL
    sll $0,$0,0               # NOP: Wait for load delay slot
    sw $t0,-4($fp)            # Save $t0 to: x
                              # Start of call: input
    sw $fp,($sp)              # Save $fp at top of stack.
    or $fp,$sp,$0             # Move fp to sp
    jal input                 # Jump and link to: input
    sll $0,$0,0               # NOP
    lw $fp,($sp)              # Restore fp. END OF CALL
    sll $0,$0,0               # NOP: Wait for load delay slot
    sw $t0,-8($fp)            # Save $t0 to: y
                              # Start of call: output
                              # Start of call: gcd
    lw $t0,-4($fp)            # Load value of: x
    sll $0,$0,0               # NOP: Wait for load delay slot
    sw $t0,-8($sp)            # Save param #0 to $sp-8
    lw $t0,-8($fp)            # Load value of: y
    sll $0,$0,0               # NOP: Wait for load delay slot
    sw $t0,-12($sp)           # Save param #1 to $sp-12
    sw $fp,($sp)              # Save $fp at top of stack.
    or $fp,$sp,$0             # Move fp to sp
    jal gcd                   # Jump and link to: gcd
    sll $0,$0,0               # NOP
    lw $fp,($sp)              # Restore fp. END OF CALL
    sll $0,$0,0               # NOP: Wait for load delay slot
    sw $t0,-8($sp)            # Save param #0 to $sp-8
    sw $fp,($sp)              # Save $fp at top of stack.
    or $fp,$sp,$0             # Move fp to sp
    jal output                # Jump and link to: output
    sll $0,$0,0               # NOP
    lw $fp,($sp)              # Restore fp. END OF CALL
    sll $0,$0,0               # NOP: Wait for load delay slot
    lw $ra,($fp)              # Load $ra from offset 0
    addiu $sp,$sp,12          # Shrink stack by 12
    jr $ra                    # Jump back
    sll $0,$0,0               # NOP
