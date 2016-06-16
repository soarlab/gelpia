
use std::sync::{Barrier, RwLock, Arc, RwLockWriteGuard};
use std::sync::atomic::{AtomicBool, Ordering};

extern crate rand;
use rand::{ThreadRng, Rng};
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

    let ref mut population = population.write().unwrap();
    let input = ea_core(&x_e, &param, population, &fo_c);
    let ans = fo_c.call(&input).upper();

    (ans, input, true)
}


fn ea_core(x_e: &Vec<GI>, param: &Parameters,
           population: &mut Vec<Individual>, fo_c: &FuncObj)
           -> (Vec<GI>) {
    let mut rng = rand::thread_rng();
    let dimension = Range::new(0, x_e.len());
    let mut ranges = Vec::new();
    for g in x_e {
        ranges.push(Range::new(g.lower(), g.upper()));
    }

    let mut times = Vec::new();
    for i in 0..100 {
        population.truncate(0);
        sample(param.population, population, fo_c, &ranges, &mut rng);
        let mut flag = true;
        for iteration in 0..10000 {
            population.sort_by(|a, b| b.fitness.partial_cmp(&a.fitness).unwrap());

            //let unfit = population.split_off(param.elitism);
            population.truncate(param.elitism);

            if population[0].fitness > 200000_f64 {
                times.push(iteration);
                flag = false;
                break;
            }
            //println!("iteration: {} best fitness: {}", iteration, population[0].fitness);
            // for d in population[0].solution.clone() {
            //     print!("{} ", d.to_string());
            // }
            // println!("");

            for _ in 0..param.selection {
                //population.push(rng.choose(&unfit).unwrap().clone());
                population.push(rand_individual(fo_c, &ranges, &mut rng));
            }
            next_generation(param.population, population, fo_c, param.mutation,
                            param.crossover, &dimension, &ranges, &mut rng);
        }
        
        assert!(flag == false);
        println!("{}", times.iter().fold(0, |mut sum, &val| {sum += val; sum})/times.len());
    }

    println!("Average: {}", times.iter().fold(0, |mut sum, &val| {sum += val; sum})/times.len());
    population[0].solution.clone()
}


fn sample(population_size: usize, population: &mut Vec<Individual>,
          fo_c: &FuncObj, ranges: &Vec<Range<f64>>, rng: &mut ThreadRng)
          -> () {
    for _ in 0..population_size-population.len() {
        population.push(rand_individual(fo_c, ranges, rng));
    }

    ()
}


fn rand_individual(fo_c: &FuncObj, ranges: &Vec<Range<f64>>, rng: &mut ThreadRng)
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
                   rng: &mut ThreadRng)
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
          dimension: &Range<usize>, ranges: &Vec<Range<f64>>, rng: &mut ThreadRng)
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
         dimention: &Range<usize>, rng: &mut ThreadRng) -> (Individual) {
    // let mut child = parent1.clone();
    // let crossover_point = dimention.ind_sample(rng);
    // child.solution.truncate(crossover_point);
    // let mut rest = parent2.clone().solution.split_off(crossover_point);
    // child.solution.append(&mut rest);
    // child.fitness = fo_c.call(&child.solution).lower();
    // child
    let (dumb_parent, smart_parent) = if parent1.fitness < parent2.fitness
    {(parent1, parent2)}else{(parent2, parent1)};

    let child = smart_parent.solution.iter().zip(dumb_parent.solution.iter()).map(|(&sm, &du)| GI::new_p(2)*sm-du).collect();
    
    let fitness = fo_c.call(&child).lower();
    
    Individual{solution: child, fitness: fitness}
}
