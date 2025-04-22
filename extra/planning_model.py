from unified_planning.shortcuts import *
from unified_planning.model.problem import Problem
import unified_planning as up

def create_problem():
    problem = Problem('museum')

    # Define Types (Objects)
    tile_type = UserType("tile")
    agent_type = UserType("agent")

    # Define attacker
    attacker_obj = Object("houdini", agent_type)
    problem.add_object(attacker_obj)

    # Define guard
    guard_obj = Object("blart", agent_type)
    problem.add_object(guard_obj)

    # Define Predicates (relationships)
    at = Fluent("at", BoolType(), a=agent_type, t=tile_type) # Specified agent is at this tile
    diamond_stolen = Fluent("diamond_stolen", BoolType())  # Has the diamond been stolen?
    furniture_at = Fluent("furniture_at", BoolType(), t=tile_type)  # Furniture is at this tile
    trace_left = Fluent("trace_left", BoolType(), t=tile_type)  # Whether a trace is left on this tile
    able_to_be_cleaned = Fluent("able_to_be_cleaned", BoolType(), t=tile_type) # Is this tile able to be cleaned (prevents cleaning as the attacker moves)
    attacker_visited = Fluent("attacker_visited", BoolType(), t=tile_type) # Has the attacker visited this tile before?
    guard_visited = Fluent("guard_visited", BoolType(), t=tile_type)
    connected = Fluent("connected", BoolType(), x=tile_type, y=tile_type)
    connected.symmetric = True
    fail_state = Fluent("fail_state", BoolType())

    # Add next tile fluent for guard path
    next_in_path = Fluent("next_in_path", BoolType(), t1=tile_type, t2=tile_type)

    # Add a turn counter to alternate between guard and attacker
    attacker_turn = Fluent("attacker_turn", BoolType())
    guard_turn = Fluent("guard_turn", BoolType())

    problem.add_fluent(at, default_initial_value=False)
    problem.add_fluent(diamond_stolen, default_initial_value=False)
    problem.add_fluent(furniture_at, default_initial_value=False)
    problem.add_fluent(trace_left, default_initial_value=False)
    problem.add_fluent(able_to_be_cleaned, default_initial_value=False)
    problem.add_fluent(attacker_visited, default_initial_value=False)
    problem.add_fluent(guard_visited, default_initial_value=False)
    problem.add_fluent(connected, default_initial_value=False)
    problem.add_fluent(next_in_path, default_initial_value=False)
    problem.add_fluent(attacker_turn, default_initial_value=True)  # Attacker goes first
    problem.add_fluent(guard_turn, default_initial_value=False)
    problem.add_fluent(fail_state, default_initial_value=False)

    # Initialize the world
    tiles = {}
    for i in range(5):
        for j in range(5):
            t_name = f"t{i}{j}"
            t = Object(t_name, tile_type)
            tiles[t_name] = t
            problem.add_object(t)

    # Define Actions for attacker
    move = InstantaneousAction("move", curr=tile_type, to=tile_type, a=agent_type)
    curr, to, a = move.parameters
    move.add_precondition(at(a, curr))
    move.add_precondition(connected(curr, to))
    move.add_precondition(Equals(a, attacker_obj))  # Only attacker can use this action
    move.add_precondition(attacker_turn())  # Can only move on attacker's turn
    move.add_effect(trace_left(to), True, furniture_at(to)) # Conditional effect: leave a trace if moving to a furniture tile
    move.add_effect(able_to_be_cleaned(curr), True, furniture_at(curr)) # Conditional effect: Set "able to be cleaned" flag when leaving a furniture tile
    move.add_effect(attacker_visited(to), True)
    move.add_effect(at(a, curr), False)
    move.add_effect(at(a, to), True)
    move.add_effect(attacker_turn(), False)  # End attacker's turn
    move.add_effect(guard_turn(), True)  # Start guard's turn
    problem.add_action(move)

    # Modify clean action to only work when we haven't been on the tile in this visit
    clean = InstantaneousAction("clean", curr=tile_type, a=agent_type)
    curr, a = clean.parameters
    clean.add_precondition(at(a, curr))
    clean.add_precondition(trace_left(curr))  # Can only clean if a trace is left
    clean.add_precondition(able_to_be_cleaned(curr))
    clean.add_precondition(attacker_visited(curr))  # Tile must have been visited before
    clean.add_precondition(attacker_turn())  # Can only clean on attacker's turn
    clean.add_effect(trace_left(curr), False)  # Cleaning removes the trace
    clean.add_effect(able_to_be_cleaned(curr), False)
    clean.add_effect(attacker_turn(), False)  # End attacker's turn
    clean.add_effect(guard_turn(), True)  # Start guard's turn
    problem.add_action(clean)

    # Fix the steal action to properly reference the current tile
    steal = InstantaneousAction("steal", curr=tile_type, a=agent_type)
    curr, a = steal.parameters
    steal.add_precondition(at(a, curr))  # Must be at curr tile
    steal.add_precondition(Equals(curr, tiles["t31"]))  # The diamond is at t31
    steal.add_precondition(attacker_turn())  # Can only steal on attacker's turn
    steal.add_effect(diamond_stolen(), True)
    steal.add_effect(attacker_turn(), False)  # End attacker's turn
    steal.add_effect(guard_turn(), True)  # Start guard's turn
    problem.add_action(steal)

    # Updated guard_move action
    guard_move = InstantaneousAction("guard_move", curr=tile_type, to=tile_type, a=agent_type)
    curr, to, a = guard_move.parameters
    guard_move.add_precondition(Equals(a, guard_obj))
    guard_move.add_precondition(at(a, curr))
    guard_move.add_precondition(next_in_path(curr, to))
    guard_move.add_precondition(guard_turn())  # Can only move on guard's turn
    guard_move.add_effect(at(a, curr), False)
    guard_move.add_effect(at(a, to), True)
    guard_move.add_effect(guard_visited(to), True)
    guard_move.add_effect(guard_turn(), False)  # End guard's turn
    guard_move.add_effect(attacker_turn(), True)  # Start attacker's turn
    guard_move.add_effect(fail_state, True, at(attacker_obj, to))  # Fail if attacker is on the same tile
    guard_move.add_effect(fail_state, True, trace_left(to))  # Fail if there is a trace on the tile
    problem.add_action(guard_move)

    # Initial Attacker Position
    problem.set_initial_value(at(attacker_obj, tiles["t00"]), True)

    # Initial Guard Position
    problem.set_initial_value(at(guard_obj, tiles["t20"]), True)

    # Define Adjacency Relations
    for i in range(5):
        for j in range(5):
            tile_name = f"t{i}{j}"
            if tile_name in tiles:
                current_tile = tiles[tile_name]
                if j > 0:
                    problem.set_initial_value(connected(current_tile, tiles[f"t{i}{j-1}"]), True)
                if j < 4:
                    problem.set_initial_value(connected(current_tile, tiles[f"t{i}{j+1}"]), True)
                if i > 0:
                    problem.set_initial_value(connected(current_tile, tiles[f"t{i-1}{j}"]), True)
                if i < 4:
                    problem.set_initial_value(connected(current_tile, tiles[f"t{i+1}{j}"]), True)

    # Define Furniture Locations
    furniture_tiles = {"t10", "t20", "t30", "t11", "t21", "t12", "t32", "t34"}
    for tile_name in furniture_tiles:
        problem.set_initial_value(furniture_at(tiles[tile_name]), True)

    # Define guard path - now using the next_in_path fluent
    guard_path = ["t20", "t21", "t22", "t32", "t42", "t41", "t40", "t30"]
    for i in range(len(guard_path)):
        current = guard_path[i]
        next_tile = guard_path[(i+1) % len(guard_path)]  # Cycle back to start
        problem.set_initial_value(next_in_path(tiles[current], tiles[next_tile]), True)

    # Ensure no traces are left at the end
    for tile in tiles.values():
        problem.add_goal(Not(trace_left(tile)))

    problem.add_goal(diamond_stolen())  # Ensure the diamond is stolen
    problem.add_goal(at(attacker_obj, tiles["t00"]))  # Attacker must return home
    problem.add_goal(attacker_turn())  # End with attacker's turn (ensures guard has completed their last move)
    problem.add_goal(Not(fail_state))  # Plan fails if fail_state is True


    return problem

problem = create_problem()
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