// Cooperative optimization solver
use std::collections::BinaryHeap;
use std::io::Write;
use std::process::{Command, Stdio};
extern crate rand;

#[macro_use(max)]
extern crate gelpia_utils;
extern crate gr;

use gelpia_utils::{Quple, NINF, Flt, eps_tol, check_diff};

use gr::{GI, width_box, split_box, midpoint_box};

use std::sync::{Barrier, RwLock, Arc, RwLockWriteGuard};

use std::sync::atomic::{AtomicBool, Ordering};

use std::thread;

//use std::time::Duration;

extern crate function;
use function::FuncObj;

extern crate args;
use args::{process_args};

extern crate time;

/// Returns the guaranteed upperbound for the algorithm
/// from the queue.
fn get_upper_bound(q: &RwLockWriteGuard<BinaryHeap<Quple>>,
                   f_best_high: f64) -> f64{
    let mut max = f_best_high;
    for qi in q.iter() {
        max = max!{max, qi.fdata.upper()};
    }
    max
}

fn log_max(q: &RwLockWriteGuard<BinaryHeap<Quple>>,
           f_best_low: f64,
           f_best_high: f64) {
    let max = get_upper_bound(q, f_best_high);
    let _ = writeln!(&mut std::io::stderr(),
                     "lb: {}, possible ub: {}, guaranteed ub: {}",
                     f_best_low,
                     f_best_high,
                     max);
}

fn check_sat(query: &String,
             names: &Vec<String>,
             inputs: &Vec<GI>,
             abs_tol: Flt,
             rel_tol: Flt) -> bool {
    let mut query_parts = Vec::new();

    for name in names.iter() {
        let decl = format!("(declare-fun {} () Real)", name);
        query_parts.push(decl);
    }

    for (name, input) in names.iter().zip(inputs.iter()) {
        let low_domain = format!("(assert (<= {} {}))", input.lower(), name);
        let high_domain = format!("(assert (<= {} {}))", name, input.upper());
        query_parts.push(low_domain);
        query_parts.push(high_domain);
    }

    query_parts.push(query.to_string());

    let string_query = query_parts.concat();

    let mut child = Command::new("dreal")
        .arg("--in")
        .arg("--nlopt-ftol-abs")
        .arg(if abs_tol == 0.0 {"1e-6".to_string()} else {abs_tol.to_string()})
        .arg("--nlopt-ftol-rel")
        .arg(if rel_tol == 0.0 {"1e-6".to_string()} else {rel_tol.to_string()})
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .spawn()
        .expect("Failed to execute dreal");

    {
    let stdin = child.stdin.as_mut().expect("Failed to open stdin");
    stdin.write_all(string_query.as_bytes()).expect("Failed to write to stdin");
    }

    let output = child.wait_with_output().expect("Failed to read stdout");
    let result = String::from_utf8_lossy(&output.stdout);

    //print!("debug: dreal: {}", result);

    result.contains("delta-sat")
}

#[allow(dead_code)]
fn print_q(q: &RwLockWriteGuard<BinaryHeap<Quple>>) {
    let mut lq: BinaryHeap<Quple> = (*q).clone();
    while lq.len() != 0 {
        let qi = lq.pop().unwrap();
        let (gen, v, _) = (qi.pf, qi.p, qi.fdata);
        print!("[{}, {}, {}], ", v, gen, qi.fdata.to_string());
    }
    println!("\n");
}

/// Returns a tuple (function_estimate, eval_interval)
/// # Arguments
/// * `f` - The function to evaluate with
/// * `input` - The input domain
fn est_func(f: &FuncObj, input: &Vec<GI>) -> (Flt, GI, Option<Vec<GI>>) {
    let mid = midpoint_box(input);
    let (est_m, _) = f.call(&mid);
    let (fsx, dfsx) = f.call(&input);
    let (fsx_u, _) = f.call(&input.iter()
                            .map(|&si| GI::new_p(si.upper()))
                            .collect::<Vec<_>>());
    let (fsx_l, _) = f.call(&input.iter()
                            .map(|&si| GI::new_p(si.lower()))
                            .collect::<Vec<_>>());
    let est_max = est_m.lower().max(fsx_u.lower()).max(fsx_l.lower());
    (est_max, fsx, dfsx)
}

// Returns the upper bound, the domain where this bound occurs and a status
// flag indicating whether the answer is complete for the problem.
fn ibba(x_0: Vec<GI>, e_x: Flt, e_f: Flt, e_f_r: Flt,
        f_bestag: Arc<RwLock<Flt>>,
        _f_best_shared: Arc<RwLock<Flt>>,
        x_bestbb: Arc<RwLock<Vec<GI>>>,
        _b1: Arc<Barrier>, _b2: Arc<Barrier>,
        q: Arc<RwLock<BinaryHeap<Quple>>>,
        _sync: Arc<AtomicBool>, stop: Arc<AtomicBool>,
        f: FuncObj,
        logging: bool, max_iters: u32,
        names: Vec<String>,
        smt2_query: String)
        -> (Flt, Flt, Vec<GI>) {
    let mut best_x = x_0.clone();

    let mut iters: u32 = 0;
    let (est_max, first_val, _) = est_func(&f, &x_0);

    q.write().unwrap().push(Quple{p: est_max, pf: 0, data: x_0.clone(),
                                  fdata: first_val, dfdata: None});
    let mut f_best_low = est_max;
    let mut f_best_high = est_max;

    while q.read().unwrap().len() != 0 && !stop.load(Ordering::Acquire) {
        if max_iters != 0 && iters >= max_iters {
            break;
        }

        // Take q as writable during an iteration
        let mut q = q.write().unwrap();

        let fbl_orig = f_best_low;
        f_best_low = max!(f_best_low, *f_bestag.read().unwrap());

        if iters % 2048 == 0 {
            let guaranteed_bound = get_upper_bound(&q, f_best_high);
            if (guaranteed_bound - f_best_high).abs() < e_f {
                f_best_high = guaranteed_bound;
                break;
            }
        }

        if logging && fbl_orig != f_best_low {
            log_max(&q, f_best_low, f_best_high);
        }

        let (ref x, iter_est, fx, ref dfx, gen) =
            match q.pop() {
                Some(y) => (y.data, y.p, y.fdata, y.dfdata, y.pf),
                None    => unreachable!()
            };

        if check_diff(dfx.clone(), x, &x_0) {
            continue;
        }
        if fx.upper() < f_best_low ||
            width_box(x, e_x) ||
            eps_tol(fx, iter_est, e_f, e_f_r) {
                {
                    if f_best_high < fx.upper() && check_sat(&smt2_query, &names, x, e_f, e_f_r) {
                        f_best_high = fx.upper();
                        best_x = x.clone();
                        if logging {
                            log_max(&q, f_best_low, f_best_high);
                        }
                    }
                    continue;
                }
            }
        else {
            let (x_s, is_split) = split_box(&x);
            for sx in x_s {
                let (est_max, fsx, dfsx) = est_func(&f, &sx);
                if f_best_low < est_max  {
                    f_best_low = est_max;
                    *x_bestbb.write().unwrap() = sx.clone();
                }
                iters += 1;
                if is_split && check_sat(&smt2_query, &names, &sx, e_f, e_f_r) {
                    q.push(Quple{p: est_max,
                                 pf: gen+1,
                                 data: sx,
                                 fdata: fsx,
                                 dfdata:dfsx});
                }
            }
        }
    }
    stop.store(true, Ordering::Release);
    (f_best_low, f_best_high, best_x)
}

fn main() {
    let args = process_args();

    let ref x_0 = args.domain;
    let ref fo = args.function;
    let x_err = args.x_error;
    let y_err = args.y_error;
    let y_rel = args.y_error_rel;
    //let seed = args.seed;

    // Early out if there are no input variables...
    if x_0.len() == 0 {
        let result = fo.call(&x_0).0;
        println!("[[{},{}], {{}}]", result.lower(), result.upper());
        return
    }

    // Early out if the query makes no sense
    if !check_sat(&args.smt2, &args.names, &x_0, y_err, y_rel) {
        println!("Overconstrained");
        return
    }

    let q_inner: BinaryHeap<Quple> = BinaryHeap::new();
    let q = Arc::new(RwLock::new(q_inner));

    let b1 = Arc::new(Barrier::new(3));
    let b2 = Arc::new(Barrier::new(3));

    let sync = Arc::new(AtomicBool::new(false));
    let stop = Arc::new(AtomicBool::new(false));

    let f_bestag: Arc<RwLock<Flt>> = Arc::new(RwLock::new(NINF));
    let f_best_shared: Arc<RwLock<Flt>> = Arc::new(RwLock::new(NINF));

    //let x_e = x_0.clone();
    let x_i = x_0.clone();

    let x_bestbb = Arc::new(RwLock::new(x_0.clone()));

    let ibba_thread =
    {
        let q = q.clone();
        let b1 = b1.clone();
        let b2 = b2.clone();
        let f_bestag = f_bestag.clone();
        let f_best_shared = f_best_shared.clone();
        let x_bestbb = x_bestbb.clone();
        let sync = sync.clone();
        let stop = stop.clone();
        let fo_c = fo.clone();
        let logging = args.logging;
        let iters= args.iters;
        let names = args.names.clone();
        let smt2_query = args.smt2.clone();
        thread::Builder::new().name("IBBA".to_string()).spawn(move || {
            ibba(x_i, x_err, y_err, y_rel,
                 f_bestag, f_best_shared,
                 x_bestbb,
                 b1, b2, q, sync, stop, fo_c, logging, iters, names, smt2_query)
        })};


    let result = ibba_thread.unwrap().join();

    if result.is_ok() {
        let (min, mut max, mut interval) = result.unwrap();
        // Go through all remaining intervals from IBBA to find the true
        // max
        let ref lq = q.read().unwrap();
        for i in lq.iter() {
            let ref top = *i;
            let (ub, dom) = (top.fdata.upper(), &top.data);
            if ub > max {
                max = ub;
                interval = dom.clone();
            }
        }
        println!("[[{},{}], {{", min, max);
        for i in 0..args.names.len() {
            println!("'{}' : {},", args.names[i], interval[i].to_string());
        }
        println!("}}]");

    }
    else {println!("error")}
}
