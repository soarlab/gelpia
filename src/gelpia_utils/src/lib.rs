/* 
Basic interval implementation and other common functions/data structures
 */
#![feature(float_extras)]

// External libraries
use std::cmp::{PartialOrd, Ordering, PartialEq, Ord};
use std::f64::{NEG_INFINITY, INFINITY};

// Internal libraries
extern crate gr;
use gr::GI;

// Datatypes
pub type Flt = f64;
pub static INF:  Flt = INFINITY;
pub static NINF: Flt = NEG_INFINITY;

#[macro_export]
macro_rules! max {
    ($x:expr) => {{ $x }};
    ($x:expr, $($y:expr),* ) => {{
        let mut max = $x;
        $(
            max = if max > $y {max} else {$y};
        )*
            max
    }}
}

#[macro_export]
macro_rules! min {
    ($x:expr) => {{ $x }};
    ( $x:expr, $($y:expr),*) => {{
        let mut min = $x;
        $(
            min = if min < $y {min} else {$y};
        )*
            min
    }}
}


// Evolutionary algo
#[derive(Debug, Copy, Clone)]
pub struct Parameters {
    pub population:usize,
    pub selection: usize,
    pub elitism:   usize,
    pub mutation:    Flt,
    pub crossover:   Flt,
    pub seed:        u32,
}
// Evolutionary algo end

// Quple 
// Data structure for insertion of a box into a priority queue
#[derive(Clone)]
pub struct Quple {
    pub p: Flt,
    pub pf: u32,
    pub data: Vec<GI>,
    pub fdata: GI
}

// Allow ordering of Quples
impl PartialEq for Quple {
    fn eq(&self, other: &Quple) -> bool {
        if self.pf == other.pf &&
            self.p == other.p {
                return true;
            }
        return false;
    }
}

impl Eq for Quple { }

impl PartialOrd for Quple {
    fn partial_cmp(&self, other: &Quple) -> Option<Ordering> {
        // This element is greater than the other element
        if self.pf < other.pf {
            return Some(Ordering::Greater);
        }
        else if self.pf == other.pf {
            return self.p.partial_cmp(&other.p);
        }
        else {
            return Some(Ordering::Less);
        }
    }
}

impl Ord for Quple {
    fn cmp(&self, other: &Quple) -> Ordering {
        if self.pf < other.pf {
            return Ordering::Greater;
        }
        else if self.pf == other.pf {
            if self.p > other.p {
                return Ordering::Greater;
            }
            else if self.p == other.p {
                return Ordering::Equal;
            }
            else {
                return Ordering::Less;
            }
        }
        else {
            return Ordering::Less;
        }
    }
}
// End Quple ordering.
// End Quple

pub fn eps_tol(fx: GI, est: f64, e_f: f64, e_f_r: f64) -> bool {
    (fx.upper() - est).abs() <= e_f_r*est +  e_f
}

pub fn printerval(input: &Vec<GI>) -> () {
    print!("[");
    for i in 0..input.len() {
        print!("{}", input[i].to_string());
        if i < input.len() - 1 {
            print!(", ");
        }
    }
    println!("]");
}
