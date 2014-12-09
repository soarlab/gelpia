
all: bin/timer_tester

bin/globopt.o: src/globopt.cc
	$(CXX) $(CXXFLAGS) -c -std=c++11 -Wall -Werror src/globopt.cc -o bin/globopt.o

bin/functions.o: src/functions.cc
	$(CXX) $(CXXFLAGS) -c -std=c++11 -Wall -Werror src/functions.cc -o bin/functions.o

bin/timer_tester: src/timer_tester.cc bin/globopt.o bin/functions.o
	$(CXX) $(CXXFLAGS) -std=c++11 -Wall -Werror src/timer_tester.cc bin/globopt.o bin/functions.o -o bin/timer_tester

.PHONY: clean
clean:
	$(RM) -f bin/globopt
	$(RM) -f bin/globopt.o
	$(RM) -f bin/functions.o
	$(RM) -f bin/timer_tester
