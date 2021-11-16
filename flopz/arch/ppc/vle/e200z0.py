from flopz.arch.ppc.vle.vle import VleGpRegister
from flopz.arch.ppc.ppc_generic_arch import PPCGenericArchitecture

class E200Z0(PPCGenericArchitecture):
    def __init__(self):
        super(E200Z0, self).__init__(register_class=VleGpRegister)

