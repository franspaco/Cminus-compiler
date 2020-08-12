    .data 
    out2str: .asciiz "Input: " 
    x: .space 80 
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
minimo: 
    addiu $sp,$sp,-28         # Start of minimo. Grow stack by: 28 (7 words)
    sw $ra,-4($fp)            # Save $ra to offset -4
    li $t0,0                  # Load literal 0 to $t0
    sw $t0,-24($fp)           # Save $t0 to: k
    li $t0,0                  # Load literal 0 to $t0
    sll $t0,$t0,2             # Multiply offset by 4
    lw $t1,-8($fp)            # Load pointer for ARRAY a to $t1
    sll $0,$0,0               # NOP: Wait for load delay slot
    addu $t0,$t1,$t0          # Add $t0 to $t1 to get absolute pointer.
    lw $t0,($t0)              # Load value to $t0
    sll $0,$0,0               # NOP: Wait for load delay slot
    sw $t0,-20($fp)           # Save $t0 to: x
    li $t0,1                  # Load literal 1 to $t0
    sw $t0,-16($fp)           # Save $t0 to: i
while_0: 
                              # START OF COMPARISON
    lw $t0,-12($fp)           # Load value of: high
    sll $0,$0,0               # NOP: Wait for load delay slot
    addiu $sp,$sp,-4          # Grow stack for COMP
    sw $t0,4($sp)             # Save COMP.Right to stack
    lw $t0,-16($fp)           # Load value of: i
    sll $0,$0,0               # NOP: Wait for load delay slot
    lw $t1,4($sp)             # Load COMP.Right to $t1
    addiu $sp,$sp,4           # Shrink stack after COMP
    slt $t0,$t0,$t1           # $t0 = $t0 LT $t1
    beq $t0,$0,endwhile_0     # Evaluate while condition
    sll $0,$0,0               # NOP: Wait for delay slot
                              # START OF COMPARISON
    lw $t0,-20($fp)           # Load value of: x
    sll $0,$0,0               # NOP: Wait for load delay slot
    addiu $sp,$sp,-4          # Grow stack for COMP
    sw $t0,4($sp)             # Save COMP.Right to stack
    lw $t0,-16($fp)           # Load value of: i
    sll $0,$0,0               # NOP: Wait for load delay slot
    sll $t0,$t0,2             # Multiply offset by 4
    lw $t1,-8($fp)            # Load pointer for ARRAY a to $t1
    sll $0,$0,0               # NOP: Wait for load delay slot
    addu $t0,$t1,$t0          # Add $t0 to $t1 to get absolute pointer.
    lw $t0,($t0)              # Load value to $t0
    sll $0,$0,0               # NOP: Wait for load delay slot
    lw $t1,4($sp)             # Load COMP.Right to $t1
    addiu $sp,$sp,4           # Shrink stack after COMP
    slt $t0,$t0,$t1           # $t0 = $t0 LT $t1
    beq $t0,$0,endif_1        # Evaluate if condition
    sll $0,$0,0               # NOP: Wait for delay slot
    lw $t0,-16($fp)           # Load value of: i
    sll $0,$0,0               # NOP: Wait for load delay slot
    sll $t0,$t0,2             # Multiply offset by 4
    lw $t1,-8($fp)            # Load pointer for ARRAY a to $t1
    sll $0,$0,0               # NOP: Wait for load delay slot
    addu $t0,$t1,$t0          # Add $t0 to $t1 to get absolute pointer.
    lw $t0,($t0)              # Load value to $t0
    sll $0,$0,0               # NOP: Wait for load delay slot
    sw $t0,-20($fp)           # Save $t0 to: x
    lw $t0,-16($fp)           # Load value of: i
    sll $0,$0,0               # NOP: Wait for load delay slot
    sw $t0,-24($fp)           # Save $t0 to: k
endif_1: 
                              # START OF SIGM
    li $t0,1                  # Load literal 1 to $t0
    addiu $sp,$sp,-4          # Grow stack for SIGM
    sw $t0,4($sp)             # Save ADD.Right to stack
    lw $t0,-16($fp)           # Load value of: i
    sll $0,$0,0               # NOP: Wait for load delay slot
    lw $t1,4($sp)             # Load ADD.Right to $t1
    addiu $sp,$sp,4           # Shrink stack after SIGM
    addu $t0,$t0,$t1          # $t0 = $t0 + $t1
    sw $t0,-16($fp)           # Save $t0 to: i
    j while_0                 # Jump back to while
endwhile_0: 
    sll $0,$0,0               # NOP: Wait for delay slot
    lw $t0,-24($fp)           # Load value of: k
    sll $0,$0,0               # NOP: Wait for load delay slot
    lw $ra,-4($fp)            # Load $ra from offset -4
    addiu $sp,$sp,28          # Shrink stack by 28
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
    sw $t0,-8($fp)            # Save $t0 to: high
    li $t0,0                  # Load literal 0 to $t0
    sw $t0,-4($fp)            # Save $t0 to: i
while_2: 
                              # START OF COMPARISON
    lw $t0,-8($fp)            # Load value of: high
    sll $0,$0,0               # NOP: Wait for load delay slot
    addiu $sp,$sp,-4          # Grow stack for COMP
    sw $t0,4($sp)             # Save COMP.Right to stack
    lw $t0,-4($fp)            # Load value of: i
    sll $0,$0,0               # NOP: Wait for load delay slot
    lw $t1,4($sp)             # Load COMP.Right to $t1
    addiu $sp,$sp,4           # Shrink stack after COMP
    slt $t0,$t0,$t1           # $t0 = $t0 LT $t1
    beq $t0,$0,endwhile_2     # Evaluate while condition
    sll $0,$0,0               # NOP: Wait for delay slot
                              # Start of call: input
    sw $fp,($sp)              # Save $fp at top of stack.
    or $fp,$sp,$0             # Move fp to sp
    jal input                 # Jump and link to: input
    sll $0,$0,0               # NOP
    lw $fp,($sp)              # Restore fp. END OF CALL
    sll $0,$0,0               # NOP: Wait for load delay slot
    addiu $sp,$sp,-4          # Grow stack for ASSIGN ARR
    sw $t0,4($sp)             # Save ASSIGN VALUE to stack
    lw $t0,-4($fp)            # Load value of: i
    sll $0,$0,0               # NOP: Wait for load delay slot
    lw $t1,4($sp)             # Load ASSIGN VALUE to $t1
    addiu $sp,$sp,4           # Shrink stack after ASSIGN ARR
    sll $t0,$t0,2             # Multiply offset by 4
    la $t2,x                  # Load address of x to $t2 (Global)
    addu $t0,$t2,$t0          # Add $t0 to $t2 to get absolute pointer.
    sw $t1,($t0)              # Save value to address in $t0
                              # START OF SIGM
    li $t0,1                  # Load literal 1 to $t0
    addiu $sp,$sp,-4          # Grow stack for SIGM
    sw $t0,4($sp)             # Save ADD.Right to stack
    lw $t0,-4($fp)            # Load value of: i
    sll $0,$0,0               # NOP: Wait for load delay slot
    lw $t1,4($sp)             # Load ADD.Right to $t1
    addiu $sp,$sp,4           # Shrink stack after SIGM
    addu $t0,$t0,$t1          # $t0 = $t0 + $t1
    sw $t0,-4($fp)            # Save $t0 to: i
    j while_2                 # Jump back to while
endwhile_2: 
    sll $0,$0,0               # NOP: Wait for delay slot
                              # Start of call: minimo
    la $t0,x                  # Load address of x to $t0 (Global)
    sw $t0,-8($sp)            # Save param #0 to $sp-8
    lw $t0,-8($fp)            # Load value of: high
    sll $0,$0,0               # NOP: Wait for load delay slot
    sw $t0,-12($sp)           # Save param #1 to $sp-12
    sw $fp,($sp)              # Save $fp at top of stack.
    or $fp,$sp,$0             # Move fp to sp
    jal minimo                # Jump and link to: minimo
    sll $0,$0,0               # NOP
    lw $fp,($sp)              # Restore fp. END OF CALL
    sll $0,$0,0               # NOP: Wait for load delay slot
    sw $t0,-4($fp)            # Save $t0 to: i
                              # Start of call: output
    lw $t0,-4($fp)            # Load value of: i
    sll $0,$0,0               # NOP: Wait for load delay slot
    sw $t0,-8($sp)            # Save param #0 to $sp-8
    sw $fp,($sp)              # Save $fp at top of stack.
    or $fp,$sp,$0             # Move fp to sp
    jal output                # Jump and link to: output
    sll $0,$0,0               # NOP
    lw $fp,($sp)              # Restore fp. END OF CALL
    sll $0,$0,0               # NOP: Wait for load delay slot
                              # Start of call: output
    lw $t0,-4($fp)            # Load value of: i
    sll $0,$0,0               # NOP: Wait for load delay slot
    sll $t0,$t0,2             # Multiply offset by 4
    la $t1,x                  # Load address of x to $t1 (Global)
    addu $t0,$t1,$t0          # Add $t0 to $t1 to get absolute pointer.
    lw $t0,($t0)              # Load value to $t0
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
