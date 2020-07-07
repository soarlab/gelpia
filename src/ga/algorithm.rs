use std::sync::{Barrier, RwLock, Arc};
use std::sync::atomic::{AtomicBool};
use std::sync::atomic::Ordering as AtOrd;
extern crate rand;
use rand::{Rng, SeedableRng, XorShiftRng};
use rand::distributions::{IndependentSample, Range};


extern crate gr;
use gr::{GI};

extern crate gelpia_utils;
use gelpia_utils::{Flt, Parameters};

extern crate function;
use function::FuncObj;

extern crate solver;
use solver::Solver;

type GARng = XorShiftRng;

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
          fo_c: FuncObj,
          mut solver: Solver) {
    // Constant function
    if x_e.len() == 0 {
        return;
    }
    let seed = param.seed;
    ea_core(&x_e, &param, &stop, &sync, &b1, &b2, &f_bestag,
            &x_bestbb, population, &fo_c, seed, &mut solver);
    return;
}


fn ea_core(x_e: &Vec<GI>, param: &Parameters, stop: &Arc<AtomicBool>,
           sync: &Arc<AtomicBool>, b1: &Arc<Barrier>, b2: &Arc<Barrier>,
           f_bestag: &Arc<RwLock<Flt>>,
           x_bestbb: &Arc<RwLock<Vec<GI>>>,
           population: Arc<RwLock<Vec<Individual>>>, fo_c: &FuncObj,
           seed: u32,
           solver: &mut Solver) {
    let rng_seed: u32 =
        match seed {
            0 => 3735928579,
            1 => rand::thread_rng().next_u32(),
            _ => seed,
        };
    let seed_r: [u32; 4] = [(rng_seed & 0xFF000000) >> 24,
                            (rng_seed & 0xFF0000) >> 16,
                            (rng_seed & 0xFF00) >> 8 ,
                            rng_seed & 0xFF];
    let mut rng: GARng = GARng::from_seed(seed_r);

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
        if sample(param.population, population, fo_c, &ranges, &mut rng, stop, solver) {
            return;
        }

        population.sort_by(|a, b| b.fitness.partial_cmp(&a.fitness).unwrap());

        for _ in 0..100 {
            if stop.load(AtOrd::Acquire) {
                return;
            }
            population.truncate(param.elitism);

            for _ in 0..param.selection {
                let ind = rand_individual(fo_c, &ranges, &mut rng, solver);
                population.push(ind);
            }

            if next_generation(param.population, population, fo_c, param.mutation,
                               param.crossover, &dimension, &ranges, &mut rng,
                               stop, solver) {
                return;
            }
            population.sort_by(|a, b| b.fitness.partial_cmp(&a.fitness).unwrap());

            // Report fittest of the fit.
            {
                let mut fbest = f_bestag.write().unwrap();
                let most_elite = population[0].fitness;
                if *fbest < most_elite {
                    *fbest = most_elite;
                }
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
                                                    &mut rng,
                                                    solver);
            population.sort_by(|a, b| b.fitness.partial_cmp(&a.fitness).unwrap());
        }
    }

    return;
}


fn sample(population_size: usize, population: &mut Vec<Individual>,
          fo_c: &FuncObj, ranges: &Vec<Range<f64>>, rng: &mut GARng,
          stop: &Arc<AtomicBool>, solver: &mut Solver)
          -> bool {
    for i in 0..population_size-population.len() {
        if i % 64 == 0 && stop.load(AtOrd::Acquire) {
            return true;
        }
        population.push(rand_individual(fo_c, ranges, rng, solver));
    }

    false
}


fn rand_individual(fo_c: &FuncObj, ranges: &Vec<Range<f64>>, rng: &mut GARng,
                   solver: &mut Solver)
                   -> (Individual) {
    loop {
        let new_sol =ranges.iter()
            .map(|r| GI::new_p(r.ind_sample(rng)))
            .collect();
        if !solver.check_may(&new_sol) {
            continue;
        }

        let (fitness_i, _) = fo_c.call(&new_sol);
        let fitness = fitness_i.lower();

        return Individual{solution:new_sol, fitness:fitness}
    }
}


fn next_generation(population_size:usize, population: &mut Vec<Individual>,
                   fo_c: &FuncObj, mut_rate: f64, crossover: f64,
                   dimension: &Range<usize>, ranges: &Vec<Range<f64>>,
                   rng: &mut GARng, stop: &Arc<AtomicBool>, solver: &mut Solver)
                   -> bool {

    let elites = population.clone();

    for i in 0..population_size-population.len() {
        if i % 64 == 0 && stop.load(AtOrd::Acquire) {
            return true;
        }
        if rng.gen::<f64>() < crossover {
            population.push(breed((&mut *rng).choose(&elites).unwrap(),
                                  rng.choose(&elites).unwrap(),
                                  fo_c,
                                  dimension, rng, solver));
        } else {
            population.push(mutate(rng.choose(&elites).unwrap(), fo_c, mut_rate,
                                   ranges, rng, solver));
        }
    }

    false
}


fn mutate(input: &Individual, fo_c: &FuncObj, mut_rate: f64,
          ranges: &Vec<Range<f64>>, rng: &mut GARng, solver: &mut Solver)
          -> (Individual) {
    loop {
        let output_sol = ranges.iter().zip(input.solution.iter())
            .map(|(r, &ind)| { if rng.gen::<f64>() < mut_rate
                               { ind }
                               else { GI::new_p(r.ind_sample(&mut *rng)) } })
            .collect::<Vec<GI>>();

        if !solver.check_may(&output_sol) {
            continue
        }

        let (fitness_i, _) = fo_c.call(&output_sol);
        let fitness = fitness_i.lower();

        return Individual{solution: output_sol, fitness: fitness}
    }
}


fn breed(parent1: &Individual, parent2: &Individual, fo_c: &FuncObj,
         dimension: &Range<usize>, rng: &mut GARng, solver: &mut Solver)
         -> (Individual) {
    loop {
        let mut child = parent1.clone();
        let crossover_point = dimension.ind_sample(rng);
        child.solution.truncate(crossover_point);
        let mut rest = parent2.clone().solution.split_off(crossover_point);
        child.solution.append(&mut rest);

        if !solver.check_may(&child.solution) {
            continue
        }

        let (fitness_i, _) = fo_c.call(&child.solution);
        child.fitness = fitness_i.lower();
        return child
    }
}
