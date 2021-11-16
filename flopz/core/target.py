from typing import Tuple

from flopz.core.addressable_object import AddressableObject
from flopz.core.function import Function
from flopz.core.shellcode import Shellcode
from flopz.listener.protocol import Protocol


class Target:
    """
    Base class that all targets have to derive from
    A target
    - provides code for all Gadgets (SlicePatch, SliceGadget, InstrumentationGadget, DataOut)
    - provides optional gadgets and hooks
    - provides a Protocol that the listener can use to talk to the instrumentation code

    It is parameterizable, in that it receives target addresses for the locations of each gadgets

    A SlicePatch is a Patch that replaces original instructions with a jump to the SliceGadget

    A SliceGadget is generated for each SlicePatch.
    It is in charge of saving at least one register, jumping to the appropriate InstrumentationGadget,
    executing the sliced original code and returning back to the original code after that

    An InstrumentationGadget is generated for each possible type of "output data combination" or hook action
    It needs to dump data that it is configured to dump, by sending it to the host using the DataOut function.
    it can implement many other functions, if necessary.
    After it's done, it needs to return to the SliceGadget.
    How that happens is up to the developer, it needs to be adjusted for each architecture or processor core

    The dataOut function is the last thing that is mandatory to be provided by the Target.
    It implements logic to send out data to the host.
    The format is always [tracelet ID][data as defined in trace config]
    """
    def __init__(self, target_ram: int, target_ram_len: int):
        """
        :param target_ram: Absolute address of instrumentation-reserved ram area
        :param target_ram_len: How much ram can we use
        """
        self.target_ram = target_ram
        self.target_ram_len = target_ram_len

    def get_init_gadgets(self, init_slice_addr: int, original_bytes: bytes,
                        init_gadget_addr: int) -> Tuple[Shellcode, Shellcode]:
        """
        The init Gadget is a SlicePatch that calls into custom initialization code.
        :param init_slice_addr: where to put the call to our init function, as absolute addr within the original file
        :param original_bytes: which bytes to replace
        :param init_gadget_addr: where to put the init gadget, as absolute addr
        :return: a tuple, with first element being the SlicePatch to replace the original instructions, the second element being the instrumentation initialization code
        """
        return Shellcode(), Shellcode()

    def get_slice_gadgets(self, slice_addr: int, original_bytes: bytes, id: int,
                          slice_gadget_addr: int, instrumentation_gadget: AddressableObject) -> Tuple[Shellcode, Shellcode]:
        """
        Called for each configured target location/slice
        The SlicePatch has to replace the original instructions and jump to the SliceGadget
        The SliceGadget needs to prepare execution of the InstrumentationGadget and jump to it
        After the InstrumentationGadget has executed, the SliceGadget has to execute the original instructions
        ..and finally return to the original code location

        :param slice_addr: the absolute address of the target instrumentation location within the original file
        :param original_bytes: which original bytes to replace
        :param id: each slice needs to have a unique id
        :param slice_gadget_addr: where to put the slice gadget
        :param instrumentation_gadget: the instrumentation gadget to jump to
        :return: a tuple, with the first element being the SlicePatch (replacing the original instructions) and the second element being the associated SliceGadget
        """
        return Shellcode(), Shellcode()

    def get_instrumentation_gadget(self, config: dict, target_addr: int, dataout_func: Function) -> Shellcode:
        """
        generate an instrumentation gadget, based on 'dump' config
        The instrumentation gadget is in charge of sending a configurable amount of data and returning back to the SliceGadget
        the instrumentation gadget should be used by _many_ sliceGadgets, which means you need to pass the return address somehow
        ..instead of jumping to a constant address
        :param config: dump config
        :param target_addr: where to put the instrumentation gadget
        :param dataout_func: the data_out function to use
        :return: A shellcode/module which implements the instrumentation (i.e. send data and jump back to SliceGadget)
        """
        return Shellcode()

    def get_data_out_function(self, target_addr: int) -> Function:
        """
        Implement this, so it returns a function that sends data to the instrumenting host
        using whatever channel your target can provide. How the function reads its parameters is up to you.
        At the very least, the caller should provide a length and a pointer to memory.
        :param target_addr: absolute base address of function
        :return: a function which handles the egress of data
        """
        return Function(address=target_addr)

    @staticmethod
    def get_protocol() -> Protocol:
        """
        :return: A Protocol that works with this target
        """
        return Protocol

    @staticmethod
    def name() -> str:
        """
        override this to return a unique name for your target
        :return: a string containing a unique name for this target
        """
        return ''