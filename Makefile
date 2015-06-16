UNAME := $(shell uname)
SWIGFLAGS := -c++ -python -Iinclude -outdir bin -w315
CXXFLAGS += -std=c++11 -Iinclude -w 


ifeq ($(UNAME), Darwin)
	BUNDLE := -bundle
	PIC := -fpic
endif

ifeq ($(UNAME), Linux)
	BUNDLE := -shared
	PIC := -fpic
endif

ifeq ($(CXX), clang++)
	NO_DEP_REG = -Wno-deprecated-register
endif

# take the c specific flag out of python cflags
PY3_CFLAGS := $(subst -Wstrict-prototypes,,$(shell python3-config --cflags))

ifeq ($(CXX), g++)
	PY3_CFLAGS := $(subst -fstack-protector-strong,,$(PY3_CFLAGS))
endif

# Object files used to create the .so for each type
BASE_OBJ := obj/large_float.o obj/interval.o obj/box.o 
BASE_OBJ := $(BASE_OBJ) obj/fast_interval.o obj/fast_box.o
TESTABLE_UTILS_OBJ := obj/testable_utils_wrap.o $(BASE_OBJ)
GELPIA_UTILS_OBJ := obj/gelpia_utils_wrap.o obj/function.o $(BASE_OBJ)

# Included files for each type
LARGE_FLOAT_INC := include/large_float.h
INTERVAL_INC := include/interval.h $(LARGE_FLOAT_INC)
BOX_INC := include/box.h $(INTERVAL_INC)
FUNCTION_INC := include/function.h $(BOX_INC)
TESTABLE_UTILS_INC := $(BOX_INC)
GELPIA_UTILS_INC := $(FUNCITON_INC)

FAST_INTERVAL_INC := include/fast_interval.h
FAST_BOX_INC := include/fast_box.h $(INTERVAL_INC)

# Compile flags for the steps to create each .so
WRAP_FLAGS := $(CXXFLAGS) $(PIC) -c $(NO_DEP_REG) $(PY3_CFLAGS)
COMPILE_FLAGS := $(CXXFLAGS) $(PIC) -c
LINK_FLAGS := $(CXXFLAGS) $(BUNDLE) -lmpfr -lmpfi -lboost_serialization -lprim `python3-config --ldflags`




all: $(BASE_OBJ) obj/gelpia_utils_wrap.o
	@cd src && ls *.py | xargs -Isol ln -f sol ../bin/sol
	@ln -f src/gelpia bin/gelpia
	@cp -rf src/rewriter bin/rewriter

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



obj/fast_interval.o:  $(FAST_INTERVAL_INC) src/fast_interval.cc
	$(CXX) $(COMPILE_FLAGS) -frounding-math -o obj/fast_interval.o src/fast_interval.cc

obj/fast_box.o:  $(FAST_BOX_INC) src/fast_box.cc
	$(CXX) $(COMPILE_FLAGS) -frounding-math -o obj/fast_box.o src/fast_box.cc




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
	./bin/testable_utils_test.py -v

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
	$(RM) parser.out
	$(RM) parsetab.py
	$(RM) -r */__pycache__/
	$(RM) -r */*/__pycache__/
