/*
  Implements the basic IBBA maximization algorithm with a priority queue.
*/

use std::collections::BinaryHeap;

extern crate gu;
use gu::{Quple, INF, NINF, Flt};

extern crate gr;
use gr::{GI, func, width_box, split_box, midpoint_box};

fn ibba(x_0: &Vec<GI>, e_x: Flt, e_f: Flt) -> (Flt, Vec<GI>) {
    let mut f_best_high = NINF;
    let mut f_best_low  = NINF;
    let mut best_x = x_0.clone();
    let mut q = BinaryHeap::new();
    let mut i: u32 = 0;

    q.push(Quple{p: INF, pf: i, data: x_0.clone()});
    while q.len() != 0 {
        let v = q.pop();
        let ref x =
            match v {
                Some(y) 
                    => 
                    y.data,
                None    => panic!("wtf")
            };

        let xw = width_box(x);
        let fx = func(x);
        let fw = fx.width();

        if fx.upper() < f_best_low ||
            xw < e_x ||
            fw < e_f //|| (!contains_zero && !on_boundary)
        {
                if f_best_high < fx.upper() {
                    f_best_high = fx.upper();
                    best_x = x.clone();
                }
                continue;
            }
        else {
            let x_s = split_box(&x);
            for sx in x_s {
                let est = func(&midpoint_box(&sx));
                if f_best_low < est.lower()  {
                    f_best_low = est.lower();
                }
                i += 1;
                q.push(Quple{p: est.upper(),
                             pf: i,
                             data: sx});
            }
        }
    }
    println!("{:?}", i);
    (f_best_high, best_x)
}

fn main() {
    let x_0 = vec![GI::new_ss("-1.0", "1.0"),
                   GI::new_ss("1.0e-5", "1.0"),
                   GI::new_ss("1.0e-5", "1.0")];
    let (max, interval) = ibba(&x_0, 0.0001, 0.0001);
    println!("{:?}", max);
    for x in interval {
        println!("{}", x.to_string());
    }
        
}
