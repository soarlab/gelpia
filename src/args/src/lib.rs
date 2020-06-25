// External libraries
use std::env;
use std::io::{self};

extern crate getopts;
use getopts::Options;

// Internal libraries
extern crate gr;
use gr::GI;

extern crate function;
use function::FuncObj;

// Datatypes
pub struct Args {
    pub domain: Vec<GI>,
    pub function: FuncObj,
    pub x_error: f64,
    pub y_error: f64,
    pub y_error_rel: f64,
    pub dreal_error: f64,
    pub dreal_error_rel: f64,
    pub timeout: u32,
    pub update_interval: u32,
    pub iters: u32,
    pub names: Vec<String>,
    pub func_suffix: String,
    pub logging: bool,
    pub seed: u32,
    pub smt2: String,
}




// Transforms the standardized string representation of the constants list
//     into a vector of intervals
fn parse_constants(consts: &String)
               -> Vec<GI> {
    let mut result = vec![];
    for inst in consts.split('|') {
        if inst == "" {
            continue;
        }
        result.push(GI::new_c(inst).unwrap());
    }
    result
}


// Transforms the standardized string representation of the free variables list
//     into a vector of string
fn parse_names(names: &String)
              -> Vec<String> {
    let mut result = vec![];
    for n in names.split(',') {
        if n == "" {
            continue;
        }
        result.push(n.to_string());
    }
    result
}




// Processes the arguments given our executable
pub fn process_args() -> Args {
    let mut opts = Options::new();

    // Required
    opts.reqopt("S", "func-suffix", "", "");
//    opts.reqopt("c", "constants", "", "");
//    opts.reqopt("f", "function", "", "");
//    opts.reqopt("i", "input", "", "");
    opts.reqopt("x", "x_epsilon", "", "");
    opts.reqopt("y", "y_epsilon", "", "");
//    opts.reqopt("n", "names", "", "");
    opts.reqopt("r", "y_epsilon_relative", "", "");

    opts.reqopt("Y", "dreal_epsilon", "", "");
    opts.reqopt("R", "dreal_epsilon_relative", "", "");

    // Optional
    opts.optopt("t", "time_out", "", "");
    opts.optopt("M", "max_iters", "", "");
    opts.optopt("u", "update", "", "");
    opts.optflag("d", "debug", "Enable debugging");
    opts.optflag("L", "logging", "Enable maximum logging to stderr");
    opts.optopt("s", "seed", "Seed to use for random number generators", "");

    // Check that the args are there
    let args: Vec<String> = env::args().collect();
    let matches = match opts.parse(&args[1..]) {
        Ok(m) => m,
        Err(f) => {panic!(f.to_string())}
    };

    // Grab out the required arguments
    let mut input_string = String::new();
    io::stdin().read_line(&mut input_string).unwrap();
    input_string.pop();
    // let input_string = matches.opt_str("i").unwrap();
    //println!("debug: inputs: '{}'", input_string);
    let x_0 = parse_constants(&input_string);

    let mut names_string = String::new();
    io::stdin().read_line(&mut names_string).unwrap();
    names_string.pop();
    // let names_string = matches.opt_str("n").unwrap();
    //println!("debug: names: '{}'", names_string);
    let names = parse_names(&names_string);

    let mut const_string = String::new();
    io::stdin().read_line(&mut const_string).unwrap();
    const_string.pop();
    // let const_string = matches.opt_str("c").unwrap();
    //println!("debug: consts: '{}'", const_string);
    let consts = parse_constants(&const_string);

    let func_suffix = matches.opt_str("S").unwrap();
    let mut func_string = String::new();
    io::stdin().read_line(&mut func_string).unwrap();
    func_string.pop();
    // let func_string = matches.opt_str("f").unwrap();
    let debug = matches.opt_present("d");
    let logging = matches.opt_present("L");
    //println!("debug: function: '{}'", func_string);
    let fo = FuncObj::new(&consts, &func_string, debug, func_suffix.clone());


    let mut smt2_string = String::new();
    io::stdin().read_line(&mut smt2_string).unwrap();
    smt2_string.pop();

    // Grab out optional arguments
    let to = if matches.opt_present("t") {
        matches.opt_str("t").unwrap().parse::<u32>().unwrap()
    } else {
        0 as u32
    };

    let seed = if matches.opt_present("s") {
        matches.opt_str("seed").unwrap().parse::<u32>().unwrap()
    } else {
        0 as u32
    };

    let ui = if matches.opt_present("u") {
        matches.opt_str("u").unwrap().parse::<u32>().unwrap()
    } else {
        0 as u32
    };

    let a_iters = if matches.opt_present("M") {
        matches.opt_str("M").unwrap().parse::<u32>().unwrap()
    } else {
        0 as u32
    };

    // Return parsed information in a struct
    Args{domain: x_0,
         function: fo,
         x_error: matches.opt_str("x").unwrap().parse::<f64>().unwrap(),
         y_error: matches.opt_str("y").unwrap().parse::<f64>().unwrap(),
         y_error_rel: matches.opt_str("r").unwrap().parse::<f64>().unwrap(),
         dreal_error: matches.opt_str("Y").unwrap().parse::<f64>().unwrap(),
         dreal_error_rel: matches.opt_str("R").unwrap().parse::<f64>().unwrap(),
         timeout: to,
         iters: a_iters,
         names: names,
         update_interval: ui,
         func_suffix: func_suffix,
         logging: logging,
         seed: seed,
         smt2: smt2_string}
}
