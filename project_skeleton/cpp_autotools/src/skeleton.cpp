#include "skeleton.h"


#if !defined(LIBRARY)
int main(int argc, char *argv[]) {
    // Get options and run program
    arguments::Arguments args = arguments::get_arguments(argc, argv);
    return execute_program(args);
}
#endif

int execute_program(arguments::Arguments &args) {
    fprintf(stdout, "Input filepath: %s\n", args.input_fp.c_str());
    fprintf(stdout, "Output filepath: %s\n", args.output_fp.c_str());

    std::string line = read_first_line(args.input_fp);
    fprintf(stdout, "\nFirst line of input file: %s\n", line.c_str());
    return 0;
}

std::string read_first_line(std::string &input_fp) {
    std::ifstream input_fh(input_fp);
    std::string line;
    std::getline(input_fh, line);
    input_fh.close();
    return line;
}
