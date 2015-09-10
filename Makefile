libfunc.so: src/func/src/lib.rs
	@./build.sh
	@cp src/func/target/release/libfunc.so ./

clean:
	@rm -f libfunc.so
