#![feature(str_split_at)]
#![feature(convert)]
#![feature(dynamic_lib)]
#![feature(asm)]
#![feature(core_simd)]
#![feature(dynamic_lib)]
use std::dynamic_lib::DynamicLibrary;
use std::path::Path;
use std::mem::transmute;

use std::env;
use std::process::Command;
use std::thread;

extern crate gr;
use gr::*;

use std::sync::atomic::{AtomicBool, Ordering, AtomicPtr, AtomicUsize};
use std::option::Option;
use std::simd;
use std::sync::{Arc, RwLock};
use std::fmt;
use std::io::Write;



#[derive(Clone)]
enum OpType {
    Func(String),
    Const(usize),
    Var(usize),
    UVar(usize),
    Op(String),
    Pow(i32)
}

impl fmt::Display for OpType {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        
        let outstring = match self {
            &OpType::Func(ref s) => format!("f{}", s),
            &OpType::Const(i) => format!("c{}", i),
            &OpType::Var(i) => format!("i{}", i),
            &OpType::UVar(i) => format!("v{}", i),
            &OpType::Op(ref s) => format!("o{}", s),
            &OpType::Pow(i) => format!("p{}", i)
        };
        write!(f, "{}", outstring)
    }
    
}

#[derive(Clone)]
pub struct FuncObj {
    handle: Arc<RwLock<Option<DynamicLibrary>>>,
    user_vars: Vec<GI>,
    constants: Vec<GI>,
    instructions: Vec<OpType>,
    switched: Arc<AtomicBool>,
    function: Arc<AtomicPtr<fn(&Vec<GI>, &Vec<GI>) -> GI>>,

}

unsafe impl Sync for FuncObj {}
unsafe impl Send for FuncObj {}
fn dummy(_x: &Vec<GI>, _c: &Vec<GI>) -> GI {
    GI::new_c("1.0")
}

impl FuncObj {
    pub fn call(&self, _x: &Vec<GI>) -> GI {
        if self.switched.load(Ordering::Acquire) {
            let result = unsafe{
                std::mem::transmute::<*mut fn(&Vec<GI>, &Vec<GI>)->GI,
                                               fn(&Vec<GI>, &Vec<GI>)->GI>(
                    (self.function.load(Ordering::Acquire)))(_x, &self.constants)};
            let mut interim: std::simd::f64x2;
            // The compiler doesn't seem to be generating the code here to
            // retrieve the return value. This gets the result from the xmm0
            // register and returns it to the caller.
            unsafe{asm!("movapd %xmm0, $0"
                        : "=x"(interim)
                        : : :)};
            let test_var = GI{data:
                              gaol_int{data:
                                       interim
                              }};
            test_var
        }
        else {
            self.interpreted(_x, &self.constants)
        }
    }

    fn set(&self, f: fn(&Vec<GI>,&Vec<GI>) -> GI, handle: DynamicLibrary) {
        // This FuncObj owns the handle from the dynamic lib as the lifetime of
        // f is tied to the lifetime of the handle.
        self.function.store(unsafe{std::mem::transmute::<fn(&Vec<GI>, &Vec<GI>)->GI,
                                                         *mut fn(&Vec<GI>, &Vec<GI>)->GI>(f)}, Ordering::Release);
        let mut h = self.handle.write().unwrap();
        *h = Some(handle);
        self.switched.store(true, Ordering::Release);
    }
    
    fn interpreted(&self, _x: &Vec<GI>, _c: &Vec<GI>) -> GI {
        let mut stack: Vec<GI> = Vec::new();
        for inst in &self.instructions {
            match inst {
                &OpType::Func(ref s) => {
                    let op = stack.last_mut().unwrap();
                    match s.as_str() {
                        "abs" => op.abs(),
                        "sin" => op.sin(),
                        "cos" => op.cos(),
                        "tan" => op.tan(),
                        "exp" => op.exp(),
                        "log" => op.log(),
                        "neg" => op.neg(),
                        "sqrt" => op.sqrt(),
                        _     => unreachable!()
                    };
                },
                &OpType::Const(i) => {
                    stack.push(self.constants[i]);
                },
                &OpType::Var(i) => {
                    stack.push(_x[i]);
                },
                &OpType::UVar(i) => {
                    stack.push(self.user_vars[i]);
                },
                &OpType::Op(ref s) => {
                    let right = stack.pop().unwrap();
                    let left = stack.last_mut().unwrap();
                    match s.as_str() {
                        "+" => left.add(right),
                        "-" => left.sub(right),
                        "*" => left.mul(right),
                        "/" => left.div(right),
                        "p" => left.powi(right),
                        _   => unreachable!()
                    };
                },
                &OpType::Pow(exp) => {
                    let arg = stack.last_mut().unwrap();
                    arg.pow(exp);
                }
            }
        }
        stack[0]
    }

    pub fn new(consts: &Vec<GI>, instructions: &String, debug: bool) -> FuncObj {
        let mut insts = vec![];
       
        for inst in instructions.split(',') {
            let dummy = inst.trim().to_string();
            let (first, rest) = dummy.split_at(1);
            insts.push(match first {
                "c" => OpType::Const(rest.to_string().parse::<usize>().unwrap()),
                "i" => OpType::Var(rest.to_string().parse::<usize>().unwrap()),
                "v" => OpType::UVar(rest.to_string().parse::<usize>().unwrap()),
                "o" => OpType::Op(rest.to_string()),
                "f" => OpType::Func(rest.to_string()),
                "p" => OpType::Pow(rest.to_string().parse::<i32>().unwrap()),
                _   => panic!()
            });
        }
        let result =
            FuncObj{handle: Arc::new(RwLock::new(Option::None)),
                user_vars: vec![],
                constants: consts.clone(),
                instructions: insts,
                switched: Arc::new(AtomicBool::new(false)),
                function: Arc::new(AtomicPtr::new(unsafe{std::mem::transmute::<fn(&Vec<GI>, &Vec<GI>)->GI,
                                                                               *mut fn(&Vec<GI>, &Vec<GI>)->GI>(dummy)}))
        };

        {
            let fo_c = result.clone();
            thread::spawn(move || {
                &fo_c.compile(debug);
            })
        };
        result
    }

    fn compile(&self, debug: bool) {
        let mut process = Command::new("/usr/bin/make");
        if debug {
            process.arg("debug");
        }
        let ignore = process.output().unwrap_or_else(|e| {panic!("Could not compile: {}", e)});
        if !ignore.status.success() {                                           
            panic!("Could not compile: {}\n----\n{}", String::from_utf8(ignore.stdout).unwrap(),
                   String::from_utf8(ignore.stderr).unwrap());                  
        }

        DynamicLibrary::prepend_search_path(Path::new("./"));                  
        let f = match DynamicLibrary::open(Some(Path::new("libfunc.so"))) {    
            Ok(lib) => lib,                                                     
            Err(err) => panic!("Could not load library: {}", err)
        };                                                                     
        let g = unsafe{match f.symbol("gelpia_func") {                         
            Ok(func) => transmute::<*mut u32, fn(&Vec<GI>, &Vec<GI>)->GI>(func),
            Err(err) => panic!("Could not load function: {}", err),          
        }};

        self.set(g, f);  
    }
}



#[test]
fn test1() {
    let constants = vec![GI::new_c("1"), GI::new_c("2"), GI::new_c("3")];
    let f = FuncObj::new(&constants,
                         &"c0,c1,o-,c2,o+".to_string());
    let expected = ((GI::new_c("1") - GI::new_c("2")) + GI::new_c("3")).to_string();
    assert!(f.call(&vec![]).to_string() == expected);
}

#[test]
fn test2() {
    let consts = vec![GI::new_c("1"), GI::new_c("2"), GI::new_c("3")];
    let f = FuncObj::new(&consts,
                         &"c0,fsin,c1,o*,fcos,c2,o/".to_string());
    let expected = cos(sin(consts[0]) * consts[1])/consts[2];
    assert!(f.call(&vec![]).to_string() == expected.to_string());
}

#[test]
fn sum_inputs() {
    let consts = vec![];
    let v = vec![GI::new_d(1.0, 1.0), GI::new_d(1.0, 2.0), GI::new_d(1.0, 3.0),
                 GI::new_d(1.0, 4.0), GI::new_d(1.0, 5.0), GI::new_d(1.0, 6.0)];
    let f = FuncObj::new(&consts,
                         &"i0,i1, o+, i2, o+, i3, o+, i4, o+, i5, o+".to_string());
    let expected = (v[0] + v[1] + v[2] + v[3] + v[4] + v[5]).to_string();
    let real = f.call(&v).to_string();
    assert!(real == expected, "real = {}, expected = {}", real, expected);
}

#[test]
fn test3() {
    let consts = vec![GI::new_c("0.1")];
    let v = vec![];
    let f = FuncObj::new(&consts,
                &"c0, fsin".to_string());
    let expected = sin(consts[0]).to_string();
    let real = f.call(&v).to_string();
    assert!(real == expected, "real = {}, expected = {}", real, expected);
}

#[test]
fn test4() {
    let consts = vec![GI::new_c("[-3, 4]")];
    let v = vec![];
    let f = FuncObj::new(&consts,
                &"c0, fabs".to_string());
    let expected = abs(consts[0]).to_string();
    let real = f.call(&v).to_string();
    assert!(real == expected, "real = {}, expected = {}", real, expected);
}

#[test]
fn test5() {
    let consts = vec![GI::new_c("[-3, 4]")];
    let v = vec![];
    let f = FuncObj::new(&consts,
                &"c0, fcos".to_string());
    let expected = cos(consts[0]).to_string();
    let real = f.call(&v).to_string();
    assert!(real == expected, "real = {}, expected = {}", real, expected);
}

#[test]
fn test6() {
    let consts = vec![GI::new_c("[-3, 4]")];
    let v = vec![];
    let f = FuncObj::new(&consts,
                &"c0, ftan".to_string());
    let expected = tan(consts[0]).to_string();
    let real = f.call(&v).to_string();
    assert!(real == expected, "real = {}, expected = {}", real, expected);
}

#[test]
fn test7() {
    let consts = vec![GI::new_c("[-3, 4]")];
    let v = vec![];
    let f = FuncObj::new(&consts,
                &"c0, fexp".to_string());
    let expected = exp(consts[0]).to_string();
    let real = f.call(&v).to_string();
    assert!(real == expected, "real = {}, expected = {}", real, expected);
}

#[test]
fn test8() {
    let consts = vec![GI::new_c("[-3, 4]")];
    let v = vec![];
    let f = FuncObj::new(&consts,
                &"c0, fneg".to_string());
    let expected = (-consts[0]).to_string();
    let real = f.call(&v).to_string();
    assert!(real == expected, "real = {}, expected = {}", real, expected);
}

#[test]
fn test9() {
    let consts = vec![GI::new_c("[0.1, .2]")];
    let v = vec![];
    let f = FuncObj::new(&consts,
                &"c0, flog".to_string());
    let expected = log(consts[0]).to_string();
    let real = f.call(&v).to_string();
    assert!(real == expected, "real = {}, expected = {}", real, expected);
}
#[test]
fn test10() {
    let consts = vec![GI::new_c("[2.0, 3.0]"),
                      GI::new_c("[1.5, 2.5]")];
    let v = vec![];
    let f = FuncObj::new(&consts,
                         &"c0, c1, op".to_string());
    let expected = powi(consts[0], consts[1]).to_string();
    let real = f.call(&v).to_string();
    assert!(real == expected, "real = {}, expected = {}", real, expected);
}
#[test]
fn test_power() {
    let consts = vec![GI::new_c("[2.0, 3.0]"),
                      GI::new_c("[1.5, 2.5]")];
    let v = vec![];
    let f = FuncObj::new(&consts,
                         &"c0, p-1, c1, p2, o+".to_string());
    let expected = (pow(consts[0], -1) + pow(consts[1], 2)).to_string();
    let real = f.call(&v).to_string();
    assert!(real == expected, "real = {}, expected = {}", real, expected);
}
