// A genetic algorithm in Rust, for testing of stochastic methods for
// accelerating rigorous global maximization.

// Adapted from https://github.com/andschwa/rust-genetic-algorithm
// By Andy Schwartzmeyer (https://github.com/andschwa)

extern crate time;
use time::{precise_time_s};

extern crate rand;
use rand::{Rng};

extern crate gu;
use gu::{Parameters, INF, Flt};

extern crate gr;
use gr::{GI};

use rand::distributions::{Range, IndependentSample};

use std::cmp::{Eq, PartialEq, Ordering, PartialOrd};

use std::mem;

use std::sync::{Barrier, RwLock, Arc};

use std::sync::atomic::{AtomicBool};
use std::sync::atomic::Ordering as AtOrd;

extern crate function;
use function::FuncObj;

/// A genetic algorithm that searches for convergence to the given
/// tolerance for the problem across the n-dimensional hypercube,
/// using a population of individuals, up to a maximum iterations
/// number of generations.
pub fn ea(x_0: Vec<GI>, params: Parameters,
          population: Arc<RwLock<Vec<Individual>>>,
          f_bestag: Arc<RwLock<Flt>>,
          x_bestbb: Arc<RwLock<Vec<GI>>>,
          b1: Arc<Barrier>, b2: Arc<Barrier>,
          stop: Arc<AtomicBool>, sync: Arc<AtomicBool>, f: FuncObj) {
    // SETUP
    // get thread local random number generator
    let mut rng = rand::thread_rng();

    // initialize population of individuals
    {
        let mut population_w = population.write().unwrap();
        for _ in 0..params.population {
            population_w.push(Individual::new(&x_0, &mut rng, &f));
        }
        assert!(population_w.len() == params.population);
    }

    let mut running: f64 = 0.0;
    let mut iters: u64 = 0;


    // start timing the search
    //let start_time = precise_time_s();
    // END SETUP
    // search iterations number of generations
    //for i in 0..params.iterations {
    while !stop.load(AtOrd::SeqCst) {
        if sync.load(AtOrd::SeqCst) {
            b1.wait();
            b2.wait();
        }
        
/*        if iters % 1000 == 0 {
            println!("Average time per iteration: {} ms/i", running);
        }

        let start = precise_time_s();*/
        
        let mut population = population.write().unwrap();
        {
            let mut fbest = f_bestag.write().unwrap();
            *fbest = match (*population).iter().max() {
                Some(i) => i.fitness,
                None => panic!("wtf"),
                }
        }
        // select, mutate, and crossover individuals for next generation
        let mut offspring: Vec<Individual> = Vec::with_capacity(population.len());
        for _ in 0..population.len()/2 {
            let (mut x, mut y) = (select(&population, params.selection, &mut rng),
                                  select(&population, params.selection, &mut rng));
            x.mutate(&x_0, params.mutation, &mut rng);
            y.mutate(&x_0, params.mutation, &mut rng);
            Individual::crossover(&mut x, &mut y, params.crossover, &mut rng, &f);
            offspring.push(x);
            offspring.push(y);
        }
        assert!(offspring.len() == population.len());

        // replace 2 random individuals with elite of prior generation
        for _ in 0..params.elitism {
            if let Some(x) = population.iter().max() {
                offspring[rng.gen_range(0, population.len())] = x.clone();
            }
        }
        
        // Replace worst with bestbb
        let mut worst_i = -1;
        let mut worst = INF;
        for i in 0..offspring.len() {
            if offspring[i].fitness < worst {
                worst = offspring[i].fitness;
                worst_i = i;
            }
        }
        {
            let bestbb = x_bestbb.read().unwrap();
            offspring[worst_i] = Individual::new(&bestbb, &mut rng, &f);
        }

        // replace population with next generation
        *population = offspring;

/*	running = ((precise_time_s() - start)*1000.0 + (iters as f64)*running)/(iters as f64 + 1.0);
        iters += 1;*/
    }
}


/// Tournament selection from n random individuals
fn select<R: Rng>(population: &[Individual], n: usize, rng: &mut R) -> Individual {
    if let Some(selected) = (0..n).map(|_| rng.choose(population)).max() {
        selected.unwrap().clone()
    } else {
        unimplemented!();
    }
}

#[derive(Clone)]
pub struct Individual {
    pub solution: Vec<GI>,
    pub fitness: Flt,
}

impl Individual {
    /// Constructs a new Individual to solve Problem with n random values
    pub fn new<R: Rng>(x: &Vec<GI>, rng: &mut R, f: &FuncObj) -> Self {
        let mut result = Vec::new();
        for i in 0..x.len() {
            let up = x[i].upper();
            let low = x[i].lower();

            let num = if 
                up == low {up} 
            else 
            {Range::new(low, 
                        up).ind_sample(rng)};
            result.push(GI::new_d(num, num));
        }
        let fitness = f.call(&result).lower();
        Individual{solution: result, fitness: fitness}
    }

    /// Mutate with chance n a single gene to a new value in the
    /// problem's domain (a "jump" mutation).
    ///
    /// Fitness is NOT evaluated as it is ALWAYS done in `crossover()`
    pub fn mutate<R: Rng>(&mut self, x: &Vec<GI>, chance: f64, rng: &mut R) {
        if rng.gen_range(0_f64, 1_f64) < chance {
            let i = rng.gen_range(0, self.solution.len());
            let up = x[i].upper();
            let low = x[i].lower();

            let num = if up == low {up} else {Range::new(low, up).ind_sample(rng)};

            self.solution[i] = GI::new_d(num, num);
        }
    }
    
    /// Performs two-point crossover with chance n to swap a random
    /// set of [0, dimension] genes between a pair of individuals.
    ///
    /// Fitness is ALWAYS evaluated because it is NOT done in mutate()
    pub fn crossover<R: Rng>(x: &mut Individual, y: &mut Individual,
                             chance: f64, rng: &mut R, f: &FuncObj) {
        // assert_eq!(x.problem, y.problem);
        if rng.gen_range(0_f64, 1_f64) < chance {
            let len = x.solution.len();
            let (start, n) = (rng.gen_range(0, len), rng.gen_range(0, len));
            for i in start..start + n {
                mem::swap(&mut x.solution[i % len], &mut y.solution[i % len]);
            }
        }
        x.fitness = f.call(&x.solution).lower();
        y.fitness = f.call(&y.solution).lower();
    }
}

impl Eq for Individual {}

impl Ord for Individual {
    /// This dangerously delegates to `partial_cmp`; NaN will panic
    fn cmp(&self, other: &Self) -> Ordering {
        if let Some(result) = self.fitness.partial_cmp(&other.fitness) {
            return result;
        }
        unimplemented!();
    }
}

impl PartialEq<Individual> for Individual {
    /// This doesn't use `fitness.eq()` because it needs to be
    /// consistent with `Eq`
    fn eq(&self, other: &Individual) -> bool {
        if let Some(result) = self.fitness.partial_cmp(&other.fitness) {
            return result == Ordering::Equal;
        }
        unimplemented!();
    }
}

impl PartialOrd for Individual {
    /// This delegates to `fitness.partial_cmp()`
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        self.fitness.partial_cmp(&other.fitness)
    }
}
