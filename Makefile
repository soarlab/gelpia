
all: bin/globopt

bin/globopt: src/globopt.cc
	$(CXX) $(CXXFLAGS) -Wall -Werror src/globopt.cc -o bin/globopt


.PHONY: clean
clean:
	$(RM) -rf bin/globopts
