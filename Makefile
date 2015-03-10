
SWIG_F = -c++ -Wall -cppext cc -python -Iinclude

# c++11 code, catch all warnings as errors
CXXFLAGS += -std=c++11 -Wall -Werror -g -Iinclude

all: bin/_large_float.so bin/_interval.so



interface/interval_wrap.cc: include/interval.h include/large_float.h interface/interval.i
	swig $(SWIG_F) interface/interval.i

obj/interval_wrap.o: interface/interval_wrap.cc
	$(CXX) $(CXXFLAGS) `python3-config --cflags` -c interface/interval_wrap.cc -o obj/interval_wrap.o

bin/_interval.so: obj/interval_wrap.o
	$(CXX) $(CXXFLAGS) -lmpfr -bundle `python3-config --ldflags` obj/interval_wrap.o -o bin/_interval.so
	cp interface/interval.py bin




interface/large_float_wrap.cc: include/large_float.h interface/large_float.i
	swig $(SWIG_F) interface/large_float.i

obj/large_float_wrap.o: interface/large_float_wrap.cc
	$(CXX) $(CXXFLAGS) `python3-config --cflags` -c interface/large_float_wrap.cc -o obj/large_float_wrap.o

bin/_large_float.so: obj/large_float_wrap.o
	$(CXX) $(CXXFLAGS) -lmpfr -bundle `python3-config --ldflags` obj/large_float_wrap.o -o bin/_large_float.so
	cp interface/large_float.py bin










.PHONY: clean
clean:
	$(RM) -r bin/*
	$(RM) interface/*.py
	$(RM) interface/*_wrap.cc
	$(RM) obj/*





.PHONY: test
test: large_float_test interval_test





.PHONY: large_float_test
large_float_test: bin/large_float_test.py
	./bin/large_float_test.py

bin/large_float_test.py: test/large_float_test.py bin/_large_float.so
	ln -f test/large_float_test.py bin/large_float_test.py



.PHONY: interval_test
interval_test: bin/interval_test.py
	./bin/interval_test.py

bin/interval_test.py: test/interval_test.py bin/_interval.so
	ln -f test/interval_test.py bin/interval_test.py

