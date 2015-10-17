all: libfunc.so bin/gelpia;

debug: bin/gelpia
	@cd src/func && cargo build
	@cp src/func/target/debug/libfunc.so ./

bin/gelpia: src/frontend/gelpia
	@cp src/frontend/*.py bin
	@cp src/frontend/gelpia bin

libfunc.so: src/func/src/lib.rs
	@cd src/func && cargo build --release
	@cp src/func/target/release/libfunc.so ./

.PHONY: clean
clean:
	@rm -fr libfunc.so bin/*.py bin/gelpia bin/__pycache__ bin/parser.out
