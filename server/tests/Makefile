# Flags passed to the preprocessor.
# Set Google Test's header directory as a system directory, such that
# the compiler doesn't generate warnings in Google Test headers.
CPPFLAGS += -I../include

# Flags passed to the C++ compiler.
CXXFLAGS += -g -Wall -Wextra -pthread -std=c++0x -pg 

# Library flags
LDFLAGS += /usr/lib/libgtest.a /usr/lib/libgtest_main.a -lpthread -lpugixml

# All tests produced by this Makefile.  Remember to add new tests you
# created to the list.
TEST_CPP = $(wildcard *_test.cpp)
TEST_O = $(patsubst %.cpp, src/%.o, $(TEST_CPP))
MAIN_FILES = ../main.cpp ../test_client.cpp
ALL_O = $(patsubst ../src/%.cpp, src/%.o, $(filter-out $(MAIN_FILES), $(wildcard ../src/*.cpp)))

all : test
	mkdir src

valgrind: test
	valgrind --tool=memcheck --leak-check=full ./test 

clean :
	rm -f $(TESTS) *.o src/*.o


src/%.o: ../src/%.cpp
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) -c $^ -o $@

src/%.o: %.cpp 
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) -c $^ -o $@

%.cpp: $(wildcard ../include/*.h)


test : $(TEST_O) $(ALL_O) /usr/lib/libgtest.a
	$(CXX) -o $@ $^ $(LDFLAGS) 

.PHONY: all valgrind
