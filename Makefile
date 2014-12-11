override CXXFLAGS += -lpthread -std=c++11

all: bin/timer bin/tester

bin/helpers.o: src/helpers.cc src/helpers.h
	$(CXX) $(CXXFLAGS) -c src/helpers.cc -o bin/helpers.o

bin/globopt.o: src/globopt.cc src/helpers.h
	$(CXX) $(CXXFLAGS) -c src/globopt.cc -o bin/globopt.o

bin/globopt-par1.o: src/globopt-par1.cc src/helpers.h
	$(CXX) $(CXXFLAGS) -c src/globopt-par1.cc -o bin/globopt-par1.o

bin/globopt-sol2.o: src/globopt-sol2.cc src/helpers.h
	$(CXX) $(CXXFLAGS) -c src/globopt-sol2.cc -o bin/globopt-sol2.o

bin/functions.o: src/functions.cc
	$(CXX) $(CXXFLAGS) -c src/functions.cc -o bin/functions.o

bin/timer: src/timer.cc bin/globopt.o bin/functions.o bin/globopt-par1.o bin/helpers.o bin/globopt-sol2.o
	$(CXX) $(CXXFLAGS) src/timer.cc bin/globopt.o bin/globopt-par1.o bin/functions.o bin/helpers.o bin/globopt-sol2.o -o bin/timer

bin/tester: src/tester.cc bin/globopt.o bin/functions.o bin/globopt-par1.o bin/helpers.o bin/globopt-sol2.o
	$(CXX) $(CXXFLAGS) src/tester.cc bin/globopt.o bin/globopt-par1.o bin/functions.o bin/helpers.o bin/globopt-sol2.o -o bin/tester

.PHONY: clean
clean:
	$(RM) bin/globopt
	$(RM) bin/globopt.o
	$(RM) bin/globopt-par1.o
	$(RM) bin/globopt-sol2.o
	$(RM) bin/globopt-par1-lockfree.o
	$(RM) bin/helpers.o
	$(RM) bin/functions.o
	$(RM) bin/timer
	$(RM) bin/tester
