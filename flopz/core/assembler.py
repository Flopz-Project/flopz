from flopz.arch.auto_instruction import AutoInstruction
from flopz.arch.instruction import Instruction
from flopz.core.label import Label, LabelRef


class AssemblerException(Exception):
    pass


class Assembler:
    """
    An Assembler is used to turn one piece of Shellcode (or a Module/Function) into assembly bytes
    It may be used without instantiating it explicitly (as done by the Shellcode class in .bytes())
    """
    def __init__(self):
        pass

    def bytes(self, shellcode) -> bytes:
        """
        :returns: binary code for assigned shellcode
        """
        # expand auto instructions and build a list of labels
        processed_instructions = []
        name2label = {}

        for ins in shellcode:
            if isinstance(ins, AutoInstruction):
                processed_instructions.extend(ins.expand())
            else:
                processed_instructions.append(ins)

        # assign addresses
        current_addr = shellcode.get_absolute_address()
        ins2addr = {}
        for ins in processed_instructions:
            if isinstance(ins, Instruction):
                ins2addr[ins] = current_addr
                current_addr += ins.size_bytes()
            elif isinstance(ins, Label):
                ins.finalize(current_addr)
                if ins.name in name2label.keys():
                    raise AssemblerException(f"Duplicate label: {ins}")
                else:
                    name2label[ins.name] = ins
            elif isinstance(ins, LabelRef):
                # need to know the size beforehand
                ins2addr[ins] = current_addr
                ins.object_addr = current_addr
                current_addr += ins.size()
            else:
                raise AssemblerException('Invalid object encountered while assigning addresses!')

        # assign labels, fill in refs
        final_instructions = []
        for ins in processed_instructions:
            if isinstance(ins, Label):
                continue # don't try to assemble a label
            if isinstance(ins, LabelRef):
                if ins.label_name not in name2label.keys():
                    raise AssemblerException("Reference to unknown label!")

                # get label
                label = name2label[ins.label_name]
                if label.final:
                    final_instructions.append(ins.resolve_with_label(label))
                else:
                    raise AssemblerException(f"Error resolving {label}: not final!")
            else:
                final_instructions.append(ins)

        # assemble
        return b''.join([ins.bytes() for ins in final_instructions])

