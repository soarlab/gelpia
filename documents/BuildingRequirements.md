If the automatic requirements script does not work for your particular
system submit a bug to the git, until that is resolved use this as a
guide for installing requirements by hand.


# Rust
A nightly build must be used, which can be found at:
  [https://www.rust-lang.org/downloads.html](https://www.rust-lang.org/downloads.html)
Under the nightly section.
Untar and cd to the source directory.
Run:

    ./install.sh --prefix=<where you want rust>

Make sure you have the location of the install bin directory in your `PATH`.
Also set it in your shell's configuration file.


# crlibm
The most recent version of crlibm can be found at:
[http://lipforge.ens-lyon.fr/projects/crlibm](http://lipforge.ens-lyon.fr/projects/crlibm)
Untar and cd to the source directory.
Run:

    export CFLAGS=-fPIC $CFLAGS
    export LDFLAGS=-fPIC $LDFLAGS
    ./configure --enable-sse2 --prefix=<where you want crlibm>
    make
    make install

Make sure you have the location of the install lib directory in your `LIBRARY_PATH` and 
the install include directory in your `C_INCLUDE_PATH` and `CPLUS_INCLUDE_PATH`.
Also set them in your shell's configuration file.


# Gaol
For gaol to work you must first have crlibm.
The most recent version of gaol can be found at:
[http://sourceforge.net/projects/gaol/](http://sourceforge.net/projects/gaol/)
Untar and cd to the source directory.
Apply gaol-4.2.0.patch from gelpia/documents:

    patch -p0 < <gelpia git location>/documents/gaol-4.2.0.patch

Run:

    ./configure  --with-mathlib=crlibm --enable-simd --disable-debug \
                 --disable-preserve-rounding --enable-optimize \
                 --disable-verbose-mode --prefix=<where you want gaol>
    make
    make install

Make sure you have the location of the install lib directory in
your `LD_LIBRARY_PATH` and `LIBRARY_PATH` as well as the install
include directory in your `CPLUS_INCLUDE_PATH`.
Also set them in your shell's configuration file.
