# Build flags
AM_CXXFLAGS = -std=c++14 -Wall -Wextra
AM_CPPFLAGS = -I$(top_srcdir)/include

# Sources for ELF and static library
sources = \
 		  skeleton.cpp \
 		  skeleton_opts.cpp \
 		  ../include/skeleton.h \
 		  ../include/skeleton_opts.h

# Libraries for tests (set LIBRARY to prevent compiling main() block)
check_LIBRARIES = libskeleton.a
libskeleton_a_SOURCES = $(sources)
libskeleton_a_CXXFLAGS = -DLIBRARY $(AM_CXXFLAGS)

# ELF
bin_PROGRAMS = skeleton
skeleton_SOURCES = $(sources)
