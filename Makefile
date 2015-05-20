UNAME := $(shell uname)
SWIGFLAGS := -c++ -Wall -python -Iinclude -outdir bin
CXXFLAGS += -std=c++11 -Wall -Werror -Iinclude

ifeq ($(UNAME), Darwin)
	BUNDLE := -bundle
	PIC := -fpic
endif

ifeq ($(UNAME), Linux)
	BUNDLE := -shared
	PIC := -fpic
endif

ifeq ($(CXX), clang++)
	NO_DEP_REG = -Wno-depreciated-register
endif

# take the c specific flag out of python cflags
PY3_CFLAGS := $(subst -Wstrict-prototypes,,$(shell python3-config --cflags))

# Object files used to create the .so for each type
BASE_OBJ := obj/large_float.o obj/interval.o obj/box.o
TESTABLE_UTILS_OBJ := obj/testable_utils_wrap.o $(BASE_OBJ)
GELPIA_UTILS_OBJ := obj/gelpia_utils_wrap.o obj/function.o $(BASE_OBJ)

# Included files for each type
LARGE_FLOAT_INC := include/large_float.h
INTERVAL_INC := include/interval.h $(LARGE_FLOAT_INC)
BOX_INC := include/box.h $(INTERVAL_INC)
FUNCTION_INC := include/function.h $(BOX_INC)
TESTABLE_UTILS_INC := $(BOX_INC)
GELPIA_UTILS_INC := $(FUNCITON_INC)

# Compile flags for the steps to create each .so
WRAP_FLAGS := $(CXXFLAGS) $(PIC) -c $(NO_DEP_REG) $(PY3_CFLAGS)
COMPILE_FLAGS := $(CXXFLAGS) $(PIC) -c
LINK_FLAGS := $(CXXFLAGS) $(BUNDLE) -lmpfr -lboost_serialization `python3-config --ldflags`




all: $(BOX_OBJ)
	@ln -f src/gelpia bin/gelpia
	@ln -f src/ian_utils.py bin/ian_utils.py
	@ln -f src/serial_solver.py bin/serial_solver.py
	@ln -f src/priority_serial_solver.py bin/priority_serial_solver.py
	@ln -f src/naive_parallel_solver.py bin/naive_parallel_solver.py


solver: bin/_gelpia_utils.so


#+-----------------------------------------------------------------------------+
#| Building each component                                                     |
#+-----------------------------------------------------------------------------+
obj/large_float.o: $(LARGE_FLOAT_INC) src/large_float.cc
	$(CXX) $(COMPILE_FLAGS) -o obj/large_float.o src/large_float.cc

obj/interval.o:  $(INTERVAL_INC) src/interval.cc
	$(CXX) $(COMPILE_FLAGS) -o obj/interval.o src/interval.cc

obj/box.o: $(BOX_INC) src/box.cc
	$(CXX) $(COMPILE_FLAGS) -o obj/box.o src/box.cc

obj/function.o: $(FUNCTION_INC) generated/function.cc
	$(CXX) $(COMPILE_FLAGS) -o obj/function.o generated/function.cc




#+-----------------------------------------------------------------------------+
#| Building gelpia_utils                                                       |
#+-----------------------------------------------------------------------------+
# run swig on gelpia_utils
generated/gelpia_utils_wrap.cc: $(GELPIA_UTILS_INC) interface/gelpia_utils.i
	swig $(SWIGFLAGS) -o generated/gelpia_utils_wrap.cc interface/gelpia_utils.i

# compile generated file
obj/gelpia_utils_wrap.o: generated/gelpia_utils_wrap.cc
	$(CXX) $(WRAP_FLAGS) -o obj/gelpia_utils_wrap.o generated/gelpia_utils_wrap.cc

# combine
bin/_gelpia_utils.so: $(GELPIA_UTILS_OBJ)
	$(CXX) -o bin/_gelpia_utils.so $(GELPIA_UTILS_OBJ) $(LINK_FLAGS)




#+-----------------------------------------------------------------------------+
#| Building testable_utils                                                     |
#+-----------------------------------------------------------------------------+
# run swig on testable_utils
generated/testable_utils_wrap.cc: $(TESTABLE_UTILS_INC) interface/testable_utils.i
	swig $(SWIGFLAGS) -o generated/testable_utils_wrap.cc interface/testable_utils.i

# compile generated file
obj/testable_utils_wrap.o: generated/testable_utils_wrap.cc
	$(CXX) $(WRAP_FLAGS) -o obj/testable_utils_wrap.o generated/testable_utils_wrap.cc

# combine
bin/_testable_utils.so: $(TESTABLE_UTILS_OBJ)
	$(CXX) -o bin/_testable_utils.so $(TESTABLE_UTILS_OBJ) $(LINK_FLAGS)




#+-----------------------------------------------------------------------------+
#| Testing                                                                     |
#+-----------------------------------------------------------------------------+
.PHONY: test
test: bin/testable_utils_test.py
	./bin/testable_utils_test.py

bin/testable_utils_test.py: bin/_testable_utils.so
	@ln -f test/testable_utils_test.py bin/testable_utils_test.py




#+-----------------------------------------------------------------------------+
#| Cleaning                                                                    |
#+-----------------------------------------------------------------------------+
.PHONY: clean
clean:
	$(RM) -r bin/*
	$(RM) obj/*
	$(RM) generated/*
