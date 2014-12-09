
all: bin/globopt

bin/globopt: src/globopt.cc
	$(CXX) $(CXXFLAGS) -std=c++11 -Wall -Werror src/globopt.cc -o bin/globopt


.PHONY: clean
clean:
	$(RM) -rf bin/globopts
