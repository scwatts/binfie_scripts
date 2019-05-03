#ifndef __UTILS_H__
#define __UTILS_H__


#include <Python.h>


// Callable from python
PyObject *quake_invsqrt(PyObject *self, PyObject *args);

// Internal
float Q_rsqrt( float number );


#endif
