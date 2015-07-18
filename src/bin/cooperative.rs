#![feature(collections)]
// Demo program for cooperative interval branch and bound algorithm.

use std::collections::BinaryHeap;

extern crate rand;
extern crate gu;
extern crate ga;
extern crate gr;

use ga::{ea, Individual};
use gu::{Quple, INF, NINF, Flt, Parameters, max};

use gr::{GI, upper_gaol, lower_gaol, func, midbox_gaol, width_gaol, width_box, split_box};

use std::sync::{Barrier, RwLock, Arc};

use std::sync::atomic::{AtomicBool, Ordering};

use std::thread;

use std::thread::{sleep_ms};

fn ibba(x_0: Vec<GI>, e_x: Flt, e_f: Flt, 
        f_bestag: Arc<RwLock<Flt>>, 
        f_best_shared: Arc<RwLock<Flt>>,
        x_bestbb: Arc<RwLock<Vec<GI>>>,
        b1: Arc<Barrier>, b2: Arc<Barrier>, 
        q: Arc<RwLock<BinaryHeap<Quple>>>, 
        sync: Arc<AtomicBool>, stop: Arc<AtomicBool>) 
        -> (Flt, Vec<GI>) {
    let mut f_best_high = NINF;
    let mut f_best_low  = NINF;
    let mut best_x = x_0.clone();

    let mut i: u32 = 0;
    q.write().unwrap().push(Quple{p: INF, pf: i, data: x_0.clone()});
    while q.read().unwrap().len() != 0 {
        if sync.load(Ordering::SeqCst) {
            // Ugly: Update the update thread's view of the best branch bound.
            *f_best_shared.write().unwrap() = f_best_low;
            b1.wait();
            b2.wait();
        }
        // Take q as writable during an iteration
        let mut q = q.write().unwrap();
        if i % 1000000 == 0 {
            let mut count = 0;
            let mut size = 0.0;
            for g in q.iter() {
                let ref g_d = g.data;
                let mut l_size = 1.0;
                for b in g_d {
                    l_size *= width_gaol(b);
                }
                size += l_size;
                let sup = upper_gaol(&func(&g_d));
                if sup >= f_best_low {
                    count += 1
                }
            }
            size /= q.len() as f64;
            println!("Iteration: {}, Relevant items: {}, low: {:?}, high {}, size: {}", 
                     i, count, f_best_low, f_best_high, size);
        }
        {
            let m = f_bestag.read().unwrap();
            if *m > f_best_low {
                println!("New BB: {:?}", *m);
            }
        }
        f_best_low = max(&[f_best_low, *f_bestag.read().unwrap()]);
        let v = q.pop();
        let ref x =
            match v {
                Some(y) => y.data,
                None    => panic!("wtf")
            };
        let xw = width_box(x);
        let fx = func(x);
        let fw = width_gaol(&fx);

        if upper_gaol(&fx) < f_best_low ||
            xw < e_x ||
            fw < e_f {
                if f_best_high < upper_gaol(&fx) {
                    println!("New max: {:?}", upper_gaol(&fx));
                    f_best_high = upper_gaol(&fx);
                    best_x = x.clone();
                }
                continue;
            }
        else {
            let x_s = split_box(&x);
            for sx in x_s {
                let mid = midbox_gaol(&sx);
                let est_m = func(&mid);
                let est_i = func(&sx);
                let est_max = max(&[lower_gaol(&est_m), lower_gaol(&est_i)]);
                if f_best_low < est_max  {
                    f_best_low = est_max;
                    *x_bestbb.write().unwrap() = sx.clone();
                }
                i += 1;
                q.push(Quple{p: lower_gaol(&est_i),
                             pf: i,
                             data: sx});
            }
        }
    }
    println!("{:?}", i);
    stop.store(true, Ordering::SeqCst);
    (f_best_high, best_x)
}

fn distance(p: &Vec<GI>, x: &Vec<GI>) -> Flt {
    let mut result = 0.0;
    for i in 0..x.len() {
        let dx = max(&[lower_gaol(&x[i]) - lower_gaol(&p[i]),
                       0.0, lower_gaol(&p[i]) - upper_gaol(&x[i])]);
        result += dx*dx;
    }
    result.sqrt()
}

fn update(q: Arc<RwLock<BinaryHeap<Quple>>>, population: Arc<RwLock<Vec<Individual>>>,
          f_best_shared: Arc<RwLock<Flt>>,
          stop: Arc<AtomicBool>, sync: Arc<AtomicBool>,
          b1: Arc<Barrier>, b2: Arc<Barrier>,
          duration: u32) {
    while !stop.load(Ordering::SeqCst) {
        // Timer code...
        thread::sleep_ms(duration);
        // Signal EA and IBBA threads.
        sync.store(true, Ordering::SeqCst);

        // Wait for EA and IBBA threads to stop.
        b1.wait();
        // Do update bizness.
        let mut q_u = q.write().unwrap();
        println!("Start {:?}",q_u.len());
        let mut q = Vec::new();
        for qi in q_u.iter() {
            q.push(qi.clone());
        }
        let mut pop = population.write().unwrap();
        let fbest = f_best_shared.read().unwrap();

        for i in 0..pop.len() {
            let mut d_min = INF;
            let mut j = 0;
            let mut x: Vec<GI>;
            let px: Flt = NINF;
            let mut x_c: Vec<GI> = q[0].data.clone();
            while j < q.len() && d_min != 0.0 {
                assert!(j < q.len(), "1");
                x = q[j].data.clone();
                if upper_gaol(&func(&x)) < *fbest {
                    assert!(j < q.len(), "2");
                    q.remove(j);
                    continue;
                }
                assert!(i < pop.len(), "3");
                let d = distance(&pop[i].solution, &x);
                
                if d == 0.0 {d_min = 0.0; continue;}
                else {
                    if d < d_min {d_min = d; x_c = x.clone();}
                }
                j += 1;
            }
            if d_min == 0.0 { 
                assert!(i < pop.len(), "4");
                let fp = lower_gaol(&func(&pop[i].solution));
                if px < fp {
                    assert!(j < q.len(), "5");
                    q[j] = Quple{p: fp, pf: q[j].pf, 
                                 data: q[j].data.clone()}.clone();
                }
            }
            else {
                // Individual is outside the search region.
                // Project it back into the nearest current search space.
                assert!(i < pop.len(), "6");
                project(&mut pop[i], &x_c);
            }
        }
        // Restore the q for the ibba thread.
        (*q_u) = BinaryHeap::from_vec(q);
        println!("Done {:?}",q_u.len());
        // Clear sync flag.
        sync.store(false, Ordering::SeqCst);
        
        // Resume EA and IBBA threads.
        b2.wait();
    }
}

/* Projects the box x into the box x_c */
fn project(p: &mut Individual, x_c: &Vec<GI>) {
    for i in 0..x_c.len() {
        if lower_gaol(&p.solution[i]) < lower_gaol(&x_c[i])
            || lower_gaol(&p.solution[i]) > upper_gaol(&x_c[i]) {
            if upper_gaol(&x_c[i]) < lower_gaol(&p.solution[i]) 
                {p.solution[i] = GI::new_d(upper_gaol(&x_c[i]),
                                           upper_gaol(&x_c[i]));}
            else {p.solution[i] = GI::new_d(lower_gaol(&x_c[i]),
                                            lower_gaol(&x_c[i]));}
        }
    }
    p.fitness = lower_gaol(&func(&p.solution));
}


fn main() {
    let q_inner: BinaryHeap<Quple> = BinaryHeap::new();
    let q = Arc::new(RwLock::new(q_inner));
    
    let population_inner: Vec<Individual> = Vec::new();
    let population = Arc::new(RwLock::new(population_inner));

    let b1 = Arc::new(Barrier::new(3));
    let b2 = Arc::new(Barrier::new(3));
    
    let sync = Arc::new(AtomicBool::new(false));
    let stop = Arc::new(AtomicBool::new(false));

    let f_bestag: Arc<RwLock<Flt>> = Arc::new(RwLock::new(NINF));
    let f_best_shared: Arc<RwLock<Flt>> = Arc::new(RwLock::new(NINF));
    
    let x_0 = vec![GI::new("-1", "1.0"),
                   GI::new("1.0e-5", "1.0"),
                   GI::new("1.0e-5", "1.0")];
    let x_i = x_0.clone();

    let x_e = x_0.clone();
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
        thread::Builder::new().name("IBBA".to_string()).spawn(move || {
            ibba(x_i, 0.0001, 0.0001,
                 f_bestag, f_best_shared,
                 x_bestbb,
                 b1, b2, q, sync, stop)
        })};

    let ea_thread = 
    {
        let population = population.clone();
        let f_bestag = f_bestag.clone();
        let x_bestbb = x_bestbb.clone();
        let sync = sync.clone();
        let stop = stop.clone();
        let b1 = b1.clone();
        let b2 = b2.clone();
        thread::Builder::new().name("EA".to_string()).spawn(move || {
            ea(x_e, Parameters{population: 1000,
                               selection: 4,
                               elitism: 2,
                               mutation: 0.3_f64,
                               crossover: 0.5_f64},
               population, 
               f_bestag, 
               x_bestbb,
               b1, b2,
               stop, sync)
        })};

    let update_thread = 
    {
        let q = q.clone();
        let population = population.clone();
        let f_best_shared = f_best_shared.clone();
        let sync = sync.clone();
        let stop = stop.clone();
        let b1 = b1.clone();
        let b2 = b2.clone();
        thread::Builder::new().name("Update".to_string()).spawn(move || {
            update(q, population, f_best_shared,
                   stop, sync, b1, b2, 10000)
        })};

    let result = ibba_thread.unwrap().join();
    // Join EA and Update here pending stop signaling.
    if result.is_ok() {
        let (max, interval) = result.unwrap();
        println!("{}", max);
        for x in interval {
            println!("{}", x.to_string());
        }
        
    }
    else {println!("error")}
}
