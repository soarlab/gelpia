# we need clang > 3.3 for this 
CXX = g++

# directories used
IDIR = include
INTDIR = interface
ODIR = obj
BDIR = bin
TDIR = test
SDIR = src

# c++11 code, catch all warnings as errors
CXXFLAGS += -std=c++11 -Wall -Werror -g -I$(IDIR)

all: $(BDIR)/_optimizer_helpers.so

$(INTDIR)/optimizer_helpers_wrap.cc: $(IDIR)/optimizer_types.h $(IDIR)/optimizer_helpers.h $(INTDIR)/optimizer_helpers.i
	swig -c++ -Wall -cppext cc -python -I$(IDIR) $(INTDIR)/optimizer_helpers.i

$(ODIR)/optimizer_helpers_wrap.o: $(SDIR)/optimizer_helpers.cc $(INTDIR)/optimizer_helpers_wrap.cc
	$(CXX) $(CXXFLAGS) `python-config --cflags` -c $(INTDIR)/optimizer_helpers_wrap.cc -o $(ODIR)/optimizer_helpers_wrap.o

$(ODIR)/optimizer_helpers.o: $(SDIR)/optimizer_helpers.cc $(INTDIR)/optimizer_helpers_wrap.cc
	$(CXX) $(CXXFLAGS) -c $(SDIR)/optimizer_helpers.cc -o $(ODIR)/optimizer_helpers.o

$(BDIR)/_optimizer_helpers.so: $(ODIR)/optimizer_helpers.o $(ODIR)/optimizer_helpers_wrap.o
	$(CXX) -bundle `python-config --ldflags` $(ODIR)/optimizer_helpers.o $(ODIR)/optimizer_helpers_wrap.o -o $(BDIR)/_optimizer_helpers.so
	mv $(INTDIR)/optimizer_helpers.py $(BDIR)

.PHONY: clean
clean:
	rm -f $(ODIR)/*.o $(TDIR)/*.tester $(BDIR)/* $(INTDIR)/*.py $(INTDIR)/*.cc
