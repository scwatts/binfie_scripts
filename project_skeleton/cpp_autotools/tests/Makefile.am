# Build flags
AM_CXXFLAGS = -std=c++11 -Wall -Wextra -fopenmp
AM_CPPFLAGS = -DDATADIR=\"$(srcdir)/data/\"
AM_FFLAGS = -Wall -Wextra

EXTRA_DIST = data

check_LIBRARIES = libtest_main.a
libtest_main_a_SOURCES = test_main.cpp catch.hpp

LDADD = libtest_main.a ../src/libskeleton.a

check_PROGRAMS = test_skeleton
AM_DEFAULT_SOURCE_EXT = .cpp
TESTS = $(check_PROGRAMS)
