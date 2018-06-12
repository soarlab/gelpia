
# Set paths to point to locally built requirements first
export PATH := ${CURDIR}/requirements/bin:${PATH}
export LD_LIBRARY_PATH := $(CURDIR)/requirements/lib:${LD_LIBRARY_PATH}
export CPLUS_INCLUDE_PATH := $(CURDIR)/requirements/include:${CPLUS_INCLUDE_PATH}
export LIBRARY_PATH := $(CURDIR)/requirements/lib:${LIBRARY_PATH}

all: bin/gelpia src/func/comp_comm.sh bin/build_func.sh bin/gaol_repl
	@cargo build -q --release
	@cargo build -q

bin/build_func.sh: src/scripts/build_func.sh
	@cp src/scripts/build_func.sh bin/
	@chmod +x bin/build_func.sh

bin/gelpia: src/frontend/gelpia.py src/frontend/*.py src/frontend/function_transforms/*.py bin
	@cp src/frontend/function_transforms/*.py bin
	@cp src/frontend/*.py bin
	@cp src/frontend/gelpia.py bin/gelpia
	@chmod +x bin/gelpia
	@cp src/frontend/gelpia_mm.py bin/gelpia_mm
	@chmod +x bin/gelpia_mm
	@cp src/frontend/gelpia.py bin/dop_gelpia
	@chmod +x bin/dop_gelpia

src/func/comp_comm.sh: src/func/src/lib_fillin.rs
	@cd src/func/ && ./make_command
	@mkdir -p .compiled

bin/gaol_repl: src/gaol_repl.cc
	@${CXX} ${CXXFLAGS} -msse3 -O2 src/gaol_repl.cc -o bin/gaol_repl -lgaol -lcrlibm -lgdtoa


.PHONY: cl
cl: #clean libs
	$(RM) src/func/src/lib_generated_*
	$(RM) -r .compiled
	$(RM) src/func/target/release/*lib_generated_*
	cd src/func && cargo clean

.PHONY: clean
clean: cl
	$(RM) libfunc.so
	$(RM) bin/*.py
	$(RM) bin/gelpia
	$(RM) bin/gelpia_mm
	$(RM) bin/dop_gelpia
	$(RM) bin/build_func.sh
	$(RM) bin/parser.out
	$(RM) -r  bin/__pycache__
	cargo clean
	$(RM) src/func/comp_comm.sh
	$(RM) Cargo.lock
	$(RM) src/func/Cargo.lock
	$(RM) src/gr/Cargo.lock
	$(RM) bin/gaol_repl


.PHONY: requirements
requirements: requirements/build.sh
	@cd requirements && ./build.sh


.PHONY: clean-requirements
clean-requirements:
	$(RM) requirements/build_log.txt
	$(RM) -r requirements/bin
	$(RM) -r requirements/etc
	$(RM) -r requirements/include
	$(RM) -r requirements/lib
	$(RM) -r requirements/share
