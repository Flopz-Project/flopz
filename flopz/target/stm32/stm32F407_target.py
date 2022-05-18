from typing import Tuple

from flopz.arch.instruction import ArbitraryBytesInstruction
from flopz.core.addressable_object import AddressableObject
from flopz.core.function import Function
from flopz.core.module import Module
from flopz.core.shellcode import Shellcode
from flopz.core.target import Target
from flopz.listener.protocol import Protocol
from flopz.core.label import Label, LabelRef, AbsoluteLabelRef

from flopz.arch.arm.thumb.stm32F407 import Stm32F407
from flopz.arch.arm.thumb.auto_instructions import *
from flopz.arch.arm.thumb.instructions import *


class Stm32F407Target(Target):
    def get_init_gadgets(self, init_slice_addr: int, original_bytes: bytes,
                         init_gadget_addr: int) -> Tuple[Shellcode, Shellcode]:
        core = Stm32F407()

        slice_patch = Shellcode(address=init_slice_addr, instructions=[
            B_T4(init_gadget_addr - init_slice_addr)
        ])

        def get_jmp_back(x):
            return B_T4((init_slice_addr + 4) - x)

        uart2_base = 0x40004400
        gpioa_base = 0x40020000

        set_mode = 0b10100000
        set_speed = 0b11110000
        set_af = 0x7700

        set_tx_rx = 0x0C
        set_ue = 0x2000

        set_brr = (17 << 4) + 6

        instr_init = Shellcode(address=init_gadget_addr, instructions=[
            # save used registers on stack
            PUSH([core.r4, core.r5]),

            # set GPIOA for PA2 & PA3 to use AF7
            AndI(core.r4, core.r4, 0x0),
            AddI_T3(core.r4, core.r4, 0x40000000),
            AddI_T3(core.r4, core.r4, 0x00020000),  # save 0x40020000 GPIOA base address in r4

            # set MODER register to AF for PA2 & PA3
            AndI(core.r5, core.r5, 0x0),
            Ldrb(core.r5, core.r4, 0),
            AddI_T2(core.r5, set_mode),
            Strb(core.r5, core.r4, 0),

            # set speed register for PA2 & PA3
            Ldrb(core.r5, core.r4, 0x08),
            AddI_T2(core.r5, set_speed),
            Strb(core.r5, core.r4, 0x08),

            # set alternate function register to use AF7 for PA2 & PA3
            Ldrh(core.r5, core.r4, 0x20),
            AddI_T3(core.r5, core.r5, set_af),
            Strh(core.r5, core.r4, 0x20),


            # Set USART2 params
            AndI(core.r4, core.r4, 0x0),
            AddI_T3(core.r4, core.r4, 0x40000000),
            AddI_T3(core.r4, core.r4, 0x4400),  # save UART2 base address in r4

            # stop bits in CR2 should be set to 1 stop bit per default
            # HwFlwCtl in CR3 should be disabled by default

            # WordLength, Parity, OverSampling can stay default in CR1
            # set TE and RE bit in CR1, also set UE bit
            AndI(core.r5, core.r5, 0x0),
            AddI_T2(core.r5, set_tx_rx),
            AddI_T3(core.r5, core.r5, set_ue),
            Strh(core.r5, core.r4, 0x0C),

            # set BRR (baud rate register)

            # target baud rate 115200 with 32MHz clock needs USARTDIV of 17,36
            # next possible val is 17,375
            # encode mantissa as 17, frac as 6
            AndI(core.r5, core.r5, 0x0),
            AddI_T3(core.r5, core.r5, set_brr),
            Strh(core.r5, core.r4, 0x08),


            # test sending something (write to data register of UART2)
            AndI(core.r5, core.r5, 0x0),
            AddI_T2(core.r5, 0x41),
            Strh(core.r5, core.r4, 0x04),


            # restore register state
            POP([core.r4, core.r5]),
            # run ori instruciton
            ArbitraryBytesInstruction(original_bytes),

            # return
            Label("here"),
            AbsoluteLabelRef("here", get_jmp_back)
        ])

        return slice_patch, instr_init

    def get_slice_gadgets(self, slice_addr: int, original_bytes: bytes, id: int,
                          slice_gadget_addr: int, instrumentation_gadget: AddressableObject) -> Tuple[Shellcode, Shellcode]:
        slice_patch = Shellcode()
        slice_gadget = Shellcode()
        return slice_patch, slice_gadget

    def get_instrumentation_gadget(self, config: dict, target_addr: int, dataout_func: Function) -> Shellcode:
        return Shellcode()

    def get_data_out_function(self, target_addr: int) -> Function:
        mod = Module(0)
        return Function(0, save_register_module=mod, restore_register_module=mod, logic=mod)

    @staticmethod
    def get_protocol() -> Protocol:
        return None

    @staticmethod
    def name() -> str:
        return 'stm32F407'