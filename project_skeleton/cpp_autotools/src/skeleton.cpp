#include "skeleton.h"


int main(int argc, char *argv[]) {
    // Get options and run program
    arguments::Arguments args = arguments::get_arguments(argc, argv);
    return execute_program(args);
}

int execute_program(arguments::Arguments &args) {
    fprintf(stdout, "Input filepath: %s\n", args.input_fp.c_str());
    fprintf(stdout, "Output filepath: %s\n", args.output_fp.c_str());
    return 0;
}
