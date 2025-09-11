from unified_planning.shortcuts import *
from unified_planning.model import Problem, Fluent
import random

def setup_gridworld_domain(problem: Problem):
    grid_size = (5, 5)

    # Define types
    tile_type = UserType("tile")
    agent_type = UserType("agent")

    attacker = Object("adversary_houdini", agent_type)
    guard = Object("leader_blart", agent_type)
    problem.add_object(attacker)
    problem.add_object(guard)

    # Create grid tiles
    tiles = {}
    for i in range(grid_size[0]):
        for j in range(grid_size[1]):
            name = f"t{i}{j}"
            t = Object(name, tile_type)
            tiles[name] = t
            problem.add_object(t)

    # --- Fluents ---

    at = Fluent("at", BoolType(), a=agent_type, t=tile_type)
    diamond_stolen = Fluent("diamond_stolen", BoolType())
    no_trace_left = Fluent("no_trace_left", BoolType(), t=tile_type)
    connected = Fluent("connected", BoolType(), x=tile_type, y=tile_type)
    connected.symmetric = True
    is_trace_tile = Fluent("is_trace_tile", BoolType(), t=tile_type)
    fail_state = Fluent("fail_state", BoolType())


    # Add fluents
    problem.add_fluent(at, default_initial_value=False)
    problem.add_fluent(diamond_stolen, default_initial_value=False)
    problem.add_fluent(no_trace_left, default_initial_value=False)
    problem.add_fluent(connected, default_initial_value=False)
    problem.add_fluent(is_trace_tile, default_initial_value=False)
    problem.add_fluent(fail_state, default_initial_value=False)

    # Initial values
    problem.set_initial_value(at(attacker, tiles["t00"]), True)
    problem.set_initial_value(at(guard, tiles["t40"]), True)

    # All tiles start with no trace
    for tile in tiles.values():
        problem.set_initial_value(no_trace_left(tile), True)

    # Select random tiles to be "trace" tiles
    all_tiles = list(tiles.values())
    random_trace_tiles = random.sample(all_tiles, k=5) # Choose 5 random tiles
    for tile in random_trace_tiles:
        problem.set_initial_value(is_trace_tile(tile), True)

    # Connected tiles
    for i in range(grid_size[0]):
        for j in range(grid_size[1]):
            curr = tiles[f"t{i}{j}"]
            if j > 0: problem.set_initial_value(connected(curr, tiles[f"t{i}{j-1}"]), True)
            if j < 4: problem.set_initial_value(connected(curr, tiles[f"t{i}{j+1}"]), True)
            if i > 0: problem.set_initial_value(connected(curr, tiles[f"t{i-1}{j}"]), True)
            if i < 4: problem.set_initial_value(connected(curr, tiles[f"t{i+1}{j}"]), True)


    # --- Guard (Leader) Action (prefixed with fix_) ---

    # Follower move (now the guard can move to any connected tile)
    fix_move = InstantaneousAction("fix_move", curr=tile_type, to=tile_type, a=agent_type)
    curr, to, a = fix_move.parameters
    fix_move.add_precondition(Equals(a, guard))
    fix_move.add_precondition(at(a, curr))
    fix_move.add_precondition(connected(curr, to))
    fix_move.add_effect(at(a, curr), False)
    fix_move.add_effect(at(a, to), True)
    fix_move.add_effect(fail_state(), True, at(attacker, to))
    fix_move.add_effect(fail_state(), True, Not(no_trace_left(to)))
    problem.add_action(fix_move)

    fix_wait = InstantaneousAction("fix_wait", loc=tile_type, a=agent_type)
    loc, a = fix_wait.parameters
    fix_wait.add_precondition(at(a, loc))
    fix_wait.add_precondition(Equals(a, guard))
    fix_wait.add_effect(at(a, loc), True) # Do nothing
    problem.add_action(fix_wait)


    # --- Attacker (Follower/Adversary) Actions (prefixed with attack_) ---

    # Leader move
    attack_move = InstantaneousAction("attack_move", curr=tile_type, to=tile_type, a=agent_type)
    curr, to, a = attack_move.parameters
    attack_move.add_precondition(at(a, curr))
    attack_move.add_precondition(connected(curr, to))
    attack_move.add_precondition(Equals(a, attacker))
    attack_move.add_effect(no_trace_left(to), False, is_trace_tile(to))
    attack_move.add_effect(at(a, curr), False)
    attack_move.add_effect(at(a, to), True)
    attack_move.add_effect(fail_state(), True, at(guard, to))
    problem.add_action(attack_move)

    # Leader wait
    attack_wait = InstantaneousAction("attack_wait", loc=tile_type, a=agent_type)
    loc, a = attack_wait.parameters
    attack_wait.add_precondition(at(a, loc))
    attack_wait.add_precondition(Equals(a, attacker))
    attack_wait.add_effect(at(a, loc), True)
    problem.add_action(attack_wait)

    # Leader clean
    attack_clean = InstantaneousAction("attack_clean", curr=tile_type, a=agent_type)
    curr, a = attack_clean.parameters
    attack_clean.add_precondition(at(a, curr))
    attack_clean.add_precondition(Not(no_trace_left(curr))) # Tile must be dirty
    attack_clean.add_effect(no_trace_left(curr), True)
    problem.add_action(attack_clean)

    # Leader steal
    attack_steal = InstantaneousAction("attack_steal", curr=tile_type, a=agent_type)
    curr, a = attack_steal.parameters
    attack_steal.add_precondition(at(a, curr))
    attack_steal.add_precondition(Equals(curr, tiles["t44"]))  # Hardcoded diamond location
    attack_steal.add_effect(diamond_stolen(), True)
    problem.add_action(attack_steal)


    # --- Final Configuration ---
    return {
        "success_conditions": [
            diamond_stolen(),
            Not(fail_state())
        ]
    }