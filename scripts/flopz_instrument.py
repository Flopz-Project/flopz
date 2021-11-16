import argparse
import json
import logging
from typing import Tuple

from flopz.core.shellcode import Shellcode
from flopz.core.target import Target
from flopz.target.all_targets import get_target_by_name
from flopz.util.parsing import get_int_from_str, get_bytes_from_hex_str


def get_arg_parser():
    parser = argparse.ArgumentParser(description='Process cmd options')
    parser.add_argument('-t', metavar='target', type=str, help='name of the target', required=True)
    parser.add_argument('-i', metavar='input', type=str, help='the original binary file you want to patch', required=True)
    parser.add_argument('-c', metavar='config', type=str, help='the json config file generated using the ghidra plugin', required=True)
    parser.add_argument('-o', metavar='output', type=str, help='output filename for patched binary', required=True)
    return parser


def get_inputs(parser) -> tuple:
    args = parser.parse_args()

    input_filename = args.i
    output_filename = args.o
    config_filename = args.c
    target_name = args.t

    target_cls = get_target_by_name(target_name)

    if target_cls is None:
        logging.error("Target not found! Please provide a valid target name.")
        return

    with open(config_filename, 'r') as f:
        config = json.load(f)

    with open(input_filename, 'rb') as f:
        input_binary = f.read()

    if input_binary is None or len(input_binary) < 1:
        logging.error("Error: input binary is empty or does not exist!")
        return
    else:
        # this is needed so we can modify the binary like an array
        input_binary = bytearray(input_binary)

    return config, target_cls, input_binary, output_filename

def _apply_patch(sc: Shellcode, binary: bytearray) -> Tuple[bytearray, int]:
    # works in-place
    sc_bytes = sc.bytes()
    binary[sc.get_absolute_address():sc.get_absolute_address()+len(sc_bytes)] = sc_bytes
    return binary, len(sc_bytes)

def _get_key_for_trace_dump_config(config: list) -> str:
    # maybe a bit hacky, but the order in which the dump entries appear makes a difference
    # for us, this should be good enough to disambiguate two different instrumentation gadgets
    ret = ''
    for dump_type in config:
        for key, value in dump_type.items():
            ret += key.strip() + '_' + (value.strip() if type(value) == str else str(value))
        ret += '_'
    return ret

def instrument_by_config(config: dict, target_cls: object, input_binary: bytearray) -> bytes:
    output_binary = input_binary
    # start parsing project metadata
    project_name = config['project']
    binary_name = config['binary']

    target_flash_addr = get_int_from_str(config['target_flash']['start_addr'])
    target_flash_len = get_int_from_str(config['target_flash']['size'])
    _tr = config['target_ram']
    target_ram = get_int_from_str(config['target_ram']['start_addr'])
    target_ram_len = get_int_from_str(config['target_ram']['size'])
    target = target_cls(target_ram, target_ram_len)

    # use a counter to keep track of target flash size
    target_flash_ctr = 0

    init_patch = config['init_patch_location']
    slice_patch, init_code = target.get_init_gadgets(init_slice_addr=get_int_from_str(init_patch['addr']),
                                                     original_bytes=get_bytes_from_hex_str(init_patch['original_bytes']),
                                                     init_gadget_addr=target_flash_addr + target_flash_ctr)
    output_binary, _ = _apply_patch(slice_patch, output_binary)
    output_binary, patch_len = _apply_patch(init_code, output_binary)
    target_flash_ctr += patch_len

    # get data out function
    dataout = target.get_data_out_function(target_flash_addr + target_flash_ctr)
    output_binary, patch_len = _apply_patch(dataout, output_binary)
    target_flash_ctr += patch_len

    # map different configs to instrumentation gadgets
    dump_config_to_instr_gadget = {}

    # start iterating over slices and patches
    for gadget in config['gadgets']:
        # a gadget has either a 'trace' and a 'patch' part or only a 'patch' part
        if 'trace' in gadget.keys() and 'patch' in gadget.keys():
            trace = gadget['trace']
            # check instrumentation gadget first
            instr_gadget = dump_config_to_instr_gadget.get(_get_key_for_trace_dump_config(trace['dump']), None)
            if not instr_gadget:
                # we need to generate it
                instr_gadget = target.get_instrumentation_gadget(trace['dump'], target_flash_addr + target_flash_ctr,
                                                                 dataout)
                output_binary, patch_len = _apply_patch(instr_gadget, output_binary)
                target_flash_ctr += patch_len
                dump_config_to_instr_gadget[_get_key_for_trace_dump_config(trace['dump'])] = instr_gadget
            # get slice gadgets & patch the output binary
            instr_id = trace['id']
            trace_patch = gadget['patch']
            target_addr = get_int_from_str(trace_patch['addr'])
            ori_bytes = get_bytes_from_hex_str(trace_patch['original_bytes'])
            slice_patch, slice_gadget = target.get_slice_gadgets(slice_addr=target_addr, original_bytes=ori_bytes,
                                                                 slice_gadget_addr=target_flash_addr+target_flash_ctr,
                                                                 instrumentation_gadget=instr_gadget, id=instr_id)
            output_binary, _ = _apply_patch(slice_patch, output_binary)
            output_binary, patch_len = _apply_patch(slice_gadget, output_binary)
            target_flash_ctr += patch_len

            # check target flash len
            if target_flash_ctr > target_flash_len:
                raise Exception('Error: Exceeded target flash length!')
        elif 'patch' in gadget.keys():
            patch = gadget['patch']
            patch_bytes = get_bytes_from_hex_str(patch['value'])
            patch_addr = get_int_from_str(patch['addr'])
            output_binary[patch_addr:patch_addr + len(patch_bytes)] = patch_bytes
        else:
            raise Exception('invalid gadget: ' + gadget)

    return output_binary

def main():
    config, target_cls, input_binary, output_filename = get_inputs(get_arg_parser())
    output_data = instrument_by_config(config, target_cls, input_binary)
    # write to output file
    logging.info(f"Writing {hex(len(output_data))} bytes to {output_filename}!")
    with open(output_filename, 'wb') as f:
        f.write(output_data)
    logging.info("Done!")


if __name__ == '__main__':
    main()