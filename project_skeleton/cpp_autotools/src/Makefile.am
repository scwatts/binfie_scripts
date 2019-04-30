# Build flags
AM_CXXFLAGS = -std=c++14 -Wall -Wextra
AM_CPPFLAGS = -I$(top_srcdir)/include

# Sources for ELF and static library
sources = \
 		  skeleton.cpp \
 		  skeleton_opts.cpp \
 		  ../include/skeleton.h \
 		  ../include/skeleton_opts.h

# ELF
bin_PROGRAMS = skeleton
skeleton_SOURCES = $(sources)
