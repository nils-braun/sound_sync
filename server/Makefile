# Flags passed to the preprocessor.
CPPFLAGS += -Iinclude

# Flags passed to the C++ compiler.
CXXFLAGS += -g -Wall -Wextra -pthread -std=c++0x 

# Library flags
LDFLAGS += -lpthread -lpugixml

# All tests produced by this Makefile.
MAIN_FILES = main.cpp
ALL_O = $(patsubst src/%.cpp, Server/src/%.o, $(filter-out $(MAIN_FILES), $(wildcard src/*.cpp)))
MAIN_O = $(patsubst %.cpp, Server/%.o, $(MAIN_FILES))
MAIN = Server/server

all : $(MAIN)

clean :
	rm -f $(ALL_O) $(MAIN_O) $(MAIN)

src/%.o: ../src/%.cpp
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) -c $^ -o $@

Server/src/%.o: src/%.cpp 
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) -c $^ -o $@

src/%.cpp: include/%.h

$(MAIN_O): $(MAIN_FILES)
	$(CXX) $(CPPFLAGS) $(CXXFLAGS) -c $^ -o $@

$(MAIN): $(ALL_O) $(MAIN_O)
	$(CXX) -o $@ $^ $(LDFLAGS) 

.PHONY: all valgrind