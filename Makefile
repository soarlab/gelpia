all: libfunc.so bin/gelpia;

bin/gelpia:
	cp src/frontend/*.py bin
	cp src/frontend/gelpia bin

libfunc.so: src/func/src/lib.rs
	@cd src/func && cargo build --release --verbose
	@cp src/func/target/release/libfunc.so ./

.PHONY: clean
clean:
	@rm -f libfunc.so bin/*.py bin/gelpia
