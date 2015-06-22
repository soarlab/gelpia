use std::ops::{Add, Sub, Mul, Div, Neg};
use std::cmp::{PartialOrd, Ordering, PartialEq, Ord};
use std::collections::BinaryHeap;

#[derive(Debug, Copy, Clone)]
struct Interval {
    inf: f64,
    sup: f64,
}

impl Interval {
    fn new(inf: f64,
           sup: f64) -> Interval{
        if inf > sup {
            panic!("Improper interval");
        }
        Interval{inf: inf, sup: sup}
    }
}

struct Quple {
    p: f64,
    pf: u32,
    data: Vec<Interval>,
}

impl PartialEq for Quple {
    fn eq(&self, other: &Quple) -> bool {
        self.pf == other.pf
    }
}

impl Eq for Quple { }

impl PartialOrd for Quple {
    fn partial_cmp(&self, other: &Quple) -> Option<Ordering> {
        if self.p > other.p {
            Some(Ordering::Greater)
        }
        else if self.pf > other.pf {
            Some(Ordering::Greater)
        }
        else {
            Some(Ordering::Less)
        }
    }
}

impl Ord for Quple {
    fn cmp(&self, other: &Quple) -> Ordering {
        if self.p > other.p {
            Ordering::Greater
        }
        else if self.pf > other.pf {
            Ordering::Greater
        }
        else if self.pf == other.pf {
            Ordering::Equal
        }
        else {
            Ordering::Less
        }
    }
}

impl Add for Interval {
    type Output = Interval;
    
    fn add(self, other: Interval) -> Interval {
        Interval::new(self.inf + other.inf,
                      self.sup + other.sup)
    }
}

impl Sub for Interval {
    type Output = Interval;
    
    fn sub(self, other: Interval) -> Interval {
        Interval::new(self.inf - other.sup,
                      self.sup - other.inf)
    }
}

impl Mul for Interval {
    type Output = Interval;
    
    fn mul(self, other: Interval) -> Interval {
        let a = self.inf;
        let b = self.sup;
        let c = other.inf;
        let d = other.sup;
        let ac = a*c;
        let ad = a*d;
        let bc = b*c;
        let bd = b*d;
        Interval::new(min(&[ac, ad, bc, bd]),
                      max(&[ac, ad, bc, bd]))
    }
}

impl Div for Interval {
    type Output = Interval;
    
    fn div(self, other: Interval) -> Interval {
        let a = self.inf;
        let b = self.sup;
        let c = other.inf;
        let d = other.sup;
        let ac = a/c;
        let ad = a/d;
        let bc = b/c;
        let bd = b/d;
        Interval::new(min(&[ac, ad, bc, bd]),
                      max(&[ac, ad, bc, bd]))
    }
}

impl Neg for Interval {
    type Output = Interval;

    fn neg(self) -> Interval {
        Interval::new(-self.sup,
                      -self.inf)
    }
}

fn min(args: &[f64]) -> f64 {
    let mut min = std::f64::INFINITY;
    for &arg in args {
        if arg < min {
            min = arg;
        }
    }
    min
}

fn abs(i: Interval) -> Interval {
    if i.inf >= 0.0 { // Interval is already positive
        i
    }
    else if i.sup <= 0.0 { // Interval is completely negative
        Interval::new(-i.sup, -i.inf)
    }
    else { // Otherwise interval spans 0.
        Interval::new(0.0, max(&[-i.inf, i.sup]))
    }
}

fn max(args: &[f64]) -> f64 {
    let mut max = std::f64::NEG_INFINITY;
    for &arg in args {
        if arg > max {
            max = arg;
        }
    }
    max
}

fn pow_d(a: f64, b: u32) -> f64 {
    if b == 0 {
        1.0
    }
    else if b == 1 {
        a
    }
    else {
        let mut result;
        let half_pow = pow_d(a, b/2);
        if b%2 == 1 {
            result = half_pow * half_pow*a;
        }
        else {
            result = half_pow*half_pow;
        }
        result
    }
}

fn pow(a: Interval, b: u32) -> Interval {
    if b % 2 == 1 {
        Interval::new(pow_d(a.inf, b), pow_d(a.sup, b))
    }
    else {
        if a.inf >= 0.0 {
            Interval::new(pow_d(a.inf, b), pow_d(a.sup, b))                
        }
        else if a.sup < 0.0 {
            Interval::new(pow_d(a.sup, b), pow_d(a.inf, b))
        }
        else {
            Interval::new(0.0, max(&[pow_d(a.inf, b),
                                     pow_d(a.sup, b)]))
        }
    }
}

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

fn width(i: &Interval) -> f64 {
    let w = i.sup - i.inf;
    if w < 0.0 {
        -w
    }
    else {
        w
    }
}

fn width_box(x: &Vec<Interval>) -> f64 {
    let mut result = std::f64::NEG_INFINITY;
    for i in x {
        let w = width(i);
        if w > result {
            result = w;
        }
    }
    result
}

fn split(x: &Vec<Interval>) -> Vec<Vec<Interval>> {
    let mut widest = std::f64::NEG_INFINITY;
    let mut idx = -1;
    for i in (0..x.len()) {
        let w = width(&x[i]);
        if w > widest {
            widest = w;
            idx = i;
        }
    }
    
    let mid = (x[idx].inf +x[idx].sup)/2.0;
    
    let mut result = vec![x.clone(), x.clone()];
    result[0][idx].sup = mid;
    result[1][idx].inf = mid;
    result
}

fn midpoint(x: &Vec<Interval>) -> Vec<Interval> {
    let mut result = Vec::new();
    for i in x {
        let mid = (i.inf + i.sup)/2.0;
        result.push(Interval::new(mid,
                                  mid));
    }
    result
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
