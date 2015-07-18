// build.rs

extern crate gcc;

fn main() {
    gcc::Config::new()
        .cpp(true)
        .cpp_link_stdlib(Some("stdc++"))
        .flag("-msse3")
        .flag("-O3")
        .flag("-march=native")
        .flag("-lgaol")
        .flag("-lgdtoa")
        .flag("-lcrlibm")
        .file("src/gaol_wrap.cc")
        .compile("librustgaol.a");
}
