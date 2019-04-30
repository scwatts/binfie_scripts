#ifndef __SKELETON_OPTS_H__
#define __SKELETON_OPTS_H__


#include <cstdio>
#include <vector>
#include <string>


#include <getopt.h>


#include "config.h"  // autoconf header


namespace arguments {


struct Arguments {
    std::string input_fp;
    std::string output_fp;
};

void print_help(FILE *stdst);
void print_version(FILE *stdst);
Arguments get_arguments(int argc, char **argv);


} // namespace arguments


#endif
