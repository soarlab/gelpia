extern crate gr;
use gr::{GI, func, midpoint_box, pow, powi, sin, cos, tan, exp, log, width_box, split_box};

fn main() {
    {
        let a = GI::new_d(1.0, 2.0);
        let b = GI::new_d(3.0, 4.0);
        println!("{}", (a+b).to_string());
        println!("{}", (a-b).to_string());
        println!("{}", (a*b).to_string());
        println!("{}", (a/b).to_string());
        println!("{}", powi(a, b).to_string());
        println!("{}", pow(a, 4).to_string());
    }
    {
        let a = GI::new_d(0.0000001, 1.0);

        println!("{}", sin(a).to_string());
        println!("{}", cos(a).to_string());
        println!("{}", tan(a).to_string());
        println!("{}", (-a).to_string());
        println!("{}", exp(a).to_string());
        println!("{}", log(a).to_string());
    }
    {
        let mut a = GI::new_d(1.0, 2.0);
        let b = GI::new_d(3.0, 4.0);
        println!("Start: a: {}, b: {}", a.to_string(), b.to_string());
        a.add(b);
        println!("Add: a: {}, b: {}", a.to_string(), b.to_string());

        a = GI::new_d(1.0, 2.0);
        a.sub(b);
        println!("Sub: a: {}, b: {}", a.to_string(), b.to_string());

        a = GI::new_d(1.0, 2.0);
        a.mul(b);
        println!("Mul: a: {}, b: {}", a.to_string(), b.to_string());

        a = GI::new_d(1.0, 2.0);
        a.div(b);
        println!("Div: a: {}, b: {}", a.to_string(), b.to_string());
        
        a = GI::new_d(1.0, 2.0);
        a.powi(b);
        println!("Pow: a: {}, b: {}", a.to_string(), b.to_string());

        let exp = 4_i32;
        
        a = GI::new_d(1.0, 2.0);
        a.pow(exp);
        println!("Pow: a: {}, exp: {}", a.to_string(), exp.to_string());


        a = GI::new_d(0.0000001, 1.0);
        
        println!("Start: a: {}", a.to_string());
        a.sin();
        println!("Sin: a: {}", a.to_string());
        
        a = GI::new_d(0.0000001, 1.0);
        a.cos();
        println!("Cos: a: {}", a.to_string());
        
        a = GI::new_d(0.0000001, 1.0);
        a.tan();
        println!("Tan: a: {}", a.to_string());

        a = GI::new_d(0.0000001, 1.0);
        a.neg();
        println!("Neg: a: {}", a.to_string());

        a = GI::new_d(0.0000001, 1.0);
        a.exp();
        println!("Exp: a: {}", a.to_string());
        
        a = GI::new_d(0.0000001, 1.0);
        a.log();
        println!("Log: a: {}", a.to_string());

        a = GI::new_d(0.0000001, 1.0);
        println!("Width: a: {}", a.width());
        
        a = GI::new_d(0.0000001, 1.0);
        println!("Lower: a: {}", a.lower());
        
        a = GI::new_d(0.0000001, 1.0);
        println!("Upper: a: {}", a.upper());        
    }

    let v = vec![GI::new_d(1.0, 2.0), GI::new_d(1.0, 3.0), GI::new_d(1.0, 3.0)];
    println!("{}", width_box(&v));
    let s = split_box(&v);
    let m = midpoint_box(&v);

    println!("split");
    for si in s {
        println!("--------------");
        for sii in si {
            println!("{}", sii.to_string());
        } 
    }
    println!("mid");
    for mi in m {
        println!("{}", mi.to_string()); 
    }
    
    println!("func");
    println!("{}", func(&v).to_string()); 
    
}
