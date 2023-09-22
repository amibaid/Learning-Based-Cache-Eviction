import sys

def get_ra(instr):
    ra = instr[2][1:] # after r
    return int(ra) * 16 * 16

def get_rb(instr):
    rb = instr[3][1:] # after r
    return int(rb) * 16

def get_rt(instr):
    rt = instr[1][1:] # after r
    return int(rt)


def assemble_label(instr):
    # nop, but label attached as string
    return [{"instr": 0b0000000100000001, "label": instr[0:-1]}]

def assemble_sub(instr):
    # 0 rt, ra, rb
    instr = get_ra(instr) + get_rb(instr) + get_rt(instr)
    return [{"instr": instr, "label": None}]

def assemble_add(instr):
    # add rt, ra, rb:
    # sub rt, 0, ra
    # sub rt, rb, rt

    return [{"instr": get_rt(instr) + get_ra(instr) // 16, "label": None},
            {"instr": get_rt(instr) + get_rb(instr) * 16 + get_rt(instr) * 16, "label": None}]
def assemble_div(instr):
    return [{"instr": (1 * 16 * 16 * 16) + get_ra(instr) + get_rt(instr), "label": None}]
def assemble_mul(instr):
    return [{"instr": (1 * 16 * 16 * 16) + get_ra(instr) + (1 * 16) + get_rt(instr), "label": None}]

def assemble_mov(instr):
    # 1000iiiiiiiitttt movl
    # 1001iiiiiiiitttt movh
    # mov into rt, lower and upper, if immediate then move lower and 0 upper, if label move label lower label upper
    label_low = None
    label_high = None
    lower = 0
    upper = 0
    if instr[2][0].isdigit(): # if it starts with a number, it is imm
        lower = int(instr[2], 16) & 0xFF # lower 8 bits
        upper = (int(instr[2], 16) & 0xFF00) >> 8 # upper 8 bits
    else: # its a label
        label_low = (0, instr[2])
        label_high = (1, instr[2])
    
    lower = lower << 4
    upper = upper << 4
    return [{"instr": (0b1000<<12) + get_rt(instr) + lower, "label": label_low},
            {"instr": (0b1001<<12) + get_rt(instr) + upper, "label": label_high}]

def assemble_jmp(instr):
    if instr[0] == "jmp":
        instr = ["jz", instr[1], "r0"]
    jmp_bits = 0 if instr[0] == "jz" else 1 if instr[0] == "jnz" else 2 if instr[0] == "js" else 3
    return [{"instr": (0b1110 << 12) + get_ra(instr) + (jmp_bits << 4) + get_rt(instr), "label": None}]

def assemble_ld(instr):
    return [{"instr": (0b1111 << 12) + get_ra(instr) + get_rt(instr), "label": None}]
def assemble_st(instr):
    return [{"instr": (0b1111 << 12) + get_ra(instr) + (1 << 4) + get_rt(instr), "label": None}]

def assemble_push(instr):
    # mov 2 into r15
    # subtract r15 from r1
    # st rt into addr at r1
    # 1000iiiiiiiitttt movl
    # 1111aaaa0001tttt st
    return [{"instr": 0b1000000000101111, "label": None},
            {"instr": 0b0000000111110001, "label": None},
            {"instr": 0b1111000100010000 + get_rt(instr), "label": None}]

def assemble_pop(instr):
    # ld addr at r1 into rt

    # mov -2 into r15
    # sub r15 from r1

    # 1111aaaa0000tttt  ld rt,ra
    return [{"instr": 0b1111000100000000 + get_rt(instr), "label": None},
            {"instr": 0b1000111111101111, "label": None},
            {"instr": 0b0000000111110001, "label": None}]

instructions = []
assemble_fn_map = {
    "add": assemble_add,
    "sub": assemble_sub,
    "div": assemble_div,
    "mul": assemble_mul,
    "mov": assemble_mov,
    "jmp": assemble_jmp,
    "jz": assemble_jmp,
    "jnz": assemble_jmp,
    "js": assemble_jmp,
    "jns": assemble_jmp,
    "ld": assemble_ld,
    "st": assemble_st,
    "push": assemble_push,
    "pop": assemble_pop
}

for line in sys.stdin:
    line = line.strip()
    line = line.split("#")
    comment = line[1].strip() if (len(line) > 1) else None
    line = line[0].strip()

    if not comment and (not line or line == ""):
        continue
    # it is either an identifier or an instr
    if line == "":
        # just comment
        # fill nop and continue
        instructions += [{"instr": 0b0000000100000001,
                        "comment": comment,
                        "label": None}]
        continue
    
    to_append = None
    if line[-1] == ":":
        # identifier
        # assemble it as a nop and attach a flag
        to_append = assemble_label(line)
    else:
        # instr
        line = line.split(",")
        line = line[0].split(" ") + line[1:]
        line = [x.strip() for x in line]
        # line[0] is instr type
        # line 1, 2, 3 args
        to_append = assemble_fn_map[line[0]](line)
    to_append[0]["comment"] = comment
    for i in range(1,len(to_append)):
        to_append[i]["comment"] = None
    instructions += to_append

label_locations = {}
# do a pass to determine the address of each label
for i, instruction in enumerate(instructions):
    if isinstance(instruction["label"], str):
        # it is a label, mark its value
        label_locations[instruction["label"]] = i * 2 # store the byte addr
        instruction["label"] = None

for instruction in instructions:
    if instruction["label"] is not None:
        # 0 is lower 8, 1 is upper 8
        needed_bits = instruction["label"][0]
        label_val = label_locations[instruction["label"][1]]
        # label_val masked with
        if needed_bits == 0:
            label_val = label_val & 0xFF
        elif needed_bits == 1:
            label_val = (label_val >> 8) & 0xFF
        # zero out the immediate
        instruction["instr"] = (instruction["instr"] & (0xF00F))
        # replace the immediate
        instruction["instr"] = (instruction["instr"] | (label_val << 4))

for instruction in instructions:
    print(("%.4X" % instruction["instr"]).lower() + ((" // %s" % instruction["comment"]) if instruction["comment"] else ""))
print("ffff")