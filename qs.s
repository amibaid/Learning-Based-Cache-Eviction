# stack ptr in r1, bottom of stack in r4
# stack bottom at word 0x7000
mov r4, 0xA000 # word 0x7000
mov r1, 0xA000

# left bound of current sort in r2, rb in r3
# words [0x1000,0x5000] are the sorting content
mov r2, 0x2000
mov r3, 0x3000
# push initial bounds on the stack
push r2
push r3

quicksort:
    # if stack ptr has reached bottom, terminate
    sub r15, r1, r4 # x = stack_ptr - bottom
    mov r14, finish
    jns r14, r15 # if stack_ptr not less than bottom

    # otherwise we pop the left and right ptrs
    pop r3 # read the right ptr
    pop r2 # left ptr

    # if L >= R (bad LR) == L !< R
    sub r15, r2, r3
    mov r14, quicksort
    jns r14, r15 # (if L !< R, continue)

    # pivot in r5
    add r5, r3, r2
    div r5, r5
    div r5, r5
    mul r5, r5

    ld r5, r5 # pivot value = mem[pivot_index]

    # left_search_ptr in r6
    # mov r6, r2
    sub r6, r2, r0
    # right_search_ptr in r7
    # mov r7, r3
    sub r7, r3, r0

    while_ptr_not_converged:
        # left loop, find the leftmost out of place element
        # left ptr for partition in r6
        # while L < R and mem[L] < pivot, increment L
            # jump to condition first, we will jump back and run loop contents if it is met
            mov r15, L_lt_R_and_memL_lteq_pivot_condition
            jmp r15
            L_lt_R_and_memL_lteq_pivot:
                # the condition is met, increment L
                mov r15, 0x0002
                add r6, r6, r15
            L_lt_R_and_memL_lteq_pivot_condition:
            # if condition is met, jump to L_lt_R_and_memL_lteq_pivot
            # if not L_lt_R, jump to end
                sub r15, r6, r7
                mov r14, L_lt_R_and_memL_lteq_pivot_end
                jns r14, r15 # (if L - R >= 0, jump to end of loop)

            # if not memL_lteq_pivot, jump to end
                ld r8, r6 # mem[L]
                sub r15, r8, r5 # if pivot - mem[L] < 0, jump to end
                mov r14, L_lt_R_and_memL_lteq_pivot_end
                jns r14, r15

            # if neither condition was met, go to the start of the loop
            mov r15, L_lt_R_and_memL_lteq_pivot
            jmp r15

        L_lt_R_and_memL_lteq_pivot_end:

        # right loop, find the rightmost out of place element
        # right ptr for partition in r7
        # while R > L and mem[R] >= pivot, decrement R
            # jump to condition first, we will jump back and run loop contents if it is met
            mov r15, R_gt_L_and_memR_gteq_pivot_condition
            jmp r15

            R_gt_L_and_memR_gteq_pivot:
                mov r15, 0x0002
                sub r7, r7, r15 # decrement R

            R_gt_L_and_memR_gteq_pivot_condition:
                # if condition is met, jump to R_gt_L_and_memR_gteq_pivot
                # if not R_gt_L, jump to end
                    sub r15, r6, r7
                    mov r14, R_gt_L_and_memR_gteq_pivot_end
                    jns r14, r15 # (if L - R >= 0, jump to end of loop)

                # if not memR_gteq_pivot, jump to end
                    ld r8, r7 # mem[R]
                    sub r15, r5, r8 # if mem[R] - pivot , 0
                    mov r14, R_gt_L_and_memR_gteq_pivot_end
                    jns r14, r15

                # if neither condition was met, go to the start of the loop
                mov r15, R_gt_L_and_memR_gteq_pivot
                jmp r15

        R_gt_L_and_memR_gteq_pivot_end:

        # if L < R, swap them
        sub r15, r6, r7 # if L < R, swap
        mov r14, after_swap
        jns r14, r15 # if L - R >= 0, skip swap because we are done

        # do swap here
            # ld mem[L] into r8
            ld r8, r6
            # ld mem[R] into r9
            ld r9, r7

            # st mem[L] into mem[R]
            st r8, r7
            # st mem[R] into mem[L]
            st r9, r6

            mov r15, 0x0002
            sub r7, r7, r15
        after_swap:

        # if L < R, do another iteration
        sub r15, r6, r7
        mov r14, while_ptr_not_converged
        js r14, r15 # if L < R, jump to start of loop

    # qs on [search_L, L-1) and (L, search_R]
        mov r15, 0x0002
        #sub r6, r6, r15 # L - 1
        add r7, r7, r15

        push r2 # push search left
        push r6 # push L0
        push r7 # 
        push r3
    mov r15, quicksort
    jmp r15

finish:

