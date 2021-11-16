from flopz.arch.arm.thumb.plchldr_reg import PlchldrRegister
from flopz.arch.arm.arm_generic_arch import ARMGenericArchitecture


class Plchldr5000(ARMGenericArchitecture):
    def __init__(self):
        super(Plchldr5000, self).__init__(register_class=PlchldrRegister)