import struct
from typing import Tuple

import pytest

from flopz.arch.instruction import ArbitraryBytesInstruction
from flopz.core.addressable_object import AddressableObject
from flopz.core.function import Function
from flopz.core.module import Module
from flopz.core.shellcode import Shellcode
from flopz.core.target import Target
from scripts.flopz_instrument import instrument_by_config, _get_key_for_trace_dump_config

@pytest.fixture
def valid_config():
    return {
        'project': 'test project',
        'binary': 'test binary',
        'schema_version': 1.0,

        'target_flash': {
            'start_addr': '0x100',
            'size': '0x100'
        },
        "target_ram": {
            "start_addr": "0x1234",
            "size": 200
        },
        'init_patch_location': {
            'addr': '0x0',
            'original_bytes': 'aa bb cc dd',
            'original_mnemonics': 'bla bla, 0'
        },
        'gadgets': [
            # it should support simple traces
            {
                "trace": {
                    "id": 123,
                    "level": "function",
                     "dump": [
                         {"type": 'id'},  # this is the default
                    ]
                },
                "patch": {
                    "addr": "0x20",
                    "original_mnemonics": "mov 1, 2",
                    "original_bytes": "bb aa dd cc"
                }
            },
            {
                "trace": {
                    "id": 321,
                    "level": "function",
                    "dump": [
                        { "type": 'id' }, # this is the default
                        {
                            "type": "register",
                            "register_name": "r1"
                        },
                        {
                            "type": "data",
                            "data_addr": "0x12345",
                            "data_len": 16
                        }
                    ]
                },
                "patch": {
                    "addr": "0x30",
                    "original_mnemonics": "mov 1, 2",
                    "original_bytes": "cc aa dd bb"
                }
            },
            # it should support basic patching
            {
                "patch": {
                    "addr": "0x40",
                    "value": "44 33 22 11"
                }
            }

        ]
    }

@pytest.fixture
def valid_target():
    class TestTarget(Target):
        def get_init_gadgets(self, init_slice_addr: int, original_bytes: bytes,
                        init_gadget_addr: int) -> Tuple[Shellcode, Shellcode]:
            slice_patch = Shellcode(address=init_slice_addr, instructions=[
                ArbitraryBytesInstruction(bytes=b'\x99\x88\x77\x66')
            ])
            instr_init = Shellcode(address=init_gadget_addr, instructions=[
                ArbitraryBytesInstruction(bytes=b'\x66\x77\x88\x99')
            ])
            return slice_patch, instr_init

        def get_slice_gadgets(self, slice_addr: int, original_bytes: bytes, id: int,
                          slice_gadget_addr: int, instrumentation_gadget: AddressableObject) -> Tuple[Shellcode, Shellcode]:
            slice_patch = Shellcode(address=slice_addr, instructions=[
                ArbitraryBytesInstruction(b'\x22\x11\x44\x33')
            ])
            slice_gadget = Shellcode(address=slice_gadget_addr, instructions=[
                ArbitraryBytesInstruction(b'\x44\x11\x22\x33'),
                ArbitraryBytesInstruction(original_bytes)
            ])
            return slice_patch, slice_gadget

        def get_instrumentation_gadget(self, config: dict, target_addr: int, dataout_func: Function) -> Shellcode:
            return Shellcode(address=target_addr, instructions=[
                ArbitraryBytesInstruction(b'\x00\x11\x00\x22')
            ])

        def get_data_out_function(self, target_addr: int) -> Function:
            return Function(address=target_addr, save_register_module=Module(0, instructions=[]),
                            restore_register_module=Module(0, instructions=[]),
                            logic=Module(0, instructions=[ArbitraryBytesInstruction(b'\x33\x22\x11\x00')])
                            )

        @staticmethod
        def name() -> str:
            return 'test_target'

    return TestTarget

@pytest.fixture
def zero_bytearray():
    return bytearray(b'\x00' * 0x1000)

def test_key_for_trace_dump_config(valid_config):
    key = _get_key_for_trace_dump_config(valid_config['gadgets'][0]['trace']['dump'])
    assert(key == 'type_id_')

    key = _get_key_for_trace_dump_config(valid_config['gadgets'][1]['trace']['dump'])
    assert(key == 'type_id_type_registerregister_name_r1_type_datadata_addr_0x12345data_len_16_')

def test_instrument_by_config(valid_config, valid_target, zero_bytearray):
    new_binary_data = instrument_by_config(valid_config, valid_target, zero_bytearray)
    assert(new_binary_data[0x00:0x04] == b'\x99\x88\x77\x66')

    # it should place the init function once, at the beginning of target_flash
    assert(new_binary_data[0x100:0x104] == b'\x66\x77\x88\x99')

    # it should apply the patch for calling the init function
    assert(new_binary_data[0x0:0x4] == b'\x99\x88\x77\x66')

    # it should place the data out function
    assert(new_binary_data[0x104:0x108] == b'\x33\x22\x11\x00')

    # it should place and patch the first slice gadget, slice_patch
    assert(new_binary_data[0x20:0x24] == b'\x22\x11\x44\x33') # check patch
    assert(new_binary_data[0x10c:0x110] == b'\x44\x11\x22\x33') # check slice gadget, after instr. gadget
    assert(new_binary_data[0x110:0x114] == b'\xbb\xaa\xdd\xcc') # original instructions

    # it should place the remaining slice gadgets, slice patches
    assert(new_binary_data[0x30:0x34] == b'\x22\x11\x44\x33')
    assert(new_binary_data[0x118:0x11c] == b'\x44\x11\x22\x33') # check slice gadget, after instr. gadget
    assert(new_binary_data[0x11c:0x120] == b'\xcc\xaa\xdd\xbb')

    # it should generate an instrumentation gadget for each unique dump configuration
    assert(new_binary_data[0x108:0x10c] == b'\x00\x11\x00\x22') # config 1
    assert(new_binary_data[0x114:0x118] == b'\x00\x11\x00\x22') # config 2

    # it should apply the patch
    assert(new_binary_data[0x40:0x44] == b'\x44\x33\x22\x11')

