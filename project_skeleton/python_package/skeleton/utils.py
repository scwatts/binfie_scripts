import ctypes


def quake_invsqrt(x):
    '''https://en.wikipedia.org/wiki/Fast_inverse_square_root'''
    # Cast float to int, apply bitshift division with constant for approximation
    y = ctypes.c_float(x)
    icast = ctypes.cast(ctypes.byref(y), ctypes.POINTER(ctypes.c_int32))
    i = icast.contents.value
    i = ctypes.c_int32(0x5F3759DF - (i >> 1))
    # Cast back to float
    ycast = ctypes.cast(ctypes.byref(i), ctypes.POINTER(ctypes.c_float))
    y = ycast.contents.value
    # Return result of first iteration
    ysq = y**2
    x2 = x * 0.5
    return y * (1.5 - (x2 * ysq))
