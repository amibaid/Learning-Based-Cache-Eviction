import sys
import cache

# load initial data into pseudo memory
MEM_SIZE = 32768
CODE_SIZE = 500
DEBUG = False
my_mem = [0 for i in range(MEM_SIZE)]
curr_index = 0
num_instrs = 0
comment = False
for line in sys.stdin.readlines():
    line = line.split("//")[0].strip()
    if line.isspace() or line == "":
        continue
    if line[0] == "@" and not comment:
        # set current index
        curr_index = int(line[1:], 16)
        continue
    if "/*" in line:
        comment = True
    if "*/" in line:
        comment = False
        continue
    # otherwise plant the memory at the appropriate index and continue
    if not comment:
        my_mem[curr_index] = int(line, 16)
        num_instrs += 1
        curr_index += 1

# cache
mem_cache = cache.Cache();   

# set pc to 0
pc = 0
# set regs to 0
regs = [0 for i in range(16)]

def is_valid(instr):
    return any([f(instr) for f in [is_sub, is_mov, is_jump, is_ld, is_st, is_div, is_mul]])

def get_bit(num, i):
    return ((num >> i) & 1)

# 0001aaaa0000tttt  div rt, ra    regs[t] = regs[a] / 2
def is_div(instr):
    return all([get_bit(instr, i) == 0 for i in range(13, 16)]) and (get_bit(instr, 12) == 1) and all([get_bit(instr, i) == 0 for i in range(4, 8)])

# 0001aaaa0001tttt  mul rt, ra    regs[t] = regs[a] * 2
def is_mul(instr):
    return all([get_bit(instr, i) == 0 for i in range(13, 16)]) and (get_bit(instr, 12) == 1) and all([get_bit(instr, i) == 0 for i in range(5, 8)]) and get_bit(instr, 4) == 1

# 0000aaaabbbbtttt  sub rt,ra,rb  regs[t] = regs[a] - regs[b]
def is_sub(instr):
    return all([get_bit(instr, i) == 0 for i in range(12, 16)])

# 1000iiiiiiiitttt  movl rt,i     regs[t] = sign_extend(i)
# 1001iiiiiiiitttt  movh rt,i     regs[t] = (regs[t] & 0xff) | (i << 8)
def is_mov(instr):
    return get_bit(instr, 15) == 1 and get_bit(instr, 14) == 0 and get_bit(instr, 13) == 0

# 1110aaaa0000tttt  jz rt,ra      pc = (regs[ra] == 0) ? regs[rt] : pc + 2
# 1110aaaa0001tttt  jnz rt,ra     pc = (regs[ra] != 0) ? regs[rt] : pc + 2
# 1110aaaa0010tttt  js rt,ra      pc = (regs[ra] < 0) ? regs[rt] : pc + 2
# 1110aaaa0011tttt  jns rt,ra     pc = (regs[ra] >= 0) ? regs[rt] : pc + 2
def is_jump(instr):
    return (tuple(get_bit(instr, i) for i in range(12, 16)) == (0, 1, 1, 1)) and get_bit(instr, 6) == 0 and get_bit(instr, 7) == 0

# 1111aaaa0000tttt  ld rt,ra      regs[t] = mem[regs[a]]
def is_ld(instr):
    return all([get_bit(instr, i) == 1 for i in range(12, 16)]) and all([get_bit(instr, i) == 0 for i in range(4, 8)])

# 1111aaaa0001tttt  st rt,ra      mem[regs[a]] = regs[t]
def is_st(instr):
    return all([get_bit(instr, i) == 1 for i in range(12, 16)]) and all([get_bit(instr, i) == 0 for i in range(5, 8)]) and get_bit(instr, 4) == 1

# ra is bits [8,11]
def get_ra(instr):
    return (instr >> 8) & 0b1111

# rb is bits [8,11]
def get_rb(instr):
    return (instr >> 4) & 0b1111

# rt is bits [8,11]
def get_rt(instr):
    return instr & 0b1111

# imm is bits [4,11]
def get_imm(instr):
    return (instr >> 4) & 0b11111111

def get_reg(reg):
    if reg == 0:
        return 0
    return regs[reg]

def set_reg(reg, val):
    if reg == 0:
        print(chr(val & 0b11111111), end='')
    else:   
        regs[reg] = (val & 0xFFFF) # get last 16 bits


def do_sub(instr):
    if DEBUG:
        print("sub", get_rt(instr), get_ra(instr), get_rb(instr))
    va = get_reg(get_ra(instr))
    vb = get_reg(get_rb(instr))
    result = va - vb 
    set_reg(get_rt(instr), result)

def do_mov(instr):
    if get_bit(instr, 12) == 0:
        # movl, we sign extend imm and replace full value
        if DEBUG:
            print("movl", get_rt(instr), get_imm(instr))
        result = (sum([(1 << i) * get_bit(instr, 11) for i in range(8)]) << 8) + get_imm(instr)
    else:
        if DEBUG:
            print("movh", get_rt(instr), get_imm(instr))
        # movh, we use high 8 bits from imm and low 8 bits from rt
        rt_old = get_reg(get_rt(instr)) & 0xFF
        result = (get_imm(instr) << 8) + rt_old
    set_reg(get_rt(instr), result)

def do_mul(instr):
    if DEBUG:
        print("mul", get_rt(instr), get_ra(instr))
    result = (get_reg(get_ra(instr)) << 1)
    set_reg(get_rt(instr), result)

def do_div(instr):
    if DEBUG:
        print("div", get_rt(instr), get_ra(instr))
    result = (get_reg(get_ra(instr)) >> 1)
    set_reg(get_rt(instr), result)


def do_jump(instr):
    if DEBUG:
        jump_bits = (get_bit(instr, 5), get_bit(instr, 4))
        print("j%s" % ("z" if jump_bits == (0, 0) else "nz" if jump_bits == (0, 1) else "s" if jump_bits == (1, 0) else "ns"), get_rt(instr), get_ra(instr))
    global pc
    va = get_reg(get_ra(instr))
    va_signbit = get_bit(va, 15)
    vt = get_reg(get_rt(instr))

    jump_bits = (get_bit(instr, 5), get_bit(instr, 4))
    jump_condition = (jump_bits == (0, 0) and va == 0) or (jump_bits == (0, 1) and va != 0) or (jump_bits == (1, 0) and va_signbit == 1) or (jump_bits == (1, 1) and va_signbit == 0)
    if jump_condition:
        pc = vt - 2


def do_ld(instr):
    if DEBUG:
        print("ld", get_rt(instr), get_ra(instr))
        print("st", get_rt(instr), get_ra(instr), my_mem[get_reg(get_ra(instr))//2], "from addr", get_reg(get_ra(instr)))
        if (get_reg(get_ra(instr)) // 2) <= CODE_SIZE:
            print("WARNING: LOADING FROM CODE SPACE")
    va = get_reg(get_ra(instr))
    
    #cache
    mem_addr = va // 2
    mem_cache.cache_lookup(mem_addr, my_mem)

    set_reg(get_rt(instr), my_mem[va // 2])

def do_st(instr):
    if DEBUG:
        print("st", get_rt(instr), get_ra(instr), get_reg(get_rt(instr)), "into addr", get_reg(get_ra(instr)))
        if (get_reg(get_ra(instr)) // 2) <= CODE_SIZE:
            print("WARNING: WRITING TO CODE SPACE")
    vt = get_reg(get_rt(instr))
    va = get_reg(get_ra(instr))
    my_mem[va // 2] = vt

    #cache
    mem_addr = va // 2
    mem_cache.update_cache(mem_addr, my_mem)

def do_instruction(instr):
    if is_sub(instr):
        do_sub(instr)
    elif is_mov(instr):
        do_mov(instr)
    elif is_div(instr):
        do_div(instr)
    elif is_mul(instr):
        do_mul(instr)
    elif is_jump(instr):
        do_jump(instr)
    elif is_ld(instr):
        do_ld(instr)
    elif is_st(instr):
        do_st(instr)
    else:
        raise ValueError("weird instruction")

# interpret instructions and update regs, pc, pseudo-memory
num_cycles = 0
while num_cycles < 5000000:
    # print(pc)
    next_instr = my_mem[pc // 2]
    # print("%d: %.4X" % (pc//2 + 1, next_instr))
    if not is_valid(next_instr):
        # print(hex(next_instr), "invalid at", pc)
        break

    do_instruction(next_instr)
    pc += 2
    num_cycles += 1

#output: cycles, FIFO hit rate, RRPV hit rate
print("Number of cycles: " + str(num_cycles))
cache_hits = mem_cache.cache_accuracy()
print("FIFO cache hit ratio:" + str(cache_hits[0]))
print("RRPV cache hit ratio:" + str(cache_hits[1]))
