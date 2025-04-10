from unified_planning.shortcuts import *
from unified_planning.model import Problem, Fluent

def setup_blocksworld_domain(problem: Problem):
    block_type = UserType("block")

    # Create blocks
    A = Object("A", block_type)
    B = Object("B", block_type)
    C = Object("C", block_type)
    problem.add_objects([A, B, C])

    # Fluents
    on = Fluent("on", BoolType(), top=block_type, bottom=block_type)
    on_table = Fluent("on_table", BoolType(), b=block_type)
    clear = Fluent("clear", BoolType(), b=block_type)
    holding = Fluent("holding", BoolType(), b=block_type)
    hand_empty = Fluent("hand_empty", BoolType())
    a_on_c_achieved = Fluent("a_on_c_achieved", BoolType())

    problem.add_fluent(on, default_initial_value=False)
    problem.add_fluent(on_table, default_initial_value=False)
    problem.add_fluent(clear, default_initial_value=False)
    problem.add_fluent(holding, default_initial_value=False)
    problem.add_fluent(hand_empty, default_initial_value=True)
    problem.add_fluent(a_on_c_achieved, default_initial_value=False)

    # Initial state
    problem.set_initial_value(on(B, A), True)
    problem.set_initial_value(on_table(A), True)
    problem.set_initial_value(on_table(C), True)
    problem.set_initial_value(clear(B), True)
    problem.set_initial_value(clear(C), True)
    problem.set_initial_value(clear(A), False)
    problem.set_initial_value(hand_empty(), True)

    # Actions
    pickup = InstantaneousAction("pickup", b=block_type)
    b = pickup.parameter("b")
    pickup.add_precondition(on_table(b))
    pickup.add_precondition(clear(b))
    pickup.add_precondition(hand_empty())
    pickup.add_effect(on_table(b), False)
    pickup.add_effect(holding(b), True)
    pickup.add_effect(clear(b), False)
    pickup.add_effect(hand_empty(), False)
    problem.add_action(pickup)

    putdown = InstantaneousAction("putdown", b=block_type)
    b = putdown.parameter("b")
    putdown.add_precondition(holding(b))
    putdown.add_effect(on_table(b), True)
    putdown.add_effect(clear(b), True)
    putdown.add_effect(holding(b), False)
    putdown.add_effect(hand_empty(), True)
    problem.add_action(putdown)

    stack = InstantaneousAction("stack", top=block_type, bottom=block_type)
    top, bottom = stack.parameters
    stack.add_precondition(holding(top))
    stack.add_precondition(clear(bottom))
    stack.add_effect(holding(top), False)
    stack.add_effect(clear(top), True)
    stack.add_effect(clear(bottom), False)
    stack.add_effect(on(top, bottom), True)
    stack.add_effect(hand_empty(), True)
    stack.add_effect(a_on_c_achieved, True, And(Equals(top, A), Equals(bottom, C)))

    problem.add_action(stack)

    unstack = InstantaneousAction("unstack", top=block_type, bottom=block_type)
    top, bottom = unstack.parameters
    unstack.add_precondition(on(top, bottom))
    unstack.add_precondition(clear(top))
    unstack.add_precondition(hand_empty())
    unstack.add_effect(on(top, bottom), False)
    unstack.add_effect(clear(bottom), True)
    unstack.add_effect(holding(top), True)
    unstack.add_effect(clear(top), False)
    unstack.add_effect(hand_empty(), False)
    problem.add_action(unstack)

    # --- Domain-guided goals ---
    restore_conditions = [
        Iff(on(B, A), True),
        Iff(on_table(A), True),
        Iff(on_table(C), True),
        Iff(clear(B), True),
        Iff(clear(C), True),
        Iff(clear(A), False),
        Iff(hand_empty(), True)
    ]

    success_conditions = [a_on_c_achieved()]

    return {
        "restore_conditions": restore_conditions,
        "success_conditions": success_conditions
    }

