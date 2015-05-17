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

# Object files used to create the .so for each type
LARGE_FLOAT_OBJ := obj/large_float.o obj/large_float_wrap.o
INTERVAL_OBJ := obj/interval.o obj/interval_wrap.o $(LARGE_FLOAT_OBJ)
BOX_OBJ := obj/box.o obj/box_wrap.o $(INTERVAL_OBJ)
FUNCTION_OBJ := obj/function.o obj/function_wrap.o $(BOX_OBJ)
GELPIA_UTILS_OBJ := obj/gelpia_utils_wrap.o $(FUNCTION_OBJ)

# Included files for each type
LARGE_FLOAT_INC := include/large_float.h
INTERVAL_INC := include/interval.h $(LARGE_FLOAT_INC)
BOX_INC := include/box.h $(INTERVAL_INC)
FUNCTION_INC := include/function.h $(BOX_INC)
GELPIA_UTILS_INC := $(FUNCITON_INC)

# Compile flags for the steps to create each .so
2_FLAGS := $(CXXFLAGS) $(PIC) -c -Wno-deprecated-register `python3-config --cflags`
3_FLAGS := $(CXXFLAGS) $(PIC) -c
4_FLAGS := $(CXXFLAGS) $(BUNDLE) -lmpfr `python3-config --ldflags`




all: 
	@ln -f src/gelpia bin/gelpia
	@ln -f src/ian_utils.py bin/ian_utils.py
	@ln -f src/serial_solver.py bin/serial_solver.py
	@ln -f src/priority_serial_solver.py bin/priority_serial_solver.py
	@ln -f src/naive_parallel_solver.py bin/naive_parallel_solver.py


solver: bin/_gelpia_utils.so


#+-----------------------------------------------------------------------------+
#| Building large_float                                                        |
#+-----------------------------------------------------------------------------+
# 1. run swig on large_float
generated/large_float_wrap.cc: $(LARGE_FLOAT_INC) interface/large_float.i
	swig $(SWIGFLAGS) -o generated/large_float_wrap.cc interface/large_float.i

# 2. compile generated file
obj/large_float_wrap.o: generated/large_float_wrap.cc
	$(CXX) $(2_FLAGS) -o obj/large_float_wrap.o generated/large_float_wrap.cc

# 3. compile source
obj/large_float.o: $(LARGE_FLOAT_INC) src/large_float.cc
	$(CXX) $(3_FLAGS) -o obj/large_float.o src/large_float.cc

# 4. combine
bin/_large_float.so: $(LARGE_FLOAT_OBJ)
	$(CXX) $(4_FLAGS) -o bin/_large_float.so $(LARGE_FLOAT_OBJ)




#+-----------------------------------------------------------------------------+
#| Building interval                                                           |
#+-----------------------------------------------------------------------------+
# 1. run swig on interval
generated/interval_wrap.cc: $(INTERVAL_INC) interface/interval.i
	swig $(SWIGFLAGS) -o generated/interval_wrap.cc interface/interval.i

# 2. compile generated file
obj/interval_wrap.o: generated/interval_wrap.cc
	$(CXX) $(2_FLAGS) -o obj/interval_wrap.o generated/interval_wrap.cc

# 3. compile source
obj/interval.o:  $(INTERVAL_INC) src/interval.cc
	$(CXX) $(3_FLAGS) -o obj/interval.o src/interval.cc

# 4. combine
bin/_interval.so: $(INTERVAL_OBJ)
	$(CXX) $(4_FLAGS) -o bin/_interval.so $(INTERVAL_OBJ)




#+-----------------------------------------------------------------------------+
#| Building box                                                                |
#+-----------------------------------------------------------------------------+
# 1. run swig on box
generated/box_wrap.cc: $(BOX_INC) interface/box.i
	swig $(SWIGFLAGS) -o generated/box_wrap.cc interface/box.i

# 2. compile generated file
obj/box_wrap.o: generated/box_wrap.cc
	$(CXX) $(2_FLAGS) -o obj/box_wrap.o generated/box_wrap.cc

# 3. compile source
obj/box.o: $(BOX_INC) src/box.cc
	$(CXX) $(3_FLAGS) -o obj/box.o src/box.cc

# 4. combine
bin/_box.so: $(BOX_OBJ)
	$(CXX) $(4_FLAGS) -o bin/_box.so $(BOX_OBJ)




#+-----------------------------------------------------------------------------+
#| Building function                                                           |
#+-----------------------------------------------------------------------------+
# 1. run swig on gelpia_cpp_interface
generated/function_wrap.cc: $(FUNCTION_INC) interface/function.i
	swig $(SWIGFLAGS) -o generated/function_wrap.cc interface/function.i

# 2. compile generated file
obj/function_wrap.o: generated/function_wrap.cc
	$(CXX) $(2_FLAGS) -o obj/function_wrap.o generated/function_wrap.cc

# 3. compile source
obj/function.o: $(FUNCTION_INC) generated/function.cc
	$(CXX) $(3_FLAGS) -o obj/function.o generated/function.cc

# 4. combine
bin/_function.so: $(FUNCTION_OBJ)
	$(CXX) $(4_FLAGS) -o bin/_function.so $(FUNCTION_OBJ)




#+-----------------------------------------------------------------------------+
#| Building gelpia_utils                                                       |
#+-----------------------------------------------------------------------------+
# 1. run swig on gelpia_utils
generated/gelpia_utils_wrap.cc: $(GELPIA_UTILS_INC) interface/gelpia_utils.i
	swig $(SWIGFLAGS) -o generated/gelpia_utils_wrap.cc interface/gelpia_utils.i

# 2. compile generated file
obj/gelpia_utils_wrap.o: generated/gelpia_utils_wrap.cc
	$(CXX) $(2_FLAGS) -o obj/gelpia_utils_wrap.o generated/gelpia_utils_wrap.cc

# 3. ommited since there is no cc source needed

# 4. combine
bin/_gelpia_utils.so: $(GELPIA_UTILS_OBJ)
	$(CXX) $(4_FLAGS) -o bin/_gelpia_utils.so $(GELPIA_UTILS_OBJ)




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
