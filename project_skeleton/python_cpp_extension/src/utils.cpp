#include "utils.h"


PyObject *quake_invsqrt(PyObject *self, PyObject *args) {
    // Collect top-level arguments
    float number;
    if(!PyArg_ParseTuple(args, "f", &number)) {
      return NULL;
    }

    // Run invsqrt and cast result to PyObject
    float result = Q_rsqrt(number);
    PyObject *py_result= PyFloat_FromDouble(result);
    return py_result;
}

// Taken verbose from https://en.wikipedia.org/wiki/Fast_inverse_square_root
float Q_rsqrt( float number ) {
    long i;
    float x2, y;
    const float threehalfs = 1.5F;

    x2 = number * 0.5F;
    y  = number;
    i  = * ( long * ) &y;                       // evil floating point bit level hacking
    i  = 0x5f3759df - ( i >> 1 );               // what the fuck?
    y  = * ( float * ) &i;
    y  = y * ( threehalfs - ( x2 * y * y ) );   // 1st iteration
    // y  = y * ( threehalfs - ( x2 * y * y ) );   // 2nd iteration, this can be removed

    return y;
}
