UNAME := $(shell uname)
BUNDLE := -shared -fpic


ifeq ($(UNAME), Darwin)
	BUNDLE := -bundle
endif

ifeq ($(UNAME), Linux)
	SHARED := -fpic
endif



SWIG_F = -c++ -Wall -cppext cc -python -Iinclude

# c++11 code, catch all warnings as errors
CXXFLAGS += -std=c++11 -Wall -Werror -g -Iinclude




all: bin/_large_float.so bin/_interval.so bin/_box.so bin/_function.so





interface/large_float_wrap.cc: include/large_float.h interface/large_float.i
	swig $(SWIG_F) interface/large_float.i

obj/large_float_wrap.o: interface/large_float_wrap.cc
	$(CXX) $(CXXFLAGS) `python3-config --cflags` $(SHARED) -c interface/large_float_wrap.cc -o obj/large_float_wrap.o

bin/_large_float.so: obj/large_float_wrap.o
	$(CXX) $(CXXFLAGS) -lmpfr $(BUNDLE) `python3-config --ldflags` obj/large_float_wrap.o -o bin/_large_float.so
	ln -f interface/large_float.py bin/large_float.py




interface/interval_wrap.cc: include/interval.h include/large_float.h interface/interval.i
	swig $(SWIG_F) interface/interval.i

obj/interval_wrap.o: interface/interval_wrap.cc
	$(CXX) $(CXXFLAGS) `python3-config --cflags` $(SHARED) -c interface/interval_wrap.cc -o obj/interval_wrap.o

bin/_interval.so: obj/interval_wrap.o
	$(CXX) $(CXXFLAGS) -lmpfr $(BUNDLE) `python3-config --ldflags` obj/interval_wrap.o -o bin/_interval.so
	ln -f interface/interval.py bin/interval.py




interface/box_wrap.cc: include/box.h include/interval.h include/large_float.h interface/box.i
	swig $(SWIG_F) interface/box.i

obj/box_wrap.o: interface/box_wrap.cc
	$(CXX) $(CXXFLAGS) `python3-config --cflags` $(SHARED) -c interface/box_wrap.cc -o obj/box_wrap.o

obj/box.o: src/box.cc include/box.h
	$(CXX) $(CXXFLAGS) $(SHARED) -c src/box.cc -o obj/box.o

bin/_box.so: obj/box.o obj/box_wrap.o
	$(CXX) $(CXXFLAGS) -lmpfr $(BUNDLE) `python3-config --ldflags` obj/box_wrap.o obj/box.o -o bin/_box.so
	ln -f interface/box.py bin/box.py




interface/function_wrap.cc: include/box.h include/interval.h include/large_float.h interface/function.i
	swig $(SWIG_F) interface/function.i

obj/function_wrap.o: interface/function_wrap.cc
	$(CXX) $(CXXFLAGS) `python3-config --cflags` $(SHARED) -c interface/function_wrap.cc -o obj/function_wrap.o

obj/function.o: src/function.cc include/function.h
	$(CXX) $(CXXFLAGS) $(SHARED) -c src/function.cc -o obj/function.o

bin/_function.so: obj/function.o obj/function_wrap.o obj/box.o
	$(CXX) $(CXXFLAGS) -lmpfr $(BUNDLE) `python3-config --ldflags` obj/function_wrap.o obj/function.o obj/box.o -o bin/_function.so
	ln -f interface/function.py bin/function.py







.PHONY: clean
clean:
	$(RM) -r bin/*
	$(RM) interface/*.py
	$(RM) interface/*_wrap.cc
	$(RM) obj/*





.PHONY: test
test: large_float_test interval_test box_test





.PHONY: large_float_test
large_float_test: bin/large_float_test.py
	./bin/large_float_test.py

bin/large_float_test.py: test/large_float_test.py bin/_large_float.so
	@ln -f test/large_float_test.py bin/large_float_test.py



.PHONY: interval_test
interval_test: bin/interval_test.py
	./bin/interval_test.py

bin/interval_test.py: test/interval_test.py bin/_interval.so
	@ln -f test/interval_test.py bin/interval_test.py



.PHONY: box_test
box_test: bin/box_test.py
	./bin/box_test.py

bin/box_test.py: test/box_test.py bin/_box.so
	@ln -f test/box_test.py bin/box_test.py



.PHONY: globopt
globopt: bin/globopt.py
	./bin/globopt.py

bin/globopt.py: test/globopt.py bin/_box.so
	@ln -f test/globopt.py bin/globopt.py


.PHONY: paperopt
paperopt: bin/paperopt.py
	./bin/paperopt.py

bin/paperopt.py: test/paperopt.py bin/_box.so
	@ln -f test/paperopt.py bin/paperopt.py



.PHONY: non_pri_paperopt
non_pri_paperopt: bin/non_pri_paperopt.py
	./bin/non_pri_paperopt.py

bin/non_pri_paperopt.py: test/non_pri_paperopt.py bin/_box.so
	@ln -f test/non_pri_paperopt.py bin/non_pri_paperopt.py



.PHONY: multiworker
multiworker: bin/multiworker.py
	./bin/multiworker.py

bin/multiworker.py: test/multiworker.py bin/_box.so
	@ln -f test/multiworker.py bin/multiworker.py
