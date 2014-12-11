
all: bin/timer bin/tester

bin/helpers.o: src/helpers.cc src/helpers.h
	$(CXX) $(CXXFLAGS) -c -std=c++11 -Wall -Werror src/helpers.cc -o bin/helpers.o

bin/globopt.o: src/globopt.cc src/helpers.h
	$(CXX) $(CXXFLAGS) -c -std=c++11 -Wall -Werror src/globopt.cc -o bin/globopt.o

bin/globopt-par1.o: src/globopt-par1.cc src/helpers.h
	$(CXX) $(CXXFLAGS) -c -std=c++11 -Wall -Werror src/globopt-par1.cc -o bin/globopt-par1.o

bin/globopt-par1-lockfree.o: src/globopt-par1-lockfree.cc src/helpers.h
	$(CXX) $(CXXFLAGS) -c -std=c++11 -Wall -Werror src/globopt-par1-lockfree.cc -o bin/globopt-par1-lockfree.o

bin/functions.o: src/functions.cc
	$(CXX) $(CXXFLAGS) -c -std=c++11 -Wall -Werror src/functions.cc -o bin/functions.o

bin/timer: src/timer.cc bin/globopt.o bin/functions.o bin/globopt-par1.o bin/helpers.o bin/globopt-par1-lockfree.o
	$(CXX) $(CXXFLAGS) -std=c++11 -Wall -Werror src/timer.cc bin/globopt.o bin/globopt-par1.o bin/functions.o bin/helpers.o bin/globopt-par1-lockfree.o -o bin/timer

bin/tester: src/tester.cc bin/globopt.o bin/functions.o bin/globopt-par1.o bin/helpers.o bin/globopt-par1-lockfree.o
	$(CXX) $(CXXFLAGS) -std=c++11 -Wall -Werror src/tester.cc bin/globopt.o bin/globopt-par1.o bin/functions.o bin/helpers.o bin/globopt-par1-lockfree.o -o bin/tester

.PHONY: clean
clean:
	$(RM) bin/globopt
	$(RM) bin/globopt.o
	$(RM) bin/globopt-par1.o
	$(RM) bin/globopt-par1-lockfree.o
	$(RM) bin/helpers.o
	$(RM) bin/functions.o
	$(RM) bin/timer
	$(RM) bin/tester
