from unified_planning.shortcuts import *
from unified_planning.model import Problem, Fluent

def setup_gridworld_domain(problem: Problem):
    # Define types
    tile_type = UserType("tile")
    agent_type = UserType("agent")

    attacker = Object("houdini", agent_type)
    guard = Object("blart", agent_type)
    problem.add_object(attacker)
    problem.add_object(guard)

    # Create grid tiles
    tiles = {}
    for i in range(5):
        for j in range(5):
            name = f"t{i}{j}"
            t = Object(name, tile_type)
            tiles[name] = t
            problem.add_object(t)

    # --- Fluents ---

    at = Fluent("at", BoolType(), a=agent_type, t=tile_type)
    diamond_stolen = Fluent("diamond_stolen", BoolType())
    furniture_at = Fluent("furniture_at", BoolType(), t=tile_type)
    no_trace_left = Fluent("no_trace_left", BoolType(), t=tile_type)
    able_to_be_cleaned = Fluent("able_to_be_cleaned", BoolType(), t=tile_type)
    attacker_visited = Fluent("attacker_visited", BoolType(), t=tile_type)
    guard_visited = Fluent("guard_visited", BoolType(), t=tile_type)
    connected = Fluent("connected", BoolType(), x=tile_type, y=tile_type)
    connected.symmetric = True
    next_in_path = Fluent("next_in_path", BoolType(), t1=tile_type, t2=tile_type)
    attacker_turn = Fluent("attacker_turn", BoolType())
    guard_turn = Fluent("guard_turn", BoolType())
    fail_state = Fluent("fail_state", BoolType())


    # Add fluents
    problem.add_fluent(at, default_initial_value=False)
    problem.add_fluent(diamond_stolen, default_initial_value=False)
    problem.add_fluent(furniture_at, default_initial_value=False)
    problem.add_fluent(no_trace_left, default_initial_value=False)
    problem.add_fluent(able_to_be_cleaned, default_initial_value=False)
    problem.add_fluent(attacker_visited, default_initial_value=False)
    problem.add_fluent(guard_visited, default_initial_value=False)
    problem.add_fluent(connected, default_initial_value=False)
    problem.add_fluent(next_in_path, default_initial_value=False)
    problem.add_fluent(attacker_turn, default_initial_value=True)  # Attacker goes first
    problem.add_fluent(guard_turn, default_initial_value=False)
    problem.add_fluent(fail_state, default_initial_value=False)

    # Initial values
    problem.set_initial_value(at(attacker, tiles["t00"]), True)
    problem.set_initial_value(at(guard, tiles["t20"]), True)

    # Furniture
    furniture_tiles = {"t10", "t20", "t30", "t11", "t21", "t12", "t32", "t34"}
    for t in furniture_tiles:
        problem.set_initial_value(furniture_at(tiles[t]), True)

    # All tiles start with no trace
    for tile in tiles.values():
        problem.set_initial_value(no_trace_left(tile), True)

    # Connected tiles
    for i in range(5):
        for j in range(5):
            curr = tiles[f"t{i}{j}"]
            if j > 0: problem.set_initial_value(connected(curr, tiles[f"t{i}{j-1}"]), True)
            if j < 4: problem.set_initial_value(connected(curr, tiles[f"t{i}{j+1}"]), True)
            if i > 0: problem.set_initial_value(connected(curr, tiles[f"t{i-1}{j}"]), True)
            if i < 4: problem.set_initial_value(connected(curr, tiles[f"t{i+1}{j}"]), True)

    # Guard path
    path = ["t20", "t21", "t22", "t32", "t42", "t41", "t40", "t30"]
    for i in range(len(path)):
        curr = path[i]
        next_tile = path[(i+1) % len(path)]
        problem.set_initial_value(next_in_path(tiles[curr], tiles[next_tile]), True)


    # --- Actions ---

    # Attacker move
    move = InstantaneousAction("move", curr=tile_type, to=tile_type, a=agent_type)
    curr, to, a = move.parameters
    move.add_precondition(at(a, curr))
    move.add_precondition(connected(curr, to))
    move.add_precondition(Equals(a, attacker))
    move.add_precondition(attacker_turn())
    move.add_effect(no_trace_left(to), False, furniture_at(to))
    move.add_effect(able_to_be_cleaned(curr), True, furniture_at(curr))
    move.add_effect(attacker_visited(to), True)
    move.add_effect(at(a, curr), False)
    move.add_effect(at(a, to), True)
    move.add_effect(attacker_turn(), False)
    move.add_effect(guard_turn(), True)
    problem.add_action(move)

    # Wait
    wait = InstantaneousAction("wait", loc=tile_type, a=agent_type)
    loc, a = wait.parameters
    wait.add_precondition(at(a, loc))
    wait.add_precondition(Equals(a, attacker))
    wait.add_precondition(attacker_turn())
    wait.add_effect(attacker_turn(), False)
    wait.add_effect(guard_turn(), True)
    problem.add_action(wait)

    # Clean
    clean = InstantaneousAction("clean", curr=tile_type, a=agent_type)
    curr, a = clean.parameters
    clean.add_precondition(at(a, curr))
    clean.add_precondition(Not(no_trace_left(curr)))
    clean.add_precondition(able_to_be_cleaned(curr))
    clean.add_precondition(attacker_visited(curr))
    clean.add_precondition(attacker_turn())
    clean.add_effect(no_trace_left(curr), True)
    clean.add_effect(able_to_be_cleaned(curr), False)
    clean.add_effect(attacker_turn(), False)
    clean.add_effect(guard_turn(), True)
    problem.add_action(clean)

    # Steal
    steal = InstantaneousAction("steal", curr=tile_type, a=agent_type)
    curr, a = steal.parameters
    steal.add_precondition(at(a, curr))
    steal.add_precondition(Equals(curr, tiles["t31"]))  # Hardcoded diamond location
    steal.add_precondition(attacker_turn())
    steal.add_effect(diamond_stolen(), True)
    steal.add_effect(attacker_turn(), False)
    steal.add_effect(guard_turn(), True)
    problem.add_action(steal)

    # Guard move
    guard_move = InstantaneousAction("guard_move", curr=tile_type, to=tile_type, a=agent_type)
    curr, to, a = guard_move.parameters
    guard_move.add_precondition(Equals(a, guard))
    guard_move.add_precondition(at(a, curr))
    guard_move.add_precondition(next_in_path(curr, to))
    guard_move.add_precondition(guard_turn())
    guard_move.add_effect(at(a, curr), False)
    guard_move.add_effect(at(a, to), True)
    guard_move.add_effect(guard_visited(to), True)
    guard_move.add_effect(guard_turn(), False)
    guard_move.add_effect(attacker_turn(), True)
    guard_move.add_effect(fail_state(), True, at(attacker, to))
    guard_move.add_effect(fail_state(), True, Not(no_trace_left(to))) # confusing.. I know
    problem.add_action(guard_move)

    # --- Final Configuration ---
    return {
        "success_conditions": [
            diamond_stolen(),
            Not(fail_state())
        ]
    }