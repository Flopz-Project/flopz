
from flopz.arch.arm.arm_generic_arch import ARMGenericArchitecture, ArmRegister


class Stm32F407(ARMGenericArchitecture):
    def __init__(self):
        super(Stm32F407, self).__init__(register_class=ArmRegister)
