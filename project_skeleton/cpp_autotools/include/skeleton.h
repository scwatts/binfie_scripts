#ifndef __SKELETON_H__
#define __SKELETON_H__


#include <cstdio>
#include <fstream>
#include <sstream>
#include <string>


#include "skeleton_opts.h"


int execute_program(arguments::Arguments &args);
std::string read_first_line(std::string &input_fp);


#endif
