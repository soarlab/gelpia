extern crate gr;
use gr::*;

#[no_mangle]
pub extern "C"
fn gelpia_func(_x: &Vec<GI>, _c: &Vec<GI>) -> GI {
    _x[0]
}
