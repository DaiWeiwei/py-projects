from ctypes import *


class CopyDataStructure(Structure):
    _fields_ = [('dwData', c_int),
                ('cbData', c_int),
                ('lpData', c_void_p)
                ]
