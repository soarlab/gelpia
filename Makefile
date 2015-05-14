UNAME := $(shell uname)
PIC := -fPIC
SWIGFLAGS := -c++ -Wall -python -Iinclude -outdir bin
CXXFLAGS += -std=c++11 -Wall -Werror -Iinclude

ifeq ($(UNAME), Darwin)
	echo "FIXME"
	BUNDLE := -bundleasdfsdfds
	PIC := -asfgadfhad
endif

ifeq ($(UNAME), Linux)
	BUNDLE := -shared
	PIC := -fpic
endif


all: bin/_large_float.so bin/_interval.so bin/_box.so

#+-----------------------------------------------------------------------------+
#| Building large_float                                                        |
#+-----------------------------------------------------------------------------+
# 1. run swig on large_float
generated/large_float_wrap.cc: include/large_float.h interface/large_float.i
	swig $(SWIGFLAGS) -o generated/large_float_wrap.cc interface/large_float.i

# 2. compile generated file
obj/large_float_wrap.o: generated/large_float_wrap.cc
	$(CXX) $(CXXFLAGS) $(PIC) -c -Wno-deprecated-register `python3-config --cflags` -o obj/large_float_wrap.o generated/large_float_wrap.cc

# 3. compile source
obj/large_float.o: src/large_float.cc include/large_float.h
	$(CXX) $(CXXFLAGS) $(PIC) -c -o obj/large_float.o src/large_float.cc

# 4. combine
bin/_large_float.so: obj/large_float.o obj/large_float_wrap.o
	$(CXX) $(CXXFLAGS) $(BUNDLE) -lmpfr `python3-config --ldflags` -o bin/_large_float.so obj/large_float.o obj/large_float_wrap.o




#+-----------------------------------------------------------------------------+
#| Building interval                                                           |
#+-----------------------------------------------------------------------------+
# 1. run swig on interval
generated/interval_wrap.cc: include/interval.h interface/interval.i
	swig $(SWIGFLAGS) -o generated/interval_wrap.cc interface/interval.i

# 2. compile generated file
obj/interval_wrap.o: generated/interval_wrap.cc
	$(CXX) $(CXXFLAGS) $(PIC) -c -Wno-deprecated-register `python3-config --cflags` -o obj/interval_wrap.o generated/interval_wrap.cc

# 3. compile source
obj/interval.o: src/interval.cc include/interval.h
	$(CXX) $(CXXFLAGS) $(PIC) -c -o obj/interval.o src/interval.cc

# 4. combine
bin/_interval.so: obj/interval.o obj/interval_wrap.o obj/large_float.o obj/large_float_wrap.o
	$(CXX) $(CXXFLAGS) $(BUNDLE) -lmpfr `python3-config --ldflags` -o bin/_interval.so obj/interval.o obj/interval_wrap.o obj/large_float.o obj/large_float_wrap.o




#+-----------------------------------------------------------------------------+
#| Building box                                                                |
#+-----------------------------------------------------------------------------+
# 1. run swig on box
generated/box_wrap.cc: include/box.h interface/box.i
	swig $(SWIGFLAGS) -o generated/box_wrap.cc interface/box.i

# 2. compile generated file
obj/box_wrap.o: generated/box_wrap.cc
	$(CXX) $(CXXFLAGS) $(PIC) -c -Wno-deprecated-register `python3-config --cflags` -o obj/box_wrap.o generated/box_wrap.cc

# 3. compile source
obj/box.o: src/box.cc include/box.h
	$(CXX) $(CXXFLAGS) $(PIC) -c -o obj/box.o src/box.cc

# 4. combine
bin/_box.so: obj/box.o obj/box_wrap.o obj/large_float.o obj/large_float_wrap.o
	$(CXX) $(CXXFLAGS) $(BUNDLE) -lmpfr `python3-config --ldflags` -o bin/_box.so obj/box.o obj/box_wrap.o obj/interval.o obj/interval_wrap.o obj/large_float.o obj/large_float_wrap.o



#+-----------------------------------------------------------------------------+
#| Testing                                                                     |
#+-----------------------------------------------------------------------------+
.PHONY: test
test: bin/large_float_test.py bin/interval_test.py bin/box_test.py
	./bin/large_float_test.py
	@echo "\n\n\n\n\n\n\n\n\n\n"
	./bin/interval_test.py
	@echo "\n\n\n\n\n\n\n\n\n\n"
	./bin/box_test.py

bin/large_float_test.py: bin/_large_float.so
	@ln -f test/large_float_test.py bin/large_float_test.py

bin/interval_test.py: bin/_interval.so
	@ln -f test/interval_test.py bin/interval_test.py

bin/box_test.py: bin/_box.so
	@ln -f test/box_test.py bin/box_test.py




#+-----------------------------------------------------------------------------+
#| Cleaning                                                            
#+-----------------------------------------------------------------------------+
.PHONY: clean
clean:
	$(RM) -r bin/*
	$(RM) obj/*
	$(RM) generated/*
