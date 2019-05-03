#include "utils.h"


// Method documentation
static char quake_invsqrt_docs[] = "Fast inverse sqrt approximation";

// Method definition
static PyMethodDef SkeletonMethods[] = {
    {"quake_invsqrt", (PyCFunction)quake_invsqrt, METH_VARARGS, quake_invsqrt_docs},
    {NULL, NULL, 0, NULL}
};

// Module documentation
static char skeleton_module_docs[] = "Skeleton package example";

// Module definition
static struct PyModuleDef skeleton_module = {
    PyModuleDef_HEAD_INIT,
    "_skeleton",
    skeleton_module_docs,
    -1,
    SkeletonMethods
};

// Module init
PyMODINIT_FUNC PyInit__skeleton(void) {
	return PyModule_Create(&skeleton_module);
}
