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
// End Quple

pub fn eps_tol(x: f64, y: f64, tol: f64) -> bool {
    let (_,exp_x,_) = x.integer_decode();
    let xe = (2.0f64).powi(exp_x as i32);
    return y - x <= tol.max(xe);
}
