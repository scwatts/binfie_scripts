#include "skeleton_opts.h"


namespace arguments {


void print_help(FILE *stdst) {
    // Print version
    print_version(stdst);
    // Print Usage
    fprintf(stdst, "\n");
    fprintf(stdst, "Usage:\n");
    fprintf(stdst, "  skeleton [options]\n");
    fprintf(stdst, "\n");
    fprintf(stdst, "Options:\n");
    fprintf(stdst, "    -i <filepath>, --input_fp <filepath>\n");
    fprintf(stdst, "                    Input filepath\n");
    fprintf(stdst, "    -o <filepath>, --output_fp <filepath>\n");
    fprintf(stdst, "                    Output filepath\n");
    fprintf(stdst, "\n");
    fprintf(stdst, "Other:\n");
    fprintf(stdst, "  -h, --help\n");
    fprintf(stdst, "                    display this help and exit\n");
    fprintf(stdst, "  -v, --version\n");
    fprintf(stdst, "                    display version information and exit\n");
}

void print_version(FILE *stdst) {
    fprintf(stdst, "Program: skeleton\n");
    fprintf(stdst, "Version %s\n", PACKAGE_VERSION);
    fprintf(stdst, "Contact: Stephen Watts (s.watts2@student.unimelb.edu.au)\n");
}

Arguments get_arguments(int argc, char **argv) {
    Arguments args;
    // Long opts
    struct option long_options[] =
        {
            {"input_fp", required_argument, NULL, 'i'},
            {"output_fp", required_argument, NULL, 'o'},
            {"version", no_argument, NULL, 'v'},
            {"help", no_argument, NULL, 'h'},
            {NULL, 0, 0, 0}
        };

    // Parse commandline arguments
    while (1) {
        // Parser variables
        int long_options_index = 0;
        int c;

        // Parser
        c = getopt_long(argc, argv, "i:o:vh", long_options, &long_options_index);

        // If no more arguments to parse, break
        if (c == -1) {
            break;
        }

        // Process current arguments
        switch(c) {
            case 'i':
                args.input_fp = optarg;
                break;
            case 'o':
                args.output_fp = optarg;
                break;
            case 'v':
                print_version(stdout);
                exit(0);
            case 'h':
                print_help(stdout);
                exit(0);
            default:
                exit(1);
        }
    }

    // Ensure that input filepaths are set
    if (args.input_fp.empty()) {
        print_help(stderr);
        fprintf(stderr,"\n%s: error: argument -i/--input_fp is required\n", argv[0]);
        exit(1);
    }
    if (args.output_fp.empty()) {
        print_help(stderr);
        fprintf(stderr,"\n%s: error: argument -o/--output_fp is required\n", argv[0]);
        exit(1);
    }

    return args;
}


} // namespace arguments
