
export PATH := ${CURDIR}/requirements/bin:${PATH}
export LD_LIBRARY_PATH := $(CURDIR)/requirements/lib:${LD_LIBRARY_PATH}
export CPLUS_INCLUDE_PATH := $(CURDIR)/requirements/include:${CPLUS_INCLUDE_PATH}
export LIBRARY_PATH := $(CURDIR)/requirements/lib:${LIBRARY_PATH}


all: bin/gelpia src/func/comp_comm.sh
	@cargo build --release

debug: bin/gelpia
	@cargo build
	@cd src/func && cargo build
	@cp src/func/target/debug/libfunc.so ./


bin/gelpia: src/frontend/gelpia
	@cp src/frontend/*.py bin
	@cp src/frontend/gelpia bin

src/func/comp_comm.sh: src/func/src/lib_fillin.rs
	@cd src/func/ && ./make_command

.PHONY: clean
clean:
	@rm -fr libfunc.so bin/*.py bin/gelpia bin/__pycache__ bin/parser.out
	@cargo clean
	@rm -fr .compiled
	@rm -f src/func/comp_comm.sh
	@cd src/func && cargo clean
