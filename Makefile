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

$(BDIR)/_optimizer_helpers.so: $(ODIR)/optimizer_helpers.o $(ODIR)/optimizer_helpers_wrap.o
	$(CXX) -bundle `python3-config --ldflags` $(ODIR)/optimizer_helpers.o $(ODIR)/optimizer_helpers_wrap.o -o $(BDIR)/_optimizer_helpers.so
	mv $(INTDIR)/optimizer_helpers.py $(BDIR)

$(ODIR)/optimizer_helpers.o: $(SDIR)/optimizer_helpers.cc $(INTDIR)/optimizer_helpers_wrap.cc
	$(CXX) $(CXXFLAGS) -c $(SDIR)/optimizer_helpers.cc -o $(ODIR)/optimizer_helpers.o

$(ODIR)/optimizer_helpers_wrap.o: $(SDIR)/optimizer_helpers.cc $(INTDIR)/optimizer_helpers_wrap.cc
	$(CXX) $(CXXFLAGS) `python3-config --cflags` -c $(INTDIR)/optimizer_helpers_wrap.cc -o $(ODIR)/optimizer_helpers_wrap.o

$(INTDIR)/optimizer_helpers_wrap.cc: $(IDIR)/optimizer_types.h $(IDIR)/optimizer_helpers.h $(INTDIR)/optimizer_helpers.i
	swig -c++ -Wall -cppext cc -python -I$(IDIR) $(INTDIR)/optimizer_helpers.i


.PHONY: test
test: $(BDIR)/example_swig.py $(BDIR)/_optimizer_helpers.so
	./$(BDIR)/example_swig.py

$(BDIR)/example_swig.py: $(TDIR)/example_swig.py
	ln -f $(TDIR)/example_swig.py $(BDIR)/example_swig.py

.PHONY: clean
clean:
	rm -f $(ODIR)/*.o $(TDIR)/*.tester $(INTDIR)/*.py $(INTDIR)/*.cc
	rm -rf $(BDIR)/*
