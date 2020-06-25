

use std::io::Write;
use std::process::{Command, Stdio};

extern crate gr;
use gr::GI;

#[derive(Clone)]
pub struct Solver {
    has_constraints: bool,
    variable_names: Vec<String>,
    ftol_abs: String,
    ftol_rel: String,
    positive_constraint: String,
    negative_constraint: String,
}


impl Solver {
    pub fn new(query: &String, names: &Vec<String>,
               ftol_abs: f64, ftol_rel: f64)
               -> Solver {
        let query_preamble = names.iter()
            .map(|n| format!("(declare-fun {} () Real)\n", n))
            .collect::<Vec<String>>()
            .concat();

        let ftol_abs_string = { if ftol_abs <= 0.0
                                { "1.0e-6".to_string() }
                                else { ftol_abs.to_string() } };

        let ftol_rel_string = { if ftol_rel <= 0.0
                                { "1.0e-6".to_string() }
                                else { ftol_rel.to_string() } };

        Solver{
            has_constraints: query.len() > 0,
            variable_names: names.clone(),
            ftol_abs: ftol_abs_string,
            ftol_rel: ftol_rel_string,
            positive_constraint: format!("{}(assert {})\n",
                                         query_preamble, query),
            negative_constraint: format!("{}(assert (not {}))\n",
                                         query_preamble, query),
        }
    }

    fn make_query(&self, is_positive: bool, input_ranges: &Vec<GI>)
                  -> String {
        let constraint = { if is_positive
                           { self.positive_constraint.clone() }
                           else { self.negative_constraint.clone()} };

        let range_mins = self.variable_names.iter()
            .zip(input_ranges.iter())
            .map(|(n,i)| format!("(assert (<= {} {}))\n", i.lower(), n));

        let range_maxs = self.variable_names.iter()
            .zip(input_ranges.iter())
            .map(|(n,i)| format!("(assert (<= {} {}))\n", n, i.upper()));

        let mut query_parts = Vec::new();

        query_parts.push(constraint);
        query_parts.extend(range_mins);
        query_parts.extend(range_maxs);
        query_parts.push("(check-sat)\n".to_string());
        query_parts.push("(exit)\n".to_string());

        let query = query_parts.concat();

        query
    }

    fn check_query(&self, query: String)
                   -> bool {

        // for line in query.lines() {
        //     println!("debug: {}", line);
        // }

        let mut child = Command::new("dreal")
            .arg("--in")
            .arg("--nlopt-ftol-abs")
            .arg(self.ftol_abs.clone())
            .arg("--nlopt-ftol-rel")
            .arg(self.ftol_rel.clone())
            .stdin(Stdio::piped())
            .stdout(Stdio::piped())
            .spawn()
            .expect("Failed to execute dreal");

        {
            let stdin = child.stdin.as_mut().expect("Failed to open stdin");
            stdin.write_all(query.as_bytes()).expect("Failed to write to stdin");
        }

        let output = child.wait_with_output().expect("Failed to read stdout");
        let result = String::from_utf8_lossy(&output.stdout);

        if result.contains("delta-sat") {
            true
        } else if result.contains("unsat") {
            false
        } else {
            panic!("dreal did not output an answer");
        }
    }

    pub fn check_may(&self, input_ranges: &Vec<GI>)
                 -> bool {
        if self.has_constraints {
            let query = self.make_query(true, input_ranges);
            let sat = self.check_query(query);
            sat
        } else {
            true
        }
    }

    pub fn check_may_not(&self, input_ranges: &Vec<GI>)
                     -> bool {
        if self.has_constraints {
            let query = self.make_query(false, input_ranges);
            let sat = self.check_query(query);
            sat
        } else {
            false
        }
    }

    pub fn check_must(&self, input_ranges: &Vec<GI>)
                  -> bool {
        if self.has_constraints {
            self.check_may(input_ranges) && !self.check_may_not(input_ranges)
        } else {
            true
        }
    }
}




#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn true_constraint() {
        let inputs = vec![GI::new_d(0.0, 10.0)];
        let names = vec!["x".to_string()];
        let constr = Solver::new(&"(> 2 1)".to_string(), &names,
                                 1.0e-6, 1.0e-6);

        assert_eq!(true, constr.check_may(&inputs));
        assert_eq!(false, constr.check_may_not(&inputs));
        assert_eq!(true, constr.check_must(&inputs));
    }

    #[test]
    fn false_constraint() {
        let inputs = vec![GI::new_d(0.0, 10.0)];
        let names = vec!["x".to_string()];
        let constr = Solver::new(&"(> 1 2)".to_string(), &names,
                                 1.0e-6, 1.0e-6);

        assert_eq!(false, constr.check_may(&inputs));
        assert_eq!(true, constr.check_may_not(&inputs));
        assert_eq!(false, constr.check_must(&inputs));
    }

    #[test]
    fn mixed_constraint() {
        let inputs = vec![GI::new_d(0.0, 10.0),
                          GI::new_d(0.0, 10.0),];
        let names = vec!["x".to_string(),
                         "y".to_string(),];
        let constr = Solver::new(&"(> (* (^ x 2) y) 99)".to_string(), &names,
                                 1.0e-6, 1.0e-6);

        assert_eq!(true, constr.check_may(&inputs));
        assert_eq!(true, constr.check_may_not(&inputs));
        assert_eq!(false, constr.check_must(&inputs));
    }

}
