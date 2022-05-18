from enum import IntEnum

"""
IA32 will have multiple Condition Mnemonics that result in the same opcode,
e.g. B and NAe (below and not above or equal). This implementation with standard IntEnums will
result in aliasing that might lead to confusion when debugging. The aenum library could be used to implement
Enums with the same integer representation without aliasing."""


class Cond(IntEnum):
    O = 0
    NO = 1
    B = 2
    C = 2
    NAE = 2
    AE = 3
    NB = 3
    NC = 3
    E = 4
    Z = 4
    NE = 5
    NZ = 5
    BE = 6
    NA = 6
    A = 7
    NBE = 7
    S = 8
    NS = 9
    P = 10
    PE = 10
    NP = 11
    PO = 11
    L = 12
    NGE = 12
    GE = 13
    NL = 13
    LE = 14
    NG = 14
    G = 15
    NLE = 15
    RCXZ = 0x73


