from typing import List
from flopz.arch.register import Register
from flopz.arch.auto_instruction import AutoInstruction
from flopz.arch.arm.thumb.instructions import *
from enum import Enum


class AutoInstructionFailure(Exception):
    def __init__(self, msg):
        super().__init__(msg)


class AutoStore(AutoInstruction):
    def __init__(self, *args, **kwargs):
        super().__init__()

        # use arg types to match fitting instruction
        self.argtypes = [type(a) for a in args[:3]]
        self.kwords = kwargs.keys()

        self.args = args
        self.kwargs = kwargs

    def expand(self) -> List[ThumbInstruction]:
        # check if we want to store halfwords or bytes
        byte = False
        hword = False
        if "byte" in self.kwords:
            byte = self.kwargs["byte"]
        if "hword" in self.kwords:
            hword = self.kwargs["hword"]

        if self.argtypes == [Register, Register, Register]:
            # its a register store instruction, allowed kwargs are: shift, byte, hword
            if "shift" in self.kwords:
                return [StrWR(*(a.get_val for a in self.args[:3]), shift=self.kwargs["shift"], byte=byte, hword=hword)]
            else:
                return [StrWR(*(a.get_val for a in self.args[3:]), shift=0, byte=byte, hword=hword)]
        elif self.argtypes == [Register, Register, int]:
            # its a immediate store instruction, allowed kwargs are: index, wback, byte, hword
            registers = self.args[:2]
            offset = self.args[2]

            # decide on 16Bit encoding or 32 Bit encoding with either 8Bit or 12Bit immediate

            # check for special indexing
            indexing = "offset"
            if "index" in self.kwords:
                if not self.kwargs["index"]:
                    if "wback" not in self.kwords or not self.kwargs["wback"]:
                        raise AutoInstructionFailure("Invalid indexing (index == False && wback == False")
                    else:
                        indexing = "post-index"
            if "index" not in self.kwords or self.kwargs["index"]:
                if "wback" in self.kwords and self.kwargs["wback"]:
                    indexing = "pre-index"

            # we have to use 32Bit T4 encoding for negative offsets or writeback
            if indexing != "offset" or offset < 0:
                if indexing == "offset":
                    return [StrW(registers[0].get_val, registers[1].get_val, offset=offset, byte=byte, hword=hword)]
                elif indexing == "pre-index":
                    return [StrW(registers[0].get_val, registers[1].get_val, offset=offset, index=True, wback=False, byte=byte, hword=hword)]
                elif indexing == "post-index":
                    return [StrW(registers[0].get_val, registers[1].get_val, offset=offset, index=False, wback=True, byte=byte, hword=hword)]

            # check offset and register range to decide between 16 or 32Bit encoding
            try:
                # try to use 16Bit encoding
                if byte:
                    return [Strb(*(r.get_val for r in registers), offset=offset)]
                elif hword:
                    return [Strh(*(r.get_val for r in registers), offset=offset)]
                else:
                    return [Str(*(r.get_val for r in registers), offset=offset)]
            except ValueError:
                # use 32Bit encoding
                return [StrWI12(*(r.get_val for r in registers), offset=offset, byte=byte, hword=hword)]
        else:
            AutoInstructionFailure("Invalid argument types for {type(self)} AutoInstruction")


class AutoLoad(AutoInstruction):
    def __init__(self, *args, **kwargs):
        super().__init__()

        # use arg types to match fitting instruction
        self.argtypes = [type(a) for a in args[:3]]
        self.kwords = kwargs.keys()

        self.args = args
        self.kwargs = kwargs

    def expand(self) -> List[ThumbInstruction]:
        # check if we want to load halfwords or bytes
        byte = False
        hword = False
        if "byte" in self.kwords:
            byte = self.kwargs["byte"]
        if "hword" in self.kwords:
            hword = self.kwargs["hword"]

        if self.argtypes == [Register, Register, Register]:
            # its a register store instruction, allowed kwargs are: shift, byte, hword
            if "shift" in self.kwords:
                return [LdrWR(*(a.get_val for a in self.args[:3]), shift=self.kwargs["shift"], byte=byte, hword=hword)]
            else:
                return [LdrWR(*(a.get_val for a in self.args[3:]), shift=0, byte=byte, hword=hword)]

        elif self.argtypes == [Register, Register, int]:
            # its a immediate store instruction, allowed kwargs are: index, wback, byte, hword
            registers = self.args[:2]
            offset = self.args[2]

            # decide on 16Bit encoding or 32 Bit encoding with either 8Bit or 12Bit immediate

            # check for special indexing
            indexing = "offset"
            if "index" in self.kwords:
                if not self.kwargs["index"]:
                    if "wback" not in self.kwords or not self.kwargs["wback"]:
                        raise Exception("Invalid indexing (index == False && wback == False")
                    else:
                        indexing = "post-index"
            if "index" not in self.kwords or self.kwargs["index"]:
                if "wback" in self.kwords and self.kwargs["wback"]:
                    indexing = "pre-index"

            # we have to use 32Bit T4 encoding for negative offsets or writeback
            if indexing != "offset" or offset < 0:
                if indexing == "offset":
                    return [LdrW(registers[0].get_val, registers[1].get_val, offset=offset, byte=byte, hword=hword)]
                elif indexing == "pre-index":
                    return [LdrW(registers[0].get_val, registers[1].get_val, offset=offset, index=True, wback=False,
                                 byte=byte, hword=hword)]
                elif indexing == "post-index":
                    return [LdrW(registers[0].get_val, registers[1].get_val, offset=offset, index=False, wback=True,
                                 byte=byte, hword=hword)]

            # check offset and register range to decide between 16 or 32Bit encoding
            try:
                # try to use 16Bit encoding
                if byte:
                    return [Ldrb(*(r.get_val for r in registers), offset=offset)]
                elif hword:
                    return [Ldrh(*(r.get_val for r in registers), offset=offset)]
                else:
                    return [Ldr(*(r.get_val for r in registers), offset=offset)]

            except ValueError:
                # use 32Bit encoding
                return [LdrWI12(*(r.get_val for r in registers), offset=offset, byte=byte, hword=hword)]
        elif self.argtypes == [Register, int]:
            # load literalinstruction
            return [LdrWLit(self.args[0].get_val, self.args[1])]
        else:
            AutoInstructionFailure("Invalid argument types for {type(self)} AutoInstruction")


class AutoBranch(AutoInstruction):
    def __init__(self, *args):
        super().__init__()

        self.cond = None
        self.offset = None

        if not any(type(a) == int for a in args):
            raise AutoInstructionFailure("AutoBranch instruction needs an int offset")
        if len(args) == 1:
            # arg has to be the desired offset
            self.offset = args[0]
        elif len(args) == 2:
            # find condition and offset
            if not any(isinstance(a, Enum) for a in args):
                raise AutoInstructionFailure("AutoBranch instruction with 2 arguments expects a condition argument")
            if isinstance(args[0], Enum):
                self.cond = args[0]
                self.offset = args[1]
            else:
                self.cond = args[1]
                self.offset = args[0]
        else:
            raise AutoInstructionFailure(f"Invalid amount of arguments {len(args)} for AutoBranch (expects 2)")

    def expand(self) -> List[ThumbInstruction]:

        if self.cond is None:
            # unconditional branch
            try:
                return [B_T2(self.offset)]
            except ValueError:
                return [B_T4(self.offset)]
        else:
            # conditional branch
            try:
                return [B_T1(self.cond, self.offset)]
            except ValueError:
                return [B_T3(self.cond, self.offset)]

# TODO encode jumps bigger than allowed for cond as IT and uncond
