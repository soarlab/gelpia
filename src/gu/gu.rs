/* 
  Basic interval implementation and other common functions/data structures
*/

use std::ops::{Add, Sub, Mul, Div, Neg};
use std::cmp::{PartialOrd, Ordering, PartialEq, Ord};
use std::f64::{NEG_INFINITY, INFINITY};

extern crate gr;
use gr::GI;

pub type Box = Vec<Interval>;
pub type Flt = f64;

pub static INF:  Flt = INFINITY;
pub static NINF: Flt = NEG_INFINITY;

//derive(Debug, Copy, Clone)]
//b struct Parameters {                                                         |
//   population: usize,                                                          |
//   selection: usize,                                                           |
//   elitism: usize,                                                             |
//   mutation: Flt,                                                              |
//   crossover: Flt,
//
#[derive(Debug, Copy, Clone)]
pub struct Parameters {
    pub population:usize,
    pub selection: usize,
    pub elitism:   usize,
    pub mutation:    Flt,
    pub crossover:   Flt,
}
// Data structure for insertion of a box into a priority queue
#[derive(Clone)]
pub struct Quple {
    pub p: Flt,
    pub pf: u32,
    pub data: Vec<GI>,
}
// Allow ordering of Quples
impl PartialEq for Quple {
    fn eq(&self, other: &Quple) -> bool {
        self.pf == other.pf
    }
}

impl Eq for Quple { }

impl PartialOrd for Quple {
    fn partial_cmp(&self, other: &Quple) -> Option<Ordering> {
        if self.p < other.p {
            Some(Ordering::Less)
        }
        else if self.pf < other.pf {
            Some(Ordering::Greater)
        }
        else {
            Some(Ordering::Greater)
        }
    }
}

impl Ord for Quple {
    fn cmp(&self, other: &Quple) -> Ordering {
        if self.p < other.p {
            Ordering::Less
        }
        else if self.pf < other.pf {
            Ordering::Greater
        }
        else if self.pf == other.pf {
            Ordering::Equal
        }
        else {
            Ordering::Greater
        }
    }
}
// End Quple ordering.

// Interval implementation
#[derive(Debug, Copy, Clone)]
pub struct Interval {
    pub inf: Flt,
    pub sup: Flt,
}

impl Interval {
    pub fn new(inf: Flt,
               sup: Flt) -> Interval{
        if inf > sup {
            panic!("Improper interval");
        }
        Interval{inf: inf, sup: sup}
    }
    
    pub fn contains(&self, x: Flt) -> bool {
        (x >= self.inf) || (x <= self.sup)
    }
}

// Overloads for arithmetic operators. From wikipedia
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

// Returns the absolute value of an interval
pub fn abs(i: Interval) -> Interval {
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

// Power of an Flt, e.g., a^b
fn pow_d(a: Flt, b: u32) -> Flt {
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

// Power of an interval with bounding optimizations
pub fn pow(a: Interval, b: u32) -> Interval {
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

// Returns the minimum of a slice of Flt
pub fn min(args: &[Flt]) -> Flt {
    let mut min = INFINITY;
    for &arg in args {
        if arg < min {
            min = arg;
        }
    }
    min
}

// Returns the maximum of a slice of Flt
pub fn max(args: &[Flt]) -> Flt {
    let mut max = NEG_INFINITY;
    for &arg in args {
        if arg > max {
            max = arg;
        }
    }
    max
}

// Width of an interval. 
pub fn width(i: &Interval) -> Flt {
    let w = i.sup - i.inf;
    if w < 0.0 {
        -w
    }
    else {
        w
    }
}

// Rerturns the width of the widest interval in the box
pub fn width_box(x: &Box) -> Flt {
    let mut result = NEG_INFINITY;
    for i in x {
        let w = width(i);
        if w > result {
            result = w;
        }
    }
    result
}

// Splits a box in pieces, currently this is at the median of the widest box.
pub fn split(x: &Box) -> Vec<Box> {
    let mut widest = NEG_INFINITY;
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

// Returns the median of the Box. E.g., a box of the midpoints of x.
pub fn midpoint(x: &Box) -> Box {
    let mut result = Vec::new();
    for i in x {
        let mid = (i.inf + i.sup)/2.0;
        result.push(Interval::new(mid,
                                  mid));
    }
    result
}

pub fn func(_x: &Vec<Interval>) -> Interval {
    let nthree = Interval::new(-3.0, -3.0);
    let m1 = _x[0];
    let w1 = _x[1];
    let a1 = _x[2];
    (w1 * -m1) * (nthree * (pow((a1/ w1), 2)))
}   

pub fn func_p(_x: &Vec<Flt>) -> Flt {
    let nthree = -3.0;
    let m1 = _x[0];
    let w1 = _x[1];
    let a1 = _x[2];
    (w1 * -m1) * (nthree * (pow_d((a1/w1), 2)))
}

