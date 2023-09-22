# r9 = constant 2
mov r9, 0x02

# addr [0,n] code space
# r6 = ptr to search target
# word 5000, byte A000
mov r6, 0xA000

search_start:

# left, middle, right ptr are r1, r2, r3
mov r1, 0x2000 # word 0x1000
mov r3, 0x8000 # word 0x4000

# r5 = search target
ld r5, r6
# if r5 (search target) is < 0, finish program
mov r10, finish
js r10, r5

search_loop:
# check if left ptr > right ptr, end loop
sub r7, r3, r1
mov r10, print_fail
js r10, r7

# calculate middle
add r2, r1, r3
# take the sum, divide by two
div r2, r2
# truncate the result by shifting right then left such that it points to a word
div r2, r2
mul r2, r2
# r4 = mem[middle]
ld r4, r2
sub r4, r4, r5

# if difference is zero (value found), jump to search_end
mov r10, print_success
jz r10, r4

# if difference is signed (search target > mem[middle]), set left ptr to middle + 1
mov r10, too_low
js r10, r4

# if difference is unsigned and not zero (target < mem[middle]), set right ptr to middle - 1
mov r10, too_high
jns r10, r4

print_fail:
# mov r0, 'F'
# mov r0, 'A'
# mov r0, 'I'
# mov r0, 'L'
# mov r0, '\n'
mov r10, search_end
jmp r10

print_success:
# mov r0, 'A'
# mov r0, 'M'
# mov r0, 'U'
# mov r0, '\n'
mov r10, search_end
jmp r10

too_low:
# set left ptr to middle + 2
add r1, r2, r9
mov r10, search_loop
jmp r10

too_high:
# set right ptr to middle - 2
sub r3, r2, r9
mov r10, search_loop
jmp r10

# jump here if left ptr > right ptr, or if target is found
search_end:
# increment search target ptr
add r6, r6, r9
mov r10, search_start
jmp r10

# jump here to terminate program
finish:
mov r15, 0xaaaa

