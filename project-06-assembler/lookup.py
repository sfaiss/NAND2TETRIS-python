"""Lookup tables for the assembler."""

mnemonic = {
    "0":   0b101010,
    "1":   0b111111,
    "-1":  0b111010,
    "D":   0b001100,
    "A":   0b110000,
    "!D":  0b001101,
    "!A":  0b110001,
    "-D":  0b001111,
    "-A":  0b110011,
    "D+1": 0b011111,
    "A+1": 0b110111,
    "D-1": 0b001110,
    "A-1": 0b110010,
    "D+A": 0b000010,
    "D-A": 0b010011,
    "A-D": 0b000111,
    "D&A": 0b000000,
    "D|A": 0b010101,
    "M":   0b110000,
    "!M":  0b110001,
    "-M":  0b110011,
    "M+1": 0b110111,
    "M-1": 0b110010,
    "D+M": 0b000010,
    "D-M": 0b010011,
    "M-D": 0b000111,
    "D&M": 0b000000,
    "D|M": 0b010101,
}

jump = {
    "JGT": 0b001,
    "JEQ": 0b010,
    "JGE": 0b011,
    "JLT": 0b100,
    "JNE": 0b101,
    "JLE": 0b110,
    "JMP": 0b111,
}


predefined = {
    "SCREEN": 0x4000,
    "KBD":    0x6000,
    "SP":     0,
    "LCL":    1,
    "ARG":    2,
    "THIS":   3,
    "THAT":   4,
}

# register R0 - R15
for i in range(16):
    predefined[f"R{i}"] = i
