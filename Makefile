
export PATH := ${CURDIR}/requirements/bin:${PATH}
export LD_LIBRARY_PATH := ${LD_LIBRARY_PATH}:$(CURDIR)/requirements/lib
export CPLUS_INCLUDE_PATH := ${CPLUS_INCLUDE_PATH}:$(CURDIR)/requirements/include
export LIBRARY_PATH := ${LIBRARY_PATH}:$(CURDIR)/requirements/lib


all: libfunc.so bin/gelpia target/release/coperative


target/release/coperative: src/main.rs
	@cargo build --release

debug: bin/gelpia target/debug/coperative
	@cd src/func && cargo build
	@cp src/func/target/debug/libfunc.so ./

target/debug/coperative: src/main.rs
	@cargo build

bin/gelpia: src/frontend/gelpia
	@cp src/frontend/*.py bin
	@cp src/frontend/gelpia bin

libfunc.so: src/func/src/lib.rs
	@cd src/func && cargo build --release
	@cp src/func/target/release/libfunc.so ./

.PHONY: clean
clean:
	@rm -fr libfunc.so bin/*.py bin/gelpia bin/__pycache__ bin/parser.out
	@cargo clean
	@cd src/func && cargo clean
