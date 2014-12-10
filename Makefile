
all: bin/timer_tester

bin/helpers.o: src/helpers.cc src/helpers.h
	$(CXX) $(CXXFLAGS) -c -std=c++11 -Wall -Werror src/helpers.cc -o bin/helpers.o

bin/globopt.o: src/globopt.cc src/helpers.h
	$(CXX) $(CXXFLAGS) -c -std=c++11 -Wall -Werror src/globopt.cc -o bin/globopt.o

bin/globopt-par1.o: src/globopt-par1.cc src/helpers.h
	$(CXX) $(CXXFLAGS) -c -std=c++11 -Wall -Werror src/globopt-par1.cc -o bin/globopt-par1.o

bin/functions.o: src/functions.cc
	$(CXX) $(CXXFLAGS) -c -std=c++11 -Wall -Werror src/functions.cc -o bin/functions.o

bin/timer_tester: src/timer_tester.cc bin/globopt.o bin/functions.o bin/globopt-par1.o bin/helpers.o
	$(CXX) $(CXXFLAGS) -std=c++11 -Wall -Werror src/timer_tester.cc bin/globopt.o bin/globopt-par1.o bin/functions.o bin/helpers.o -o bin/timer_tester

.PHONY: clean
clean:
	$(RM) -f bin/globopt
	$(RM) -f bin/globopt.o
	$(RM) -f bin/globopt-par1.o
	$(RM) -f bin/helpers.o
	$(RM) -f bin/functions.o
	$(RM) -f bin/timer_tester
