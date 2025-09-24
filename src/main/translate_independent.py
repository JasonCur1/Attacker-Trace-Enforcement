from unified_planning.shortcuts import *
from unified_planning.model import Problem, Fluent, Parameter, Object
from unified_planning.io import PDDLWriter
from typing import Callable, List

from gridworld_domain import setup_gridworld_domain
from blocksworld_domain import setup_blocksworld_domain

def create_problem(domain_setup_fn: Callable[[Problem], dict]):
    """
    Sets up a domain-independent problem using a snapshot of the initial state
    to ensure state restoration, and includes domain-specific success conditions.
    """
    problem = Problem("generalized_domain")

    # Setup domain
    setup_info = domain_setup_fn(problem)
    domain_goals = setup_info.get("success_conditions", [])

    # Take snapshot of initial state for restoration goals
    # restore_goals = []
    # for fluent_expr, val in problem.initial_values.items():
    #     # Check if the FNode is a Boolean constant with value TRUE
    #     if val.is_bool_constant() and val.bool_constant_value():
    #         restore_goals.append(fluent_expr)


    # # Add both restoration and domain-specific goals
    # for goal in restore_goals + domain_goals:
    #     problem.add_goal(goal)

    for goal in domain_goals:
        problem.add_goal(goal)

    return problem


# Select domain here
problem = create_problem(setup_gridworld_domain)

# Write to PDDL files for the Stackelberg planner
w = PDDLWriter(problem)
w.write_domain('domain.pddl')
w.write_problem('problem.pddl')

# Uncomment to try blocksworld:
# problem = create_problem(setup_blocksworld_domain)
# w = PDDLWriter(problem)
# w.write_domain('blocksworld_domain.pddl')
# w.write_problem('blocksworld_problem.pddl')