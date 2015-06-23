//use std::ops::{Add, Sub, Mul, Div, Neg};
//use std::cmp::{PartialOrd, Ordering, PartialEq, Ord};
use std::collections::BinaryHeap;

mod gu;

use gu::{Interval, width, width_box, Quple, split, midpoint, pow, abs};


// Answer: ~500.488
fn func(_x: &Vec<Interval>) -> Interval {
    let x = _x[0];
    let y = _x[1];
    let z = _x[2];
    let a = _x[3];
    let b = _x[4];
    let c = _x[5];
    pow(abs(-y * z - x * a + y * b + z * c - b * c + x * (-x + y + z - a + b + c)), 2)
}

fn ibba(x_0: &Vec<Interval>, e_x: f64, e_f: f64) -> (f64, Vec<Interval>) {
    let mut f_best_high = std::f64::NEG_INFINITY;
    let mut f_best_low  = std::f64::NEG_INFINITY;
    let mut best_x = x_0.clone();
    
    let mut q = BinaryHeap::new();
    let mut i: u32 = 0;

    q.push(Quple{p: std::f64::INFINITY, pf: i, data: x_0.clone()});
    while q.len() != 0 {
        let v = q.pop();
        let ref x =
            match v {
                Some(y) => y.data,
                None    => panic!("wtf")
            };

        let xw = width_box(x);
        let fx = func(x);
        let fw = width(&fx);

        if fx.sup < f_best_low ||
            xw < e_x ||
            fw < e_f {
                if f_best_high < fx.sup {
                    f_best_high = fx.sup;
                    best_x = x.clone();
                }
                continue;
            }
        else {
            let x_s = split(x);
            for sx in x_s {
                let mid = midpoint(&sx);
                let est = func(&mid);
                if f_best_low < est.inf  {
                    f_best_low = est.inf;
                }
                i += 1;
                q.push(Quple{p:est.sup,
                             pf: i,
                             data: sx});
            }
        }
    }
    (f_best_high, best_x)
}

fn main() {
    let bound = Interval::new(-10.0, 10.0);
    let x_0 = vec![bound, bound, bound,
                   bound, bound, bound];
    let (max, interval) = ibba(&x_0, 0.001, 0.001);
    println!("{:?}, {:?}", max, interval)
}
