from unified_planning.shortcuts import *
from unified_planning.model import Problem, Fluent, Parameter
from typing import Callable
import itertools

from gridworld_domain import setup_gridworld_domain
from blocksworld_domain import setup_blocksworld_domain


def create_problem(domain_setup_fn: Callable[[Problem], dict]):
    """
    Sets up a domain-independent problem where the goal is to restore
    the initial state after performing some actions.

    domain_setup_fn should set up the domain (objects, fluents, actions, initial values)
    and return a dictionary like:
    {
        "fluents_to_track": List[Fluent],  # fluents whose values we want to "restore"
        "success_conditions": List[Expression],  # optional goal conditions that indicate task success
    }
    """
    problem = Problem("generalized_domain")

    # Call domain-specific setup, passing in the problem object
    setup_info = domain_setup_fn(problem)
    tracked_fluents = setup_info.get("fluents_to_track", [])
    success_conditions = setup_info.get("success_conditions", [])



    # Step 1: Collect all possible grounded fluents for our tracked fluents
    grounded_fluents = {}
    for fluent in tracked_fluents:
        sig = fluent.signature
        if not sig:  # No parameters
            grounded_fluents[(fluent, ())] = problem.initial_value(fluent())
        else:
            # Generate all possible parameter combinations
            param_types = [p.type for p in sig]
            objects_by_type = [problem.objects(t) for t in param_types]

            # Create cartesian product of all possible parameter combinations
            for params in itertools.product(*objects_by_type):
                try:
                    # Get the initial value if it exists
                    value = problem.initial_value(fluent(*params))
                    grounded_fluents[(fluent, params)] = value
                except:
                    # If the value is not defined, skip it
                    pass



    # Step 2: Create static fluents to represent the initial state
    static_fluents = {}
    for (fluent, params), value in grounded_fluents.items():
        # Create a new static fluent with the same parameters
        static_name = f"initial_{fluent.name}"

        if not fluent.signature:  # No parameters
            if static_name not in static_fluents:
                static_fluent = problem.add_fluent(static_name, fluent.type)
                static_fluents[static_name] = static_fluent
                problem.set_initial_value(static_fluent(), value)
        else:
            if static_name not in static_fluents:
                # Create fluent with same signature
                param_dict = {}
                for i, p in enumerate(fluent.signature):
                    param_dict[f"p{i}"] = p.type

                static_fluent = problem.add_fluent(static_name, fluent.type, **param_dict)
                static_fluents[static_name] = static_fluent

            # Set the initial value
            problem.set_initial_value(static_fluents[static_name](*params), value)



    # Step 3: Add goals to make final state match initial state
    for (fluent, params), value in grounded_fluents.items():
        static_name = f"initial_{fluent.name}"
        static_fluent = static_fluents[static_name]

        if not params:  # No parameters
            problem.add_goal(Iff(fluent(), static_fluent()))
        else:
            problem.add_goal(Iff(fluent(*params), static_fluent(*params)))

    # Add any additional success conditions
    for condition in success_conditions:
        problem.add_goal(condition)

    return problem



problem = create_problem(setup_gridworld_domain)
print(problem.kind)
print(problem)

with OneshotPlanner(problem_kind=problem.kind) as planner:
    result = planner.solve(problem)
    plan = result.plan
    if plan is not None:
        print("%s returned:" % planner.name)
        print(plan)
    else:
        print("No plan found.")

# problem = create_problem(setup_blocksworld_domain)
# print(problem.kind)
# print(problem)

# with OneshotPlanner(problem_kind=problem.kind) as planner:
#     result = planner.solve(problem)
#     plan = result.plan
#     if plan is not None:
#         print("%s returned:" % planner.name)
#         print(plan)
#     else:
#         print("No plan found.")