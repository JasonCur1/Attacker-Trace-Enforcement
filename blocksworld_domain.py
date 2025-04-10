from unified_planning.shortcuts import *
from unified_planning.model import Problem

def setup_blocksworld_domain(problem: Problem):
    block_type = UserType("block")

    # Objects
    blocks = [Object(name, block_type) for name in ["A", "B", "C"]]
    for b in blocks:
        problem.add_object(b)

    # Fluents
    on = Fluent("on", BoolType(), x=block_type, y=block_type)  # block x is on block y
    on_table = Fluent("on_table", BoolType(), x=block_type)    # block x is on table
    clear = Fluent("clear", BoolType(), x=block_type)          # block x has nothing on top
    holding = Fluent("holding", BoolType(), x=block_type)      # agent is holding block x
    hand_empty = Fluent("hand_empty", BoolType())              # agent is holding nothing

    # Add fluents
    for f in [on, on_table, clear, holding]:
        problem.add_fluent(f, default_initial_value=False)
    problem.add_fluent(hand_empty, default_initial_value=True)

    # --- Initial Configuration ---
    # Stack: A on B, B on table, C on table
    A, B, C = blocks
    problem.set_initial_value(on(A, B), True)
    problem.set_initial_value(on_table(B), True)
    problem.set_initial_value(on_table(C), True)
    problem.set_initial_value(clear(A), True)
    problem.set_initial_value(clear(C), True)
    problem.set_initial_value(clear(B), False)
    problem.set_initial_value(hand_empty(), True)

    # --- Actions ---

    # Pick up from table
    pick_up = InstantaneousAction("pick_up", x=block_type)
    [x] = pick_up.parameters
    pick_up.add_precondition(on_table(x))
    pick_up.add_precondition(clear(x))
    pick_up.add_precondition(hand_empty())
    pick_up.add_effect(on_table(x), False)
    pick_up.add_effect(clear(x), False)
    pick_up.add_effect(holding(x), True)
    pick_up.add_effect(hand_empty(), False)
    problem.add_action(pick_up)

    # Unstack from another block
    unstack = InstantaneousAction("unstack", x=block_type, y=block_type)
    x, y = unstack.parameters
    unstack.add_precondition(on(x, y))
    unstack.add_precondition(clear(x))
    unstack.add_precondition(hand_empty())
    unstack.add_effect(on(x, y), False)
    unstack.add_effect(clear(y), True)
    unstack.add_effect(clear(x), False)
    unstack.add_effect(holding(x), True)
    unstack.add_effect(hand_empty(), False)
    problem.add_action(unstack)

    # Put block on another block
    stack = InstantaneousAction("stack", x=block_type, y=block_type)
    x, y = stack.parameters
    stack.add_precondition(holding(x))
    stack.add_precondition(clear(y))
    stack.add_effect(on(x, y), True)
    stack.add_effect(clear(y), False)
    stack.add_effect(clear(x), True)
    stack.add_effect(holding(x), False)
    stack.add_effect(hand_empty(), True)
    problem.add_action(stack)

    # Put block on table
    put_down = InstantaneousAction("put_down", x=block_type)
    [x] = put_down.parameters
    put_down.add_precondition(holding(x))
    put_down.add_effect(on_table(x), True)
    put_down.add_effect(clear(x), True)
    put_down.add_effect(holding(x), False)
    put_down.add_effect(hand_empty(), True)
    problem.add_action(put_down)

    # --- Final Setup ---
    tracked_fluents = [on, on_table, clear]
    success_conditions = [hand_empty()]  # No block should be in hand

    return {
        "fluents_to_track": tracked_fluents,
        "success_conditions": success_conditions
    }
