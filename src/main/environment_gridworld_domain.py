from unified_planning.shortcuts import *
from unified_planning.model import Problem, Fluent
import random

random.seed(42)

def setup_domain(problem: Problem):
    grid_size = (3, 3)
    diamond_location = "t21"
    attacker_starting_position = "t00"
    number_of_trace_tiles = 1


    # --- Types ---
    tile_type = UserType("tile")
    agent_type = UserType("agent")

    attacker = Object("adversary_houdini", agent_type)
    architect = Object("leader_bob", agent_type)
    problem.add_object(attacker)
    problem.add_object(architect)

    # --- Create grid tiles ---
    tiles = {}
    for i in range(grid_size[0]):
        for j in range(grid_size[1]):
            name = f"t{i}{j}"
            t = Object(name, tile_type)
            tiles[name] = t
            problem.add_object(t)

    # --- Fluents ---
    connected = Fluent("static_connected", BoolType(), x=tile_type, y=tile_type)
    connected.symmetric = True
    at = Fluent("static_at", BoolType(), a=agent_type, t=tile_type)
    diamond_at = Fluent("static_diamond_at", BoolType(), t=tile_type)
    diamond_stolen = Fluent("diamond_stolen", BoolType())
    escaped = Fluent("escaped", BoolType())
    is_trace_tile = Fluent("static_is_trace_tile", BoolType(), t=tile_type)
    no_trace_left = Fluent("no_trace_left", BoolType(), t=tile_type)

    problem.add_fluent(connected, default_initial_value=False)
    problem.add_fluent(at, default_initial_value=False)
    problem.add_fluent(diamond_at, default_initial_value=False)
    problem.add_fluent(diamond_stolen, default_initial_value=False)
    problem.add_fluent(escaped, default_initial_value=False)
    problem.add_fluent(is_trace_tile, default_initial_value=False)
    problem.add_fluent(no_trace_left)

    # --- Initial Values ---
    problem.set_initial_value(at(attacker, tiles[attacker_starting_position]), True)
    problem.set_initial_value(diamond_at(tiles[diamond_location]), True)

    for tile in tiles.values():
        problem.set_initial_value(no_trace_left(tile), True)

    # Trace tile selection
    all_tiles = list(tiles.values())
    random_trace_tiles = random.sample(all_tiles, k=number_of_trace_tiles)
    for tile in random_trace_tiles:
        problem.set_initial_value(is_trace_tile(tile), True) # Fluent used be attacker to determine if tile is dirtied

    # Connected tiles
    for i in range(grid_size[0]):
        for j in range(grid_size[1]):
            curr = tiles[f"t{i}{j}"]
            if j > 0: problem.set_initial_value(connected(curr, tiles[f"t{i}{j-1}"]), True)
            if j < grid_size[1] - 1: problem.set_initial_value(connected(curr, tiles[f"t{i}{j+1}"]), True)
            if i > 0: problem.set_initial_value(connected(curr, tiles[f"t{i-1}{j}"]), True)
            if i < grid_size[0] - 1: problem.set_initial_value(connected(curr, tiles[f"t{i+1}{j}"]), True)

    # ----- Actions -----
    # --- Architect (Leader) actions (prefixed with fix_) ---
    fix_place_wall = InstantaneousAction("fix_place_wall", curr=tile_type, to=tile_type, a=agent_type, b=agent_type)
    curr, to, a, b = fix_place_wall.parameters

    # --- Agent Assignment Preconditions ---
    fix_place_wall.add_precondition(Equals(a, architect))
    fix_place_wall.add_precondition(Equals(b, attacker))
    fix_place_wall.add_precondition(connected(curr, to)) # Matches (static_connected ?curr ?to)
    fix_place_wall.add_precondition(connected(to, curr)) # Matches (static_connected ?to ?curr)
    fix_place_wall.add_precondition(Not(diamond_at(curr))) # Matches (not (static_diamond_at ?curr))
    fix_place_wall.add_precondition(Not(diamond_at(to)))   # Matches (not (static_diamond_at ?to))
    fix_place_wall.add_precondition(Not(at(b, curr))) # Matches (not (static_at ?b ?curr))
    fix_place_wall.add_precondition(Not(at(b, to)))   # Matches (not (static_at ?b ?to))
    fix_place_wall.add_effect(connected(curr, to), False) # Matches (not (static_connected ?curr ?to))
    fix_place_wall.add_effect(connected(to, curr), False) # Matches (not (static_connected ?to ?curr))
    problem.add_action(fix_place_wall)

    # for i in range(grid_size[0]):
    #     for j in range(grid_size[1]):
    #         curr = tiles[f"t{i}{j}"]

    #         # Not allowed to place walls on starting tile or diamond tile
    #         if curr.name == "t00" or curr.name == diamond_location:
    #             continue

    #         # Define a new action for each tile
    #         action_name = f"fix_place_wall_{curr.name}"
    #         fix_place_wall_action = InstantaneousAction(action_name, a=agent_type)
    #         a = fix_place_wall_action.parameters

    #         fix_place_wall_action.add_precondition(Equals(a, architect))

    #         # Check for and add preconditions and effects for each neighbor
    #         if j > 0:
    #             left_tile = tiles[f"t{i}{j-1}"]
    #             fix_place_wall_action.add_precondition(connected(curr, left_tile))
    #             fix_place_wall_action.add_effect(connected(curr, left_tile), False)

    #         if j < grid_size[1] - 1:
    #             right_tile = tiles[f"t{i}{j+1}"]
    #             fix_place_wall_action.add_precondition(connected(curr, right_tile))
    #             fix_place_wall_action.add_effect(connected(curr, right_tile), False)

    #         if i > 0:
    #             above_tile = tiles[f"t{i-1}{j}"]
    #             fix_place_wall_action.add_precondition(connected(curr, above_tile))
    #             fix_place_wall_action.add_effect(connected(curr, above_tile), False)

    #         if i < grid_size[0] - 1:
    #             below_tile = tiles[f"t{i+1}{j}"]
    #             fix_place_wall_action.add_precondition(connected(curr, below_tile))
    #             fix_place_wall_action.add_effect(connected(curr, below_tile), False)

    #         problem.add_action(fix_place_wall_action)

    fix_place_trace_tile = InstantaneousAction("fix_place_trace_tile", curr=tile_type, a=agent_type)
    curr, a = fix_place_trace_tile.parameters
    fix_place_trace_tile.add_precondition(Equals(a, architect))
    fix_place_trace_tile.add_effect(is_trace_tile(curr), True)
    problem.add_action(fix_place_trace_tile)

    # --- Attacker (Follower) actions (prefixed with attack_) ---
    attack_move = InstantaneousAction("attack_move", curr=tile_type, to=tile_type, a=agent_type)
    curr, to, a = attack_move.parameters
    attack_move.add_precondition(at(a, curr))
    attack_move.add_precondition(connected(curr, to))
    attack_move.add_precondition(Equals(a, attacker))
    attack_move.add_effect(at(a, curr), False)
    attack_move.add_effect(at(a, to), True)
    attack_move.add_effect(no_trace_left(to), False, is_trace_tile(to))
    problem.add_action(attack_move)

    attack_wait = InstantaneousAction("attack_wait", curr=tile_type, a=agent_type)
    curr, a = attack_wait.parameters
    attack_wait.add_precondition(at(a, curr))
    attack_wait.add_precondition(Equals(a, attacker))
    attack_wait.add_effect(at(a, curr), True)
    problem.add_action(attack_wait)

    attack_clean = InstantaneousAction("attack_clean", curr=tile_type, a=agent_type)
    curr, a = attack_clean.parameters
    attack_clean.add_precondition(at(a, curr))
    attack_clean.add_precondition(Equals(a, attacker))
    attack_clean.add_precondition(Not(no_trace_left(curr))) # Tile must be dirty
    attack_clean.add_effect(no_trace_left(curr), True)
    problem.add_action(attack_clean)

    attack_steal = InstantaneousAction("attack_steal", curr=tile_type, a=agent_type)
    curr, a = attack_steal.parameters
    attack_steal.add_precondition(at(a, curr))
    attack_steal.add_precondition(Equals(a, attacker))
    attack_steal.add_precondition(diamond_at(curr))
    attack_steal.add_effect(diamond_stolen(), True)
    problem.add_action(attack_steal)

    attack_escape = InstantaneousAction("attack_escape", curr=tile_type, a=agent_type)
    curr, a = attack_escape.parameters
    attack_escape.add_precondition(at(a, curr))
    attack_escape.add_precondition(Equals(a, attacker))
    attack_escape.add_precondition(diamond_stolen())
    attack_escape.add_precondition(Equals(curr, tiles["t00"]))
    attack_escape.add_effect(escaped(), True)
    problem.add_action(attack_escape)

    # --- Domain Specific Goals ---
    return {
        "success_conditions": [
            diamond_stolen(),
            escaped(),
        ]
    }