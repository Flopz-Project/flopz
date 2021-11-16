from typing import Tuple

from flopz.arch.instruction import ArbitraryBytesInstruction
from flopz.core.addressable_object import AddressableObject
from flopz.core.function import Function
from flopz.core.module import Module
from flopz.core.shellcode import Shellcode
from flopz.core.target import Target
from flopz.core.label import Label, LabelRef, AbsoluteLabelRef
from flopz.arch.ppc.vle.instructions import *
from flopz.arch.ppc.vle.auto_instructions import *
from flopz.arch.ppc.vle.e200z0 import E200Z0
from flopz.listener.protocol import Protocol
from flopz.target.bolero.bolero_protocol import BoleroProtocol

class BoleroTarget(Target):
    def get_init_gadgets(self, init_slice_addr: int, original_bytes: bytes,
                         init_gadget_addr: int) -> Tuple[Shellcode, Shellcode]:
        core = E200Z0()

        slice_patch = Shellcode(address=init_slice_addr, instructions=[
            EB(init_gadget_addr - init_slice_addr)
        ])

        def get_jmp_back(x):
            return EB((init_slice_addr + 4) - x)

        instr_init = Shellcode(address=init_gadget_addr, instructions=[
            # first, save r26 so we can use it as a pointer (as in our slice gadget)
            Mtspr(core.SPRG0, core.r26),
            AutoLoadI(core.r26, (self.target_ram + 8)),
            # save r27, r28, r29, r30, r31 to ram
            EStmw(core.r27, core.r26, 0),

            # initialize our BUF_IDX variable
            AutoLoadI(core.r28, 0),
            SeSubi(core.r26, 8),
            SeStw(core.r28, core.r26, 0),
            SeStw(core.r28, core.r26, 4),
            SeAddi(core.r26, 8),

            # restore registers
            ELmw(core.r27, core.r26, 0),
            Mfspr(core.r26, core.SPRG0),

            # run ori instruciton
            ArbitraryBytesInstruction(original_bytes),

            # return
            Label("here"),
            AbsoluteLabelRef("here", get_jmp_back)
        ])


        return slice_patch, instr_init

    def get_slice_gadgets(self, slice_addr: int, original_bytes: bytes, id: int,
                          slice_gadget_addr: int, instrumentation_gadget: AddressableObject) -> Tuple[Shellcode, Shellcode]:
        core = E200Z0()
        slice_patch = Shellcode(address=slice_addr, instructions=[
            EB(slice_gadget_addr - slice_addr)
        ])

        slice_gadget = Shellcode(address=slice_gadget_addr, instructions=[
            # disable interrupts
            Wrteei(0),
            # first, save r24 so we can use it as a target_ram pointer
            Mtspr(core.SPRG0, core.r24),
            # set up our instrumentation stack pointer in r24 + 0x8
            # -> we leave 0x8 bytes reserved for variables
            AutoLoadI(core.r24, (self.target_ram + 8)),
            # save r25, r26, r27, r28, r29, r30, r31 to ram
            # ..for this we use e_stmw which will do that in one instruction
            EStmw(core.r25, core.r24, 0),
            # increment the stack pointer by 28 (7 registers x 4 bytes)
            SeAddi(core.r24, 28),
            # store the old CR register
            Mfcr(core.r27),
            SeStw(core.r27, core.r24,0),
            SeAddi(core.r24, 4),
            # store the old link register, we'll use it
            SeMflr(core.r27),
            SeStw(core.r27, core.r24, 0),
            SeAddi(core.r24, 4), # increment stack pointer

            # store the id in target_ram + 4
            AutoLoadI(core.r26, (self.target_ram + 4)),
            AutoLoadI(core.r27, id),
            SeSth(core.r27, core.r26, 0), # [r26] = r27 = id

            # add the jmp to instr. gadget
            Label("sgEnd"),
            AbsoluteLabelRef("sgEnd", lambda curr_addr: EBl(instrumentation_gadget.get_absolute_address() - curr_addr))
        ])

        # restore all the registers
        slice_gadget.instructions.extend([
            # read the stored link register back into LR
            SeSubi(core.r24, 4), # decrement stack pointer by 4
            SeLwz(core.r27, core.r24, 0), # read the old LR into r27
            SeMtlr(core.r27), # put it back into the LR
            # read the stored CR and restore it
            SeSubi(core.r24, 4),
            SeLwz(core.r27, core.r27, 0),
            Mtcrf(0xff, core.r27),

            # decrement the stack pointer first by 20 (5 registers x 4 bytes)
            SeSubi(core.r24, 28),
            # lead r25, r26, r27, r28, r29, r30, r31 at once
            ELmw(core.r25, core.r24, 0),
            # finally, restore the register containing our stack pointer
            Mfspr(core.r24, core.SPRG0),
            # ..restore interrupts
            Wrteei(1),
        ])

        # add the original bytes/code
        slice_gadget.instructions.append(
            ArbitraryBytesInstruction(bytes=original_bytes)
        )

        # jump back to the patch addr
        slice_gadget.instructions.extend([
            Label("currentPC"),
            AbsoluteLabelRef("currentPC", lambda curr_addr: EB(- (curr_addr - (slice_addr + 4))))
        ])
        return slice_patch, slice_gadget

    def get_instrumentation_gadget(self, config: dict, target_addr: int, dataout_func: Function) -> Shellcode:
        core = E200Z0()
        return Shellcode(address=target_addr, instructions=[
            # ARGS:
            # r27: function ID
            # - prepare arguments for dataout function

            # store old LR, dataout func will restore r31 for us
            SeMflr(core.r31),

            # prepare dataout arguments
            AutoLoadI(core.r28, self.target_ram + 4), # points to function id halfword
            AutoLoadI(core.r29, 2), # send as 2 bytes

            # - call dataout function
            *dataout_func.make_call.get_instructions(),
            # return to slice gadget
            SeMtlr(core.r31),
            SeBlr()
            #SeBl
        ])

    def get_data_out_function(self, target_addr: int) -> Function:
        core = E200Z0()

        def _save_regs_inst_func(args):
            # assume r26 points to our instrumentation stack
            return [
                # store the registers used by DataOutFunc [r25 - r31]
                EStmw(core.r25, core.r24, 0),
                # increment the stack pointer by 28 (7 registers x 4 bytes)
                SeAddi(core.r24, 28),
            ]

        save_regs_mod = Module(instructions_func=_save_regs_inst_func, address=0)

        def _restore_regs_ins_func(args):
            # assume r26 points to our instrumentation stack
            return [
                SeSubi(core.r24, 28), # restore 7 * 4 bytes = 28
                ELmw(core.r25, core.r24, 0),
                # we're done! branch to link register
                SeBlr(),
            ]

        restore_regs_mod = Module(instructions_func=_restore_regs_ins_func, address=0)

        make_call = Module(instructions=[
            # branch and link to logic_mod (which is at target_addr)
            # NOTE: this will overwrite LR - you need to save it yourself if you need it afterwards
            Label("call_source"),
            AbsoluteLabelRef("call_source", lambda cia: EBl(target_addr - cia))
        ], address=0)

        logic_mod = Module(instructions=[
            # ARGS:
            # r28: data ptr
            # r29: data length
            # -> on entry, move arguments to r30, r31 for later
            SeMr(core.r30, core.r28), # r30 = r28
            SeMr(core.r31, core.r29), # r31 = r29

            # always check if the CGM output is enabled
            # if it isn't, bail out
            AutoLoadI(core.r27, 0xc3fe0370),
            SeLwz(core.r28, core.r27, 0),
            SeCmpi(core.r28, 0),
            LabelRef("bail_out", lambda x: EBe(x)),

            # check if CAN is in FREEZE mode / not ready
            AutoLoadI(core.r27, 0xfffc0000),
            SeLbz(core.r28, core.r27, 0),
            EAnd2i(core.r28, 0x8),
            SeCmpi(core.r28, 0),
            LabelRef("bail_out", lambda x: EBne(x)),


            # always clear the FLEXCAN0 IMASK bits for MBs 30-31!
            AutoLoadI(core.r27, 0xfffc0000 + 0x28),
            SeLbz(core.r28, core.r27, 0),
            # zero out bit 0 - bit 3 (including bit 3)
            EAnd2i(core.r28, 0x3f),
            SeStb(core.r28, core.r27, 0),

            Label("top_outer_loop"),

            # select a free Message Buffer by reading the 'next buffer index'
            # for this, we load the static location in ram and read from it
            AutoLoadI(core.r27, (self.target_ram + 0)),
            SeLbz(core.r28, core.r27, 0),
            # if this is out of range (> 3), we need to reset it and wait for the first MB to become free
            SeCmpi(core.r28, 3),
            LabelRef('dstbuf_known', lambda addr: EBlt(addr)),
            # ..reset it to 0:
            SeLi(core.r28, 0),
            SeStb(core.r28, core.r27, 0), # [r27] = r28
            Label("dstbuf_known"),
            # put the msgbuf base in r27
            # -> r27 = (msgbuf_base) + (msgbuf_idx * msgbuf_struct_size)
            AutoLoadI(core.r27, 0xfffc0260), # flexcan0->BUF[30]
            EMull2i(core.r28, 0x10), # r28 = r28 * 16 -> mbuf offset
            SeAdd(core.r27, core.r28), # r27 = r27 + r28
            # now we have our message buffer ptr in r27!
            # -> check CODE register. if it is not 1000 (INACTIVE), then we need to wait
            # -> CODE is at offset 0 of the MB, bits [4:7] (including bit 7)
            Label("check_mb_code"),
            SeLbz(core.r28, core.r27, 0), # r28 = 0x0(r27)
            SeCmpi(core.r28, 8),
            # while r28 > 8: busy wait
            LabelRef("check_mb_code", lambda x: SeBgt(x)),

            # write the ID word, adding the buf idx to it
            AutoLoadI(core.r29, (self.target_ram + 0)),
            SeLbz(core.r29, core.r29, 0), # r29 = [r29]
            AutoLoadI(core.r28, 0x7f0),
            SeAdd(core.r28, core.r29), # r28 += r29
            SeSlwi(core.r28, 2), # r28 = r28 << 2 (shift left by two so it gets written to std id field)

            SeSth(core.r28, core.r27, 0x4), # MB+4 = PRIO | ID_STD | ID_EXT ..

            # loop head:
            # i = 0
            AutoLoadI(core.r28, 0), # i = r28 = 0
            # mbuf_offset = target_ram+1 = r25
            AutoLoadI(core.r25, (self.target_ram + 1)),
            SeLbz(core.r25, core.r25, 0),
            # r27 += mbuf_offset
            SeAdd(core.r27, core.r25),

            Label("inner_fill_frame"),
            SeLbz(core.r29, core.r30, 0), # data = core.r29 = [r30]
            SeStb(core.r29, core.r27, 8), # [r27]+8 = r29
            SeAddi(core.r30, 1), # ptr += 1
            SeAddi(core.r27, 1), # r27 += 1 (mbuf++)
            SeAddi(core.r28, 1), # i += 1

            # check len
            SeSubi(core.r31, 1), # len -= 1
            SeMr(core.r26, core.r28),  # r26 = i (* precalculate r26 = i + mbuf_offset in case we exit here)
            SeAdd(core.r26, core.r25),  # r26 += r25 (mbuf_offset)

            SeCmpi(core.r31, 1), # if len < 1: break
            LabelRef("exit_inner_fill_frame", lambda x: SeBlt(x)),

            # check if mbuf_offset + i < 8 (* use precalculated r26)
            SeCmpi(core.r26, 8), #  loop, if i+mbuf_offset < 8, else: break
            LabelRef("inner_fill_frame", lambda x: SeBlt(x)),
            Label("exit_inner_fill_frame"),

            # restore r27 by subtracting i
            SeSub(core.r27, core.r28),
            # ..and subtracing mbuf_offset
            SeSub(core.r27, core.r25),

            # adjust the mbuf idx, if necessary
            # at this point, r26 still contains old_mbuf_offset+i
            SeCmpi(core.r26, 8),
            LabelRef("skip_mbuf_increment", lambda x: SeBlt(x)),
            # increment mbuf idx:
            AutoLoadI(core.r29, (self.target_ram + 0)), # r29 = [target_ram]
            SeLbz(core.r28, core.r29, 0), # r29 = [r29]
            SeAddi(core.r28, 1), # r28++
            SeStb(core.r28, core.r29, 0), # [r29] = r28
            # zeroize mbuf_offset:
            SeLi(core.r28, 0),
            SeStb(core.r28, core.r29, 1), # [r29+1] = r28 = 0

            # if we are here, this means that the mbuf is full and idx has been incremented
            # ..so finally, we can send the frame!
            # write length, control and code fields of Control and Status words to activate the MB
            # 1 bit don't care
            # srr = 0 (substitute remote req.)
            # ide = 0 (0 -> not an extended ID)
            # RTR = 0 (not a remote transmission req.)
            # length = 8
            AutoLoadI(core.r28, 0x8),  # r28 = 0x8
            SeStb(core.r28, core.r27, 1),  # write to BUF_BASE+1 (setting the above described fields)
            # set status in CODE word to 1100 -> transmit data frame unconditionally once
            AutoLoadI(core.r28, 0xC),  # r28 = 0xC
            SeStb(core.r28, core.r27, 0),  # write to BUF_BASE (setting the CODE byte)
            LabelRef("frame_sent_skip_mbuf_offset_write", lambda x: SeB(x)),
            Label("skip_mbuf_increment"),
            # else branch: i+mbuf_offset < 8
            # this means we have to store the new value: mbuf_offset = old_mbuf + i
            AutoLoadI(core.r25, (self.target_ram + 1)), # r25 =  $mbuf_offset_var
            SeStb(core.r26, core.r25, 0),

            Label("frame_sent_skip_mbuf_offset_write"),
            SeCmpi(core.r31, 0),
            LabelRef("top_outer_loop", lambda x: EBgt(x)), # run until r31 is < 1 (all data is sent)
            Label("bail_out"),
        ], address=0)

        return Function(address=target_addr, save_register_module=save_regs_mod, make_call=make_call,
                        restore_register_module=restore_regs_mod, logic=logic_mod)

    @staticmethod
    def get_protocol() -> Protocol:
        return BoleroProtocol

    @staticmethod
    def name() -> str:
        return 'bolero'