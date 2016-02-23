
export PATH := ${CURDIR}/requirements/bin:${PATH}
export LD_LIBRARY_PATH := $(CURDIR)/requirements/lib:${LD_LIBRARY_PATH}
export CPLUS_INCLUDE_PATH := $(CURDIR)/requirements/include:${CPLUS_INCLUDE_PATH}
export LIBRARY_PATH := $(CURDIR)/requirements/lib:${LIBRARY_PATH}


all: bin/gelpia src/func/comp_comm.sh
	@cargo build --release

debug: bin/gelpia src/func/comp_comm.sh
	@cargo build

bin/gelpia: src/frontend/gelpia
	@cp src/frontend/*.py bin
	@cp src/frontend/gelpia bin

src/func/comp_comm.sh: src/func/src/lib_fillin.rs
	@cd src/func/ && ./make_command
	@mkdir -f .compiled

.PHONY: clean
clean:
	$(RM) libfunc.so 
	$(RM) bin/*.py 
	$(RM) bin/gelpia 
	$(RM) bin/parser.out
	$(RM) -r  bin/__pycache__ 
	cargo clean
	$(RM) -r .compiled
	$(RM) src/func/comp_comm.sh
	cd src/func && cargo clean


.PHONY: requirements
requirements: requirements/build.sh
	cd requirements && ./build.sh


.PHONY: clean-requirements
clean-requirements:
	$(RM) -r requirements/bin
	$(RM) -r requirements/etc
	$(RM) -r requirements/include
	$(RM) -r requirements/lib
	$(RM) -r requirements/share
	$(RM) -r requirements/Sources