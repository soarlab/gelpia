#![feature(convert)]

extern crate gr;
use gr::*;

enum OpType {
    Func(String),
    Const(usize),
    Var(usize),
    UVar(usize),
    Op(String),
    Pow(i32)
}

struct FuncObj {
    user_vars: Vec<GI>,
    constants: Vec<GI>,
    instructions: Vec<OpType>,
    switched: bool,
    func: Box<fn(&Vec<GI>) -> GI>
}

fn dummy(_x: &Vec<GI>) -> GI {
    GI::new_c("1.0")
}

impl FuncObj {
    pub fn call(&self, _x: &Vec<GI>) -> GI {
        if self.switched {
            func(_x)
        }
        else {
            self.interpreted(_x)
        }
    }
    
    fn interpreted(&self, _x: &Vec<GI>) -> GI {
        let mut stack: Vec<GI> = Vec::new();
        for inst in &self.instructions {
            match inst {
                &OpType::Func(ref s) => {
                    let op = stack.pop().unwrap();
                    let result = match s.as_str() {
                        "abs" => abs(op),
                        "sin" => sin(op),
                        "cos" => cos(op),
                        "tan" => tan(op),
                        "exp" => exp(op),
                        "log" => log(op),
                        "neg" => -op,
                        _     => unreachable!()
                    };
                    stack.push(result);
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
                    let left = stack.pop().unwrap();
                    let result = match s.as_str() {
                        "+" => left + right,
                        "-" => left - right,
                        "*" => left * right,
                        "/" => left / right,
                        "p" => powi(left, right),
                        _   => unreachable!()
                    };
                    stack.push(result);
                },
                &OpType::Pow(exp) => {
                    let arg = stack.pop().unwrap();
                    stack.push(gr::pow(arg, exp));
                }
            }
        }
        stack[0]
    }
    
    fn new(consts: &Vec<GI>, instructions: &String) -> FuncObj {
        let mut insts = vec![];
       
        for inst in instructions.split(',') {
            let mut first = true;
            let mut tmp = "".to_string();
            let mut result = OpType::Const(0);
            for c in inst.to_string().trim().to_string().chars() {
                if first {
                    match c {
                        'c' => {result = OpType::Const(0)},
                        'i' => {result = OpType::Var(0)},
                        'v' => {result = OpType::UVar(0)},
                        'o' => {result = OpType::Op("".to_string())},
                        'f' => {result = OpType::Func("".to_string())},
                        'p' => {result = OpType::Pow(0)},
                        _   => unreachable!()
                    }
                    first = false;
                }
                else {tmp.push(c);}
            }
            insts.push(match result {
                OpType::Const(_) => OpType::Const(tmp.parse::<usize>().unwrap()),
                OpType::Var(_) => OpType::Var(tmp.parse::<usize>().unwrap()),
                OpType::UVar(_) => OpType::UVar(tmp.parse::<usize>().unwrap()),
                OpType::Op(_) => OpType::Op(tmp),
                OpType::Func(_) => OpType::Func(tmp),
                OpType::Pow(_) => OpType::Pow(tmp.parse::<i32>().unwrap()),                
            });
        }
        
        FuncObj{user_vars: vec![],
                constants: consts.clone(),
                instructions: insts,
                switched: false,
                func: Box::new(dummy)}
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
