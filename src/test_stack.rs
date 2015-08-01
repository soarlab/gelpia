extern crate gr;
use gr::{GI, func, midpoint_box, pow, powi, sin, cos, tan, exp, log, width_box, split_box};

fn main() {
    let mut result = GI::new_d(0.0, 0.0);
    let v = vec!{GI::new_c("[.999, 1]"),
                 GI::new_c("[1e-5, 1e-4]"),
                 GI::new_c("[.999, 1]")};

    for _ in 0..1000000 {
        result.add(func(&v));
    }
    println!("{}", result.to_string());
}
