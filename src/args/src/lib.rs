extern crate gr;
use gr::GI;

extern crate function;
use function::FuncObj;

use std::env;

extern crate getopts;
use getopts::Options;

fn proc_consts(consts: &String) -> Vec<GI> {
    let mut result = vec![];
    for inst in consts.split('|') {
        if inst == "" {
            continue;
        }
        result.push(GI::new_c(inst));
    }
    result
}

pub struct Args {
    pub domain: Vec<GI>,
    pub function: FuncObj,
    pub x_error: f64,
    pub y_error: f64,
    pub timeout: u32,
    pub update_interval: u32,
    pub iters: u64,
    pub names: Vec<String>,
}

fn proc_names(names: &String) -> Vec<String> {
    let mut result = vec![];
    for n in names.split(',') {
        if n == "" {
            continue;
        }
        result.push(n.to_string());
    }
    result
}

pub fn process_args() -> Args {
    let args: Vec<String> = env::args().collect();

    let mut opts = Options::new();
    opts.reqopt("c", "constants", "", "");
    opts.reqopt("f", "function", "", "");
    opts.reqopt("i", "input", "", "");
    opts.optflag("d", "debug", "Enable debugging");
    opts.reqopt("x", "x_epsilon", "", "");
    opts.reqopt("y", "y_epsilon", "", "");
    opts.optopt("t", "time_out", "", "");
    opts.optopt("m", "max_iters", "", "");
    opts.reqopt("n", "names", "", "");
    opts.optopt("u", "update", "", "");
    
    let matches = match opts.parse(&args[1..]) {
        Ok(m) => m,
        Err(f) => {panic!(f.to_string())}
    };
    let const_string = matches.opt_str("c").unwrap();
    let input_string = matches.opt_str("i").unwrap();
    let func_string = matches.opt_str("f").unwrap();
    let name_string = matches.opt_str("n").unwrap();
    
    let x_0 = proc_consts(&input_string.to_string());
    let fo = FuncObj::new(&proc_consts(&const_string.to_string()),
                          &func_string.to_string(), matches.opt_present("d"));

    let mut to = 0 as u32;

    if matches.opt_present("t") {
        to = matches.opt_str("t").unwrap().parse::<u32>().unwrap();
    }
    
    let mut ui = 10 as u32; // Default 10 seconds.

    if matches.opt_present("u") {
        ui = matches.opt_str("u").unwrap().parse::<u32>().unwrap();
    }
    
    let names = proc_names(&name_string);
    Args{domain: x_0, function: fo, x_error: matches.opt_str("x").unwrap().parse::<f64>().unwrap(),
         y_error: matches.opt_str("y").unwrap().parse::<f64>().unwrap(), timeout: to, iters: 0,
         names: names, update_interval: ui}
}
