"""
SAT solver using CDCL
"""
import os
import time
from collections import deque
from pkg.utils.constants import TRUE, FALSE, UNASSIGN
from pkg.utils.exceptions import FileFormatError
from pkg.utils.logger import set_logger

logger = set_logger()


class Solver:

    def __init__(self, filename, proof, suffix):
        logger.info('========= create pysat from %s =========', filename)
        self.filename = filename
        self.proof_cnf, self.proof_vars, self.cnf, self.vars = Solver.read_file(filename, proof)
        self.decision_list = list(map(int, suffix.split(',')))
        self.learnts = set()
        self.assigns = dict.fromkeys(list(self.vars), UNASSIGN)
        self.proof_assigns = dict.fromkeys(list(self.proof_vars), UNASSIGN)
        self.level = 0
        self.proof_level = 0
        self.nodes = dict((k, ImplicationNode(k, UNASSIGN)) for k in list(self.vars))
        self.branching_vars = set()
        self.branching_history = {}  # level -> branched variable
        self.propagate_history = {}  # level -> propagate variables list
        self.proof_propagate_history = {}  # level -> propagate variables list
        self.branching_count = 0
      
    def run(self):
         self.unit_prop_path_conditions()
         self.proof_transform()
         self.assigns = dict.fromkeys(list(self.vars), UNASSIGN)
         for elem in self.proof_cnf:
             for e in elem:
                print(e,end=" ")
             print("0")

         #print(self.proof_cnf)
         
         
    def Update(self):
        for bt_var in self.decision_list:
           self.level += 1
           self.branching_count += 1
           self.assigns[abs(bt_var)] = bt_var>0
           self.branching_vars.add(abs(bt_var))
           self.branching_history[self.level] = abs(bt_var)
           self.propagate_history[self.level] = deque()
           self.update_graph(abs(bt_var))
           self.preprocess()              		


    def proof_transform(self):
        for clause in self.proof_cnf:
            temp_clause = list(clause)
            flag = 1
            for lit in clause:
                 if abs(lit) not in self.proof_assigns.keys():
                       pass
                 elif self.proof_assigns[abs(lit)]==-1:
                       pass
                 elif lit<0 and self.proof_assigns[abs(lit)]:  
                       temp_clause.remove(lit)
                 elif lit>0 and not self.proof_assigns[abs(lit)]:  
                       temp_clause.remove(lit)
                 else:
                       flag = 0
                       break 
            self.proof_cnf.remove(clause)       
            if flag:
                 self.proof_cnf.add(clause)
        
        
                             
    def unit_prop_path_conditions(self):
        unit_clauses = set()
        for lit in self.decision_list:
            unit_clauses.add(frozenset([lit]))
        while True:
            propagate_queue = deque()
            cls = [x for x in self.cnf.union(unit_clauses)]
            for clause in cls:
                c_val = self.compute_clause(clause) 
                if c_val == TRUE:
                    continue
                if c_val == FALSE:
                    return clause
                else:
                    is_unit, unit_lit = self.is_unit_clause(clause) 
                    if not is_unit:
                        continue
                    prop_pair = (unit_lit, clause)
                    if prop_pair not in propagate_queue:
                        propagate_queue.append(prop_pair)
            if not propagate_queue:
                return None
            logger.fine('propagate_queue: %s', propagate_queue)
            for prop_lit, clause in propagate_queue:
                prop_var = abs(prop_lit)
                self.assigns[prop_var] = TRUE if prop_lit > 0 else FALSE
                logger.fine('propagated %s to be %s', prop_var, self.assigns[prop_var])
	

    def proofred(self):
        self.preprocess()
        conf_cls = self.unit_propagate()
        if conf_cls is not None:
             # there is conflict in unit propagation
             return self.conflict_analyze(conf_cls)
        else:
             raise FileFormatError('Sub problem not UNSAT')



    def preprocess(self):
        """ Injects before solving """
        pass

    @staticmethod
    def read_file(filename, proof):
        """
        Reads a DIMACS CNF format file, returns clauses (set of frozenset) and
        literals (set of int).
            :param filename: the file name
            :raises FileFormatError: when file format is wrong
            :returns: (clauses, literals)
        """
        with open(filename) as f:
            lines = [
                line.strip().split() for line in f.readlines()
                if (not (line.startswith('c') or
                         line.startswith('%') or
                         line.startswith('0'))
                    and line != '\n')
            ]
            
        if lines[0][:2] == ['p', 'cnf']:
            count_literals, count_clauses = map(int, lines[0][-2:])
        else:
            raise FileFormatError('Number of literals and clauses are not declared properly.')

        literals = set()
        clauses = set()

        for line in lines[1:]:
            if line[-1] != '0':
                raise FileFormatError('Each line of clauses must end with 0.')
            clause = frozenset(map(int, line[:-1]))
            literals.update(map(abs, clause))
            clauses.add(clause)

        if len(literals) != count_literals or len(lines) - 1 != count_clauses:
            raise FileFormatError(
                'Unmatched literal count or clause count.'
                ' Literals expected: {}, actual: {}.'
                ' Clauses expected: {}, actual: {}.'
                    .format(count_literals, len(literals), count_clauses, len(clauses)))

        logger.fine('clauses: %s', clauses)
        logger.fine('literals: %s', literals)               
 
 
        with open(proof) as f:
            lines = [
                line.strip().split() for line in f.readlines()
                if (not (line.startswith('0') or
                         line.startswith('d') or
                         line.startswith('c'))
                    and line != '\n')
            ]
            
        proof_literals = set()
        proof_clauses = set()

        for line in lines:
            if line[-1] != '0':
                raise FileFormatError('Each line of clauses must end with 0.')
            clause = frozenset(map(int, line[:-1]))
            proof_literals.update(map(abs, clause))
            proof_clauses.add(clause)
 
  
        return proof_clauses, proof_literals, clauses, literals


    def compute_value(self, literal):
        """
        Compute the value of the literal (could be -/ve or +/ve) from
        `assignment`. Returns -1 if unassigned
            :param literal: an int, can't be 0
            :returns: value of the literal
        """
        value = self.assigns[abs(literal)]
        value = value if value == UNASSIGN else value ^ (literal < 0)
        logger.finest('value: %s', value)
        return value

    def proof_compute_value(self, literal):
        value = self.proof_assigns[abs(literal)]
        value = value if value == UNASSIGN else value ^ (literal < 0)
        logger.finest('value: %s', value)
        return value


    def compute_clause(self, clause):
        values = list(map(self.compute_value, clause))
        value = UNASSIGN if UNASSIGN in values else max(values)
        logger.finest('clause: %s, value: %s', clause, value)
        return value

    def proof_compute_clause(self, clause):
        values = list(map(self.proof_compute_value, clause))
        value = UNASSIGN if UNASSIGN in values else max(values)
        logger.finest('clause: %s, value: %s', clause, value)
        return value

    def compute_cnf(self):
        logger.fine('cnf: %s', self.cnf)
        logger.fine('assignments: %s', self.assigns)
        return min(map(self.proof_compute_clause, self.cnf))

    def proof_is_unit_clause(self, clause):
        """
        Checks if clause is a unit clause. If and only if there is
        exactly 1 literal unassigned, and all the other literals having
        value of 0.
            :param clause: set of ints
            :returns: (is_clause_a_unit, the_literal_to_assign, the clause)
        """
        logger.finest('clause: %s', clause)
        values = []
        unassigned = None

        for literal in clause:
            value = self.proof_compute_value(literal)
            logger.finest('value of %s: %s', literal, value)
            values.append(value)
            unassigned = literal if value == UNASSIGN else unassigned

        check = ((values.count(FALSE) == len(clause) - 1 and
                  values.count(UNASSIGN) == 1) or
                 (len(clause) == 1
                  and values.count(UNASSIGN) == 1))
        logger.finest('%s: %s', clause, (check, unassigned))
        logger.finest('assignments: %s', self.assigns)
        return check, unassigned


    def is_unit_clause(self, clause):
        """
        Checks if clause is a unit clause. If and only if there is
        exactly 1 literal unassigned, and all the other literals having
        value of 0.
            :param clause: set of ints
            :returns: (is_clause_a_unit, the_literal_to_assign, the clause)
        """
        logger.finest('clause: %s', clause)
        values = []
        unassigned = None

        for literal in clause:
            value = self.compute_value(literal)
            logger.finest('value of %s: %s', literal, value)
            values.append(value)
            unassigned = literal if value == UNASSIGN else unassigned

        check = ((values.count(FALSE) == len(clause) - 1 and
                  values.count(UNASSIGN) == 1) or
                 (len(clause) == 1
                  and values.count(UNASSIGN) == 1))
        logger.finest('%s: %s', clause, (check, unassigned))
        logger.finest('assignments: %s', self.assigns)
        return check, unassigned

    def assign(self, literal):
        """ Assign the variable so that literal is TRUE """

    def update_graph(self, var, clause=None):
        node = self.nodes[var]
        node.value = self.assigns[var]
        node.level = self.level

        # update parents
        if clause:  # clause is None, meaning this is branching, no parents to update
            for v in [abs(lit) for lit in clause if abs(lit) != var]:
                node.parents.append(self.nodes[v])
                self.nodes[v].children.append(node)
            node.clause = clause
            logger.fine('node %s has parents: %s', var, node.parents)

    def unit_propagate(self):
        """
        A unit clause has all of its literals but 1 assigned to 0. Then, the sole
        unassigned literal must be assigned to value 1. Unit propagation is the
        process of iteratively applying the unit clause rule.
        :return: None if no conflict is detected, else return the literal
        """
        while True:
            propagate_queue = deque()
            for clause in [x for x in self.cnf.union(self.learnts)]:
                c_val = self.compute_clause(clause)
                if c_val == TRUE:
                    continue
                if c_val == FALSE:
                    return clause
                else:
                    is_unit, unit_lit = self.is_unit_clause(clause)
                    if not is_unit:
                        continue
                    prop_pair = (unit_lit, clause)
                    if prop_pair not in propagate_queue:
                        propagate_queue.append(prop_pair)
            if not propagate_queue:
                return None
            logger.fine('propagate_queue: %s', propagate_queue)

            for prop_lit, clause in propagate_queue:
                prop_var = abs(prop_lit)
                self.assigns[prop_var] = TRUE if prop_lit > 0 else FALSE
                logger.fine('propagated %s to be %s', prop_var, self.assigns[prop_var])
                self.update_graph(prop_var, clause=clause)
                try:
                    self.propagate_history[self.level].append(prop_lit)
                except KeyError:
                    pass  # propagated at level 0

    def get_unit_clauses(self):
        return list(filter(lambda x: x[0], map(self.is_unit_clause, self.cnf)))

    def all_unassigned_vars(self):
        return filter(
            lambda v: v in self.assigns and self.assigns[v] == UNASSIGN,
            self.vars)


    def conflict_analyze(self, conf_cls):
        """
        Analyze the most recent conflict and learn a new clause from the conflict.
        - Find the cut in the implication graph that led to the conflict
        - Derive a new clause which is the negation of the assignments that led to the conflict

        Returns a decision level to be backtracked to.
        :param conf_cls: (set of int) the clause that introduces the conflict
        :return: ({int} level to backtrack to, {set(int)} clause learnt)
        """
        def next_recent_assigned(clause):
            """
            According to the assign history, separate the latest assigned variable
            with the rest in `clause`
            :param clause: {set of int} the clause to separate
            :return: ({int} variable, [int] other variables in clause)
            """
            for v in reversed(assign_history):
                if v in clause or -v in clause:
                    return v, [x for x in clause if abs(x) != abs(v)]

        if self.level == 0:
            return -1, None

        logger.fine('conflict clause: %s', conf_cls)

        assign_history = [self.branching_history[self.level]] + list(self.propagate_history[self.level])
        logger.fine('assign history for level %s: %s', self.level, assign_history)

        pool_lits = conf_cls
        done_lits = set()
        curr_level_lits = set()
        prev_level_lits = set()

        while True:
            logger.fine('-------')
            logger.fine('pool lits: %s', pool_lits)
            for lit in pool_lits:
                if self.nodes[abs(lit)].level == self.level:
                    curr_level_lits.add(lit)
                else:
                    prev_level_lits.add(lit)

            logger.fine('curr level lits: %s', curr_level_lits)
            logger.fine('prev level lits: %s', prev_level_lits)
            if len(curr_level_lits) == 1:
                break

            last_assigned, others = next_recent_assigned(curr_level_lits)
            logger.fine('last assigned: %s, others: %s', last_assigned, others)

            done_lits.add(abs(last_assigned))
            curr_level_lits = set(others)

            pool_clause = self.nodes[abs(last_assigned)].clause
            pool_lits = [
                l for l in pool_clause if abs(l) not in done_lits
            ] if pool_clause is not None else []

            logger.fine('done lits: %s', done_lits)

        learnt = frozenset([l for l in curr_level_lits.union(prev_level_lits)])
        if prev_level_lits:
            level = max([self.nodes[abs(x)].level for x in prev_level_lits])
        else:
            level = self.level - 1

        return level, learnt



class ImplicationNode:
    """
    Represents a node in an implication graph. Each node contains
    - its value
    - its implication children (list)
    - parent nodes (list)
    """

    def __init__(self, variable, value):
        self.variable = variable
        self.value = value
        self.level = -1
        self.parents = []
        self.children = []
        self.clause = None

    def all_parents(self):
        parents = set(self.parents)
        for parent in self.parents:
            for p in parent.all_parents():
                parents.add(p)
        return list(parents)

    def __str__(self):
        sign = '+' if self.value == TRUE else '-' if self.value == FALSE else '?'
        return "[{}{}:L{}, {}p, {}c, {}]".format(
            sign, self.variable, self.level, len(self.parents), len(self.children), self.clause)

    def __repr__(self):
        return str(self)
