from unified_planning.shortcuts import *
from unified_planning.model import Problem, Fluent, Parameter
from typing import Callable

from gridworld_domain import setup_gridworld_domain
from blocksworld_domain import setup_blocksworld_domain

def create_problem(domain_setup_fn: Callable[[Problem], dict]):
    """
    Sets up a domain-independent problem using only the restore conditions
    explicitly provided by the domain.
    """
    problem = Problem("generalized_domain")

    # Call domain-specific setup
    setup_info = domain_setup_fn(problem)

    restore_conditions = setup_info.get("restore_conditions", [])
    success_conditions = setup_info.get("success_conditions", [])

    # Add restore goals (manually selected by domain)
    for cond in restore_conditions:
        problem.add_goal(cond)

    # Add any additional success conditions
    for cond in success_conditions:
        problem.add_goal(cond)

    return problem


problem = create_problem(setup_gridworld_domain)
print(problem.kind)
#print(problem)

with OneshotPlanner(problem_kind=problem.kind) as planner:
    result = planner.solve(problem)
    plan = result.plan
    if plan is not None:
        print("%s returned:" % planner.name)
        print(plan)
    else:
        print("No plan found.")

# Uncomment to try blocksworld:
problem = create_problem(setup_blocksworld_domain)
print(problem.kind)
#print(problem)

with OneshotPlanner(problem_kind=problem.kind) as planner:
    result = planner.solve(problem)
    plan = result.plan
    if plan is not None:
        print("%s returned:" % planner.name)
        print(plan)
    else:
        print("No plan found.")
