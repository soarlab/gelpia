use std::sync::{Barrier, RwLock, Arc, RwLockWriteGuard};
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::atomic::Ordering as AtOrd;
extern crate rand;
//use rand::{ThreadRng, Rng};
use rand::{Rng, SeedableRng, StdRng};
use rand::distributions::{IndependentSample, Range};


extern crate gr;
use gr::{GI, width_box, split_box, midpoint_box, eps_tol};

extern crate gelpia_utils;
use gelpia_utils::{Quple, INF, NINF, Flt, Parameters};

extern crate function;
use function::FuncObj;


#[derive(Clone)]
pub struct Individual {
    pub solution: Vec<GI>,
    pub fitness: Flt,
}


pub fn ea(x_e: Vec<GI>,
          param: Parameters,
          population: Arc<RwLock<Vec<Individual>>>,
          f_bestag: Arc<RwLock<Flt>>,
          x_bestbb: Arc<RwLock<Vec<GI>>>,
          b1: Arc<Barrier>,
          b2: Arc<Barrier>,
          stop: Arc<AtomicBool>,
          sync: Arc<AtomicBool>,
          fo_c: FuncObj) -> (Flt, Vec<GI>, bool) {
    // Constant function
    if x_e.len() == 0 {
        return (0.0, x_e, true);
    }
    let input = ea_core(&x_e, &param, &stop, &sync, &b1, &b2, &f_bestag,
                        &x_bestbb, population, &fo_c);
    let ans = fo_c.call(&input).upper();

    (ans, input, true)
}


fn ea_core(x_e: &Vec<GI>, param: &Parameters, stop: &Arc<AtomicBool>,
           sync: &Arc<AtomicBool>, b1: &Arc<Barrier>, b2: &Arc<Barrier>,
           f_bestag: &Arc<RwLock<Flt>>,
           x_bestbb: &Arc<RwLock<Vec<GI>>>,
           population: Arc<RwLock<Vec<Individual>>>, fo_c: &FuncObj)
           -> (Vec<GI>) {
    //    let mut rng = rand::thread_rng();
    let seed: &[_] = &[1, 2, 3, 4];
    let mut rng: StdRng = SeedableRng::from_seed(seed);
    let dimension = Range::new(0, x_e.len());
    let mut ranges = Vec::new();
    for g in x_e {
        ranges.push(Range::new(g.lower(), g.upper()));
    }

    while !stop.load(AtOrd::Acquire) {
        if sync.load(AtOrd::Acquire) {
            b1.wait();
            b2.wait();
        }
        let ref mut population = *population.write().unwrap();
        sample(param.population, population, fo_c, &ranges, &mut rng);

        population.sort_by(|a, b| b.fitness.partial_cmp(&a.fitness).unwrap());

        for iteration in 0..100 {
            population.truncate(param.elitism);

            for _ in 0..param.selection {
                population.push(rand_individual(fo_c, &ranges, &mut rng));
            }

            next_generation(param.population, population, fo_c, param.mutation,
                            param.crossover, &dimension, &ranges, &mut rng);
            population.sort_by(|a, b| b.fitness.partial_cmp(&a.fitness).unwrap());

            // Report fittest of the fit.
            {
                let mut fbest = f_bestag.write().unwrap();
                
                *fbest =
                    if *fbest < population[0].fitness { population[0].fitness }
                else { *fbest };
            }
            
            // Kill worst of the worst
            let mut ftg = Vec::new();
            {
                let bestbb = x_bestbb.read().unwrap();
                // From The Gods
                for i in 0..bestbb.len() {
                    ftg.push(Range::new(bestbb[i].lower(), bestbb[i].upper()));
                }
            }
            let worst_ind = population.len() - 1;
            population[worst_ind] = rand_individual(fo_c,
                                                    &ftg,
                                                    &mut rng);
            population.sort_by(|a, b| b.fitness.partial_cmp(&a.fitness).unwrap());
        }
    }
    
    let ref population = *population.read().unwrap();
    let result = if !population.is_empty() {
        population[0].solution.clone()
    } else {
        x_e.clone()
    };
    
    result
}


fn sample(population_size: usize, population: &mut Vec<Individual>,
          fo_c: &FuncObj, ranges: &Vec<Range<f64>>, rng: &mut StdRng)
          -> () {
    for _ in 0..population_size-population.len() {
        population.push(rand_individual(fo_c, ranges, rng));
    }

    ()
}


fn rand_individual(fo_c: &FuncObj, ranges: &Vec<Range<f64>>, rng: &mut StdRng)
                   -> (Individual) {
    let mut new_sol = Vec::new();
    for r in ranges {
        new_sol.push(GI::new_p(r.ind_sample(rng)));
    }
    let fitness = fo_c.call(&new_sol).lower();

    Individual{solution:new_sol, fitness:fitness}
}


fn next_generation(population_size:usize, population: &mut Vec<Individual>,
                   fo_c: &FuncObj, mut_rate: f64, crossover: f64,
                   dimension: &Range<usize>, ranges: &Vec<Range<f64>>,
                   rng: &mut StdRng)
                   -> () {

    let elites = population.clone();

    for _ in 0..population_size-population.len() {
        if rng.gen::<f64>() < crossover {
            population.push(breed(rng.choose(&elites).unwrap(),
                                  rng.choose(&elites).unwrap(),
                                  fo_c,
                                  dimension, rng));
        } else {
            population.push(mutate(rng.choose(&elites).unwrap(), fo_c, mut_rate,
                                   dimension, ranges, rng));
        }
    }

    ()
}


fn mutate(input: &Individual, fo_c: &FuncObj, mut_rate: f64,
          dimension: &Range<usize>, ranges: &Vec<Range<f64>>, rng: &mut StdRng)
          -> (Individual) {
    let mut output_sol = Vec::new();

    for (r, &ind) in ranges.iter().zip(input.solution.iter()) {
        output_sol.push(
            if rng.gen::<f64>() < mut_rate {
                ind
            } else {
                GI::new_p(r.ind_sample(rng))
            });
    }

    let fitness = fo_c.call(&output_sol).lower();

    Individual{solution: output_sol, fitness: fitness}
}


fn breed(parent1: &Individual, parent2: &Individual, fo_c: &FuncObj,
         dimension: &Range<usize>, rng: &mut StdRng) -> (Individual) {
    let mut child = parent1.clone();
    let crossover_point = dimension.ind_sample(rng);
    child.solution.truncate(crossover_point);
    let mut rest = parent2.clone().solution.split_off(crossover_point);
    child.solution.append(&mut rest);
    child.fitness = fo_c.call(&child.solution).lower();
    child
}
