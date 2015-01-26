# we need clang > 3.3 for this 
CXX = clang

# directories used
IDIR = include
ODIR = obj
BDIR = bin
TDIR = test
SDIR = src

# c++11 code, catch all warnings as errors
CXXFLAGS += -std=c++11 -Wall -Werror -g -I$(IDIR)

$(ODIR)/serial_global_optimizer.o: $(IDIR)/optimizer_types.h $(SDIR)/serial_global_optimizer.cc $(ODIR)/optimizer_helpers.o
	$(CXX) $(CXXFLAGS) -c $(SDIR)/serial_global_optimizer.cc -o $(ODIR)/serial_global_optimizer.o

$(ODIR)/optimizer_helpers.o: $(IDIR)/optimizer_helpers.h $(SDIR)/optimizer_helpers.cc
	$(CXX) $(CXXFLAGS) -c $(SDIR)/optimizer_helpers.cc -o $(ODIR)/optimizer_helpers.o


.PHONY: clean
clean:
	rm -f $(ODIR)/*.o $(TDIR)/*.tester $(BDIR)/*
