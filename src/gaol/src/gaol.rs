#![feature(libc)]

extern crate libc;
use libc::{c_double, c_void, c_char, c_int};
use std::ffi::{CString, CStr};
use std::ops::{Add, Mul, Sub, Div, Neg};

// Structure holding a pointer to a GAOL interval.
#[repr(C)]
pub struct gaol_int {
    pub data: * mut c_void
}

unsafe impl Send for gaol_int {}

unsafe impl Sync for gaol_int {

}
// Functions exported from the C GAOL wrapper.
#[link(name="rustgaol", kind="static")]
#[link(name="gaol", kind="dylib")]
#[link(name="gdtoa", kind="dylib")]
#[link(name="crlibm", kind="dylib")]
extern {
    // All constructors and non inplace functions return an allocated
    // interval. These resources must be freed.

    // Constructs an interval from two doubles
    fn make_interval_dd(a: c_double, b: c_double) -> gaol_int;
    // Constructs an interval from two strings
    fn make_interval_ss(inf: *const c_char,
                        sup: *const c_char) -> gaol_int;
    // Constructs an interval from one string, using the single string 
    // constructor. See the GAOL documentation.
    fn make_interval_s(x: *const c_char) -> gaol_int;
    // Creates a clone of a GAOL interval
    fn make_interval_i(x: gaol_int) -> gaol_int;
    
    // Returns the empty GAOL interval
    fn make_interval_e() -> gaol_int;
    
    // Prints a GAOL interval using C++.
    fn print(a: gaol_int);

    // Deletes a GAOL interval.
    fn del_int(a: gaol_int);
    
    // Returns the sum of a and b as a new interval.
    fn add(a: gaol_int, b: gaol_int) -> gaol_int;
    
    // Returns a = a + b
    fn iadd(a: gaol_int, b:gaol_int) -> gaol_int;
    
    // Returns a - b as a new interval.
    fn sub(a: gaol_int, b: gaol_int) -> gaol_int;
    
    // Returns a = a - b.
    fn isub(a: gaol_int, b: gaol_int) -> gaol_int;
    
    // Returns a * b as a new interval.
    fn mul(a: gaol_int, b: gaol_int) -> gaol_int;
    
    // Returns a = a * b.
    fn imul(a: gaol_int, b: gaol_int) -> gaol_int;
    
    // Returns a / b as a new interval.
    fn div_g(a: gaol_int, b: gaol_int) -> gaol_int;
    
    // Returns a = a / b.
    fn idiv_g(a: gaol_int, b: gaol_int) -> gaol_int;
    
    // Returns -a as a new interval.
    fn neg_g(a: gaol_int) -> gaol_int;
    
    // Returns a = -a.
    fn ineg_g(a: gaol_int) -> gaol_int;
    
    // Returns sin(a) as a new interval.
    fn sin_g(a: gaol_int) -> gaol_int;
    // Returns a = sin(a).
    fn isin_g(a: gaol_int) -> gaol_int;
    // Returns cos(a) as a new interval.
    fn cos_g(a: gaol_int) -> gaol_int;
    // Returns a = cos(a).
    fn icos_g(a: gaol_int) -> gaol_int;
    // Returns tan(a) as a new interval.
    fn tan_g(a: gaol_int) -> gaol_int;
    // Returns a = tan(a).
    fn itan_g(a: gaol_int) -> gaol_int;
    
    // Returns e^a as a new interval.
    fn exp_g(a: gaol_int) -> gaol_int;
    // Returns a = e^a.
    fn iexp_g(a: gaol_int) -> gaol_int;
    
    // Returns ln(a) as a new interval.
    fn log_g(a: gaol_int) -> gaol_int;
    // Returns a = ln(a).
    fn ilog_g(a: gaol_int) -> gaol_int;
    
    // Returns a^b as a new interval.
    fn pow_ig(a: gaol_int, b: c_int) -> gaol_int;
    // Returns a = a^b.
    fn ipow_ig(a: gaol_int, b: c_int) -> gaol_int;
    
    // Returns a^b with b an interval as a new interval.
    fn pow_vg(a: gaol_int, b: gaol_int) -> gaol_int;
    // Returns a = a^b where be is an interval.
    fn ipow_vg(a: gaol_int, b: gaol_int) -> gaol_int;

    // Returns the supremum of a.
    fn upper_g(a: gaol_int) -> c_double;
    // Returns the infimum of a.
    fn lower_g(a: gaol_int) -> c_double;
    // Returns the width of a
    fn width_g(a: gaol_int) -> c_double;
    // Returns the midpoint of a.
    fn midpoint_g(a: gaol_int) -> gaol_int;
    // Sets out_1 and out_2 to two intervals of input split.
    fn split_g(input: gaol_int, out_1: gaol_int, out_2: gaol_int);
    // Returns a string representation of the interval.
    fn to_str(a: gaol_int) -> *const c_char;
}

pub struct GI {
    pub data: gaol_int
}

impl Clone for GI {
    fn clone(&self) -> GI {
        unsafe{GI{data: 
                  make_interval_i(gaol_int{data: 
                                           self.data.data.clone()})}}
    }
}

impl Drop for GI {
    fn drop(&mut self) {
        unsafe{del_int(gaol_int{data: self.data.data.clone()})};
    }
}

impl<'a, 'b> Add<&'a GI> for &'b GI {
    type Output = GI;
    
    fn add(self, other: &'a GI) -> GI {
        let a = gaol_int{data: self.data.data.clone()};
        let b = gaol_int{data: other.data.data.clone()};
        unsafe{GI{data: add(a, b)}}
    }
}

impl<'a, 'b> Sub<&'a GI> for &'b GI {
    type Output = GI;
    
    fn sub(self, other: &'a GI) -> GI {
        let a = gaol_int{data: self.data.data.clone()};
        let b = gaol_int{data: other.data.data.clone()};
        unsafe{GI{data: sub(a, b)}}
    }
}

impl<'a, 'b> Mul<&'a GI> for &'b GI {
    type Output = GI;
    
    fn mul(self, other: &'a GI) -> GI {
        let a = gaol_int{data: self.data.data.clone()};
        let b = gaol_int{data: other.data.data.clone()};
        unsafe{GI{data: mul(a, b)}}
    }
}

impl<'a, 'b> Div<&'a GI> for &'b GI {
    type Output = GI;
    
    fn div(self, other: &'a GI) -> GI {
        let a = gaol_int{data: self.data.data.clone()};
        let b = gaol_int{data: other.data.data.clone()};
        unsafe{GI{data: div_g(a, b)}}
    }
}

impl<'a> Neg for &'a GI {
    type Output = GI;
    
    fn neg(self) -> GI {
        unsafe{
            GI{data: neg_g(gaol_int{data: self.data.data.clone()})}
        }
    }
}

pub fn ineg_gaol<'a>(x: &'a GI) -> &'a GI {
    unsafe{
        ineg_g(gaol_int{data: x.data.data.clone()})};
    x
}

impl GI {
    pub fn new(inf: &str, sup: &str) -> GI{
        GI{data: 
           unsafe{make_interval_ss(CString::new(inf).unwrap().as_ptr(), 
                                   CString::new(sup).unwrap().as_ptr())}}
    }
    
    pub fn new_c(x: &str) -> GI{
        GI{data: 
           unsafe{make_interval_s(CString::new(x).unwrap().as_ptr())}}
    }
    pub fn new_d(inf: f64, sup: f64) -> GI {
        GI{data:
           unsafe{make_interval_dd(inf as c_double, sup as c_double)}}
    }
    pub fn new_e() -> GI {
        GI{data:
           unsafe{make_interval_e()}}
    }

    pub fn split(&self, out1: &mut GI, out2: &mut GI) {
        unsafe{split_g(gaol_int{data: self.data.data.clone()},
                       gaol_int{data: out1.data.data.clone()},
                       gaol_int{data: out2.data.data.clone()})};
    }
}

pub fn sin_gaol(x: &GI) -> GI{
    unsafe{GI{data: 
              sin_g(gaol_int{data: 
                             x.data.data.clone()})}}
}

pub fn isin_gaol<'a>(a: &'a mut GI) -> &'a GI {
    unsafe{isin_g(gaol_int{data: a.data.data.clone()})};
    a
}

pub fn cos_gaol(x: &GI) -> GI{
    unsafe{GI{data: 
              cos_g(gaol_int{data: 
                             x.data.data.clone()})}}
}

pub fn icos_gaol<'a>(a: &'a mut GI) -> &'a GI {
    unsafe{icos_g(gaol_int{data: a.data.data.clone()})};
    a
}

pub fn imul_gaol<'a>(a: &'a mut GI, b: &GI) -> &'a GI{
    unsafe{imul(gaol_int{data: a.data.data.clone()},
                gaol_int{data: b.data.data.clone()})};
    a
}

pub fn iadd_gaol<'a>(a: &'a mut GI, b: &GI) -> &'a GI{
    unsafe{iadd(gaol_int{data: a.data.data.clone()},
                gaol_int{data: b.data.data.clone()})};
    a
}

pub fn isub_gaol<'a>(a: &'a mut GI, b: &GI) -> &'a GI{
    unsafe{isub(gaol_int{data: a.data.data.clone()},
                gaol_int{data: b.data.data.clone()})};
    a
}

pub fn idiv_gaol<'a>(a: &'a mut GI, b: &GI) -> &'a GI{
    unsafe{idiv_g(gaol_int{data: a.data.data.clone()},
                gaol_int{data: b.data.data.clone()})};
    a
}

pub fn tan_gaol(x: &GI) -> GI{
    unsafe{GI{data: 
              tan_g(gaol_int{data: 
                             x.data.data.clone()})}}
}

pub fn itan_gaol<'a>(a: &'a mut GI) -> &'a GI {
    unsafe{itan_g(gaol_int{data: a.data.data.clone()})};
    a
}

pub fn exp_gaol(x: &GI) -> GI{
    unsafe{GI{data: 
              exp_g(gaol_int{data: 
                             x.data.data.clone()})}}
}

pub fn iexp_gaol<'a>(a: &'a mut GI) -> &'a GI {
    unsafe{iexp_g(gaol_int{data: a.data.data.clone()})};
    a
}

pub fn log_gaol(x: &GI) -> GI{
    unsafe{GI{data: 
              log_g(gaol_int{data: 
                             x.data.data.clone()})}}
}

pub fn ilog_gaol<'a>(a: &'a mut GI) -> &'a GI {
    unsafe{ilog_g(gaol_int{data: a.data.data.clone()})};
    a
}

pub fn pow_igaol(x: &GI, y: i32) -> GI{
    unsafe{GI{data: 
              pow_ig(gaol_int{data: 
                             x.data.data.clone()}, y as c_int)}}
}

pub fn ipow_igaol<'a>(x: &'a mut GI, y: i32) -> &'a GI {
    unsafe{ipow_ig(gaol_int{data: x.data.data.clone()}, y as c_int)};
    x
}

pub fn pow_vgaol(x: &GI, y: &GI) -> GI{
    unsafe{GI{data: 
              pow_vg(gaol_int{data: 
                              x.data.data.clone()},
                     gaol_int{data:
                              y.data.data.clone()})}}
}

pub fn ipow_vgaol<'a>(x: &'a mut GI, y: &GI) -> &'a GI {
    unsafe{ipow_vg(gaol_int{data: x.data.data.clone()},
                   gaol_int{data: y.data.data.clone()})};
    x
}




pub fn upper_gaol(x: &GI) -> f64 {
    unsafe{
        upper_g(gaol_int{data: x.data.data.clone()}) as f64 }
}

pub fn lower_gaol(x: &GI) -> f64 {
    unsafe{
        lower_g(gaol_int{data: x.data.data.clone()}) as f64 }
}

pub fn width_gaol(x: &GI) -> f64 {
    unsafe{
        width_g(gaol_int{data: x.data.data.clone()}) as f64 }
}

pub fn width_box(x: &Vec<GI>) -> f64 {
    let mut w = std::f64::NEG_INFINITY;
    for i in 0..x.len() {
        let l_w = width_gaol(&x[i]);
        if l_w > w {
            w = l_w;
        }
    }
    w
}

pub fn midpoint_gaol(x: &GI) -> GI {
    let result = unsafe {
        midpoint_g(gaol_int{data:
                            x.data.data.clone()})}; 
    GI{data: result}
}

pub fn midbox_gaol(x: &Vec<GI>) -> Vec<GI> {
    let mut result = Vec::new();
    for i in 0..x.len() {
        result.push(midpoint_gaol(&x[i]));
    }
    result
}

pub fn print_i(x: &GI) {
    unsafe{print(gaol_int{data: x.data.data.clone()})};
}

impl ToString for GI {
    fn to_string(&self) -> String {
        let x: *const c_char = unsafe {to_str(gaol_int{data: self.data.data.clone()})};
        let y = unsafe { 
            CStr::from_ptr(x).to_bytes()
            };
        let z = String::from_utf8(y.to_vec()).unwrap();
        z
    }
}

pub fn split_box(x: &Vec<GI>) -> Vec<Vec<GI>> {
    let mut widest = std::f64::NEG_INFINITY;
    let mut widest_i = -1;
    for i in 0..x.len() {
        if widest < width_gaol(&x[i]) {
            widest = width_gaol(&x[i]);
            widest_i = i;
        }
    }
    let mut x1 = x.clone();
    let mut x2 = x.clone();
    &x[widest_i].split(&mut x1[widest_i], &mut x2[widest_i]);
    vec![x1, x2]
}

pub fn func(_x: &Vec<GI>) -> GI {
    let mut nthree = GI::new_d(3.0, 3.0);
    let ref m1 = _x[0];
    let ref w1 = _x[1];
    let ref a1 = _x[2];
    let mut a = -m1;
    imul_gaol(&mut a, w1);
    let mut b = a1/w1;
    ipow_igaol(&mut b, 2);
    imul_gaol(&mut nthree, &mut b);
    imul_gaol(&mut a, &mut nthree);
    a
}
