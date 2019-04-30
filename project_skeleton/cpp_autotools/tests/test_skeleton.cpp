#include "catch.hpp"


#include "../include/skeleton.h"


TEST_CASE("Simple unittest") {
    // Input files
    std::string data_dir = std::string(DATADIR);
    std::string input_a_fp =  data_dir + "input_a.txt";
    std::string input_b_fp =  data_dir + "input_b.txt";

    // Tests
    REQUIRE(read_first_line(input_a_fp)=="a");
    REQUIRE(read_first_line(input_b_fp)=="b");
}
