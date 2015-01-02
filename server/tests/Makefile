# Flags passed to the preprocessor.
# Set Google Test's header directory as a system directory, such that
# the compiler doesn't generate warnings in Google Test headers.
CPPFLAGS += -I..

# Flags passed to the C++ compiler.
CXXFLAGS += -g -Wall -Wextra -pthread -std=c++0x

# Library flags
LDFLAGS += /usr/lib/libgtest.a /usr/lib/libgtest_main.a -lpthread

# All tests produced by this Makefile.  Remember to add new tests you
# created to the list.
TEST_CPP = $(wildcard *_test.cpp)
TEST_O = $(patsubst %.cpp, %.o, $(TEST_CPP))
MAIN_FILES = ../main.cpp ../test_client.cpp
ALL_O = $(patsubst %.cpp, %.o, $(filter-out $(MAIN_FILES), $(wildcard ../*.cpp)))

all : test

clean :
	rm -f $(TESTS) *.o

%.o: %.cpp
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) -c $^ -o $@

test : $(TEST_O) $(ALL_O)
	$(CXX) -o $@ $^ $(LDFLAGS) 
	rm *.o
