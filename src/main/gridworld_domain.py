from unified_planning.shortcuts import *
from unified_planning.model import Problem, Fluent
import random

def setup_gridworld_domain(problem: Problem):
    grid_size = (9, 9)
    diamond_location = "t01"
    num_timesteps = 20
    random.seed(42)

    # Define types
    tile_type = UserType("tile")
    agent_type = UserType("agent")
    time_type = UserType("time")

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

    # Create time objects
    timesteps = {}
    for i in range(num_timesteps):
        name = f"time{i}"
        t = Object(name, time_type)
        timesteps[name] = t
        problem.add_object(t)

    # --- Fluents ---
    #turn_guard = Fluent("turn_guard", BoolType())
    escaped = Fluent("escaped", BoolType())
    is_current_timestep = Fluent("is_current_timestep", BoolType(), t=time_type)
    is_next_timestep = Fluent("is_next_timestep", BoolType(), t1=time_type, t2=time_type)
    at = Fluent("at", BoolType(), a=agent_type, t=tile_type)
    diamond_stolen = Fluent("diamond_stolen", BoolType())
    diamond_at = Fluent("diamond_at", BoolType(), t=tile_type)
    no_trace_left = Fluent("no_trace_left", BoolType(), t=tile_type)
    connected = Fluent("connected", BoolType(), x=tile_type, y=tile_type)
    connected.symmetric = True
    is_trace_tile = Fluent("is_trace_tile", BoolType(), t=tile_type)
    attacker_caught = Fluent("attacker_caught", BoolType())


    # Add fluents
    #problem.add_fluent(turn_guard, default_initial_value=True)
    problem.add_fluent(escaped, default_initial_value=False)
    problem.add_fluent(is_current_timestep, default_initial_value=False)
    problem.add_fluent(is_next_timestep, default_initial_value=False)
    problem.add_fluent(at, default_initial_value=False)
    problem.add_fluent(diamond_stolen, default_initial_value=False)
    problem.add_fluent(diamond_at, default_initial_value=False)
    problem.add_fluent(no_trace_left, default_initial_value=True)
    problem.add_fluent(connected, default_initial_value=False)
    problem.add_fluent(is_trace_tile, default_initial_value=False)
    problem.add_fluent(attacker_caught, default_initial_value=False)

    # --- Initial values ---
    problem.set_initial_value(at(attacker, tiles["t00"]), True)
    problem.set_initial_value(at(guard, tiles[f"t{grid_size[0]-1}{grid_size[1]-1}"]), True) # guard starts bottom right
    problem.set_initial_value(diamond_at(tiles[diamond_location]), True)

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
            if j < grid_size[1] - 1: problem.set_initial_value(connected(curr, tiles[f"t{i}{j+1}"]), True)
            if i > 0: problem.set_initial_value(connected(curr, tiles[f"t{i-1}{j}"]), True)
            if i < grid_size[0] - 1: problem.set_initial_value(connected(curr, tiles[f"t{i+1}{j}"]), True)

    # Time
    problem.set_initial_value(is_current_timestep(timesteps["time0"]), True)
    for i in range(num_timesteps - 1):
        problem.set_initial_value(is_next_timestep(timesteps[f"time{i}"], timesteps[f"time{i+1}"]), True)

    # --- Guard (Leader) Action (prefixed with fix_) ---

    # Leader move (now the guard can move to any connected tile)
    fix_move = InstantaneousAction("fix_move", curr=tile_type, to=tile_type, a=agent_type, t1=time_type, t2=time_type)
    curr, to, a, t1, t2 = fix_move.parameters
    #fix_move.add_precondition(turn_guard)
    fix_move.add_precondition(Equals(a, guard))
    fix_move.add_precondition(at(a, curr))
    fix_move.add_precondition(connected(curr, to))
    fix_move.add_precondition(is_current_timestep(t1))
    fix_move.add_precondition(is_next_timestep(t1, t2))
    #fix_move.add_effect(turn_guard, False)
    fix_move.add_effect(at(a, curr), False)
    fix_move.add_effect(at(a, to), True)
    fix_move.add_effect(attacker_caught(), True, at(attacker, to))
    fix_move.add_effect(attacker_caught(), True, Not(no_trace_left(to)))
    fix_move.add_effect(is_current_timestep(t1), False)
    fix_move.add_effect(is_current_timestep(t2), True)
    problem.add_action(fix_move)

    fix_wait = InstantaneousAction("fix_wait", loc=tile_type, a=agent_type, t1=time_type, t2=time_type)
    loc, a, t1, t2 = fix_wait.parameters
    #fix_wait.add_precondition(turn_guard)
    fix_wait.add_precondition(at(a, loc))
    fix_wait.add_precondition(Equals(a, guard))
    fix_wait.add_precondition(is_current_timestep(t1))
    fix_wait.add_precondition(is_next_timestep(t1, t2))
    #fix_wait.add_effect(turn_guard, False)
    fix_wait.add_effect(at(a, loc), True) # Do nothing
    fix_wait.add_effect(is_current_timestep(t1), False)
    fix_wait.add_effect(is_current_timestep(t2), True)
    problem.add_action(fix_wait)


    # --- Attacker (Follower/Adversary) Actions (prefixed with attack_) ---

    # Follower move
    attack_move = InstantaneousAction("attack_move", curr=tile_type, to=tile_type, a=agent_type, t1=time_type, t2=time_type)
    curr, to, a, t1, t2 = attack_move.parameters
    #attack_move.add_precondition(Not(turn_guard))
    attack_move.add_precondition(at(a, curr))
    attack_move.add_precondition(connected(curr, to))
    attack_move.add_precondition(Equals(a, attacker))
    attack_move.add_precondition(is_current_timestep(t1))
    attack_move.add_precondition(is_next_timestep(t1, t2))
    #attack_move.add_effect(turn_guard, True)
    attack_move.add_effect(no_trace_left(to), False, is_trace_tile(to))
    attack_move.add_effect(at(a, curr), False)
    attack_move.add_effect(at(a, to), True)
    attack_move.add_effect(attacker_caught(), True, at(guard, to))
    attack_move.add_effect(is_current_timestep(t1), False)
    attack_move.add_effect(is_current_timestep(t2), True)
    problem.add_action(attack_move)

    # Follower wait
    attack_wait = InstantaneousAction("attack_wait", loc=tile_type, a=agent_type, t1=time_type, t2=time_type)
    loc, a, t1, t2 = attack_wait.parameters
    #attack_wait.add_precondition(Not(turn_guard))
    attack_wait.add_precondition(at(a, loc))
    attack_wait.add_precondition(Equals(a, attacker))
    attack_wait.add_precondition(is_current_timestep(t1))
    attack_wait.add_precondition(is_next_timestep(t1, t2))
    #attack_wait.add_effect(turn_guard, True)
    attack_wait.add_effect(at(a, loc), True)
    attack_wait.add_effect(is_current_timestep(t1), False)
    attack_wait.add_effect(is_current_timestep(t2), True)
    problem.add_action(attack_wait)

    # Follower clean
    attack_clean = InstantaneousAction("attack_clean", curr=tile_type, a=agent_type, t1=time_type, t2=time_type)
    curr, a, t1, t2 = attack_clean.parameters
    #attack_clean.add_precondition(Not(turn_guard))
    attack_clean.add_precondition(at(a, curr))
    attack_clean.add_precondition(Not(no_trace_left(curr))) # Tile must be dirty
    attack_clean.add_precondition(is_current_timestep(t1))
    attack_clean.add_precondition(is_next_timestep(t1, t2))
    #attack_clean.add_effect(turn_guard, True)
    attack_clean.add_effect(no_trace_left(curr), True)
    attack_clean.add_effect(is_current_timestep(t1), False)
    attack_clean.add_effect(is_current_timestep(t2), True)
    problem.add_action(attack_clean)

    # Follower steal
    attack_steal = InstantaneousAction("attack_steal", curr=tile_type, a=agent_type, t1=time_type, t2=time_type)
    curr, a, t1, t2 = attack_steal.parameters
    #attack_steal.add_precondition(Not(turn_guard))
    attack_steal.add_precondition(at(a, curr))
    attack_steal.add_precondition(diamond_at(curr))  # Hardcoded diamond location
    attack_steal.add_precondition(is_current_timestep(t1))
    attack_steal.add_precondition(is_next_timestep(t1, t2))
    #attack_steal.add_effect(turn_guard, True)
    attack_steal.add_effect(diamond_stolen(), True)
    attack_steal.add_effect(is_current_timestep(t1), False)
    attack_steal.add_effect(is_current_timestep(t2), True)
    problem.add_action(attack_steal)

    attack_escape = InstantaneousAction("attack_escape", curr=tile_type, a=agent_type, t1=time_type, t2=time_type)
    curr, a, t1, t2 = attack_escape.parameters
    #attack_escape.add_precondition(Not(turn_guard))
    attack_escape.add_precondition(at(a, curr))
    attack_escape.add_precondition(Equals(curr, tiles["t00"]))
    attack_escape.add_precondition(is_current_timestep(t1))
    attack_escape.add_precondition(is_next_timestep(t1, t2))
    attack_escape.add_precondition(diamond_stolen())
    #attack_escape.add_effect(turn_guard, True)
    attack_escape.add_effect(escaped(), True)
    attack_escape.add_effect(is_current_timestep(t1), False)
    attack_escape.add_effect(is_current_timestep(t2), True)
    problem.add_action(attack_escape)



    # --- Final Configuration ---
    return {
        "success_conditions": [
            diamond_stolen(),
            Not(attacker_caught()),
            escaped(),
            *[no_trace_left(tile) for tile in random_trace_tiles] # * = unpack contents of this list
        ]
    }