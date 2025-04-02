from unified_planning.shortcuts import *
from unified_planning.model.problem import Problem
import unified_planning as up

def create_problem():
    problem = Problem('museum')

    # Define Types (Objects)
    tile_type = UserType("tile")
    agent_type = UserType("agent")

    # Define Predicates (relationships)
    at = Fluent("at", BoolType(), a=agent_type, t=tile_type) # Specified agent is at this tile
    diamond_stolen = Fluent("diamond_stolen", BoolType())  # Has the diamond been stolen?
    furniture_at = Fluent("furniture_at", BoolType(), t=tile_type)  # Furniture is at this tile
    trace_left = Fluent("trace_left", BoolType(), t=tile_type)  # Whether a trace is left on this tile
    visited = Fluent("visited", BoolType(), t=tile_type) # Has the attacker visited this tile before?
    connected = Fluent("connected", BoolType(), x=tile_type, y=tile_type)
    connected.symmetric = True

    # Add fluents to problems
    problem.add_fluent(at, default_initial_value=False)
    problem.add_fluent(diamond_stolen, default_initial_value=False)
    problem.add_fluent(furniture_at, default_initial_value=False)
    problem.add_fluent(trace_left, default_initial_value=False)
    problem.add_fluent(visited, default_initial_value=False)
    problem.add_fluent(connected, default_initial_value=False)

    # Initialize the world
    tiles = {}
    for i in range(5):
        for j in range(5):
            t_name = f"t{i}{j}"
            t = Object(t_name, tile_type)
            tiles[t_name] = t
            problem.add_object(t)


    # Define Actions
    move = InstantaneousAction("move", curr=tile_type, to=tile_type, a=agent_type)
    curr, to, a = move.parameters
    move.add_precondition(at(a, curr))
    move.add_precondition(connected(curr, to))

    # Conditional effect: leave a trace if moving to a furniture tile
    move.add_effect(trace_left(to), True, furniture_at(to))

    move.add_effect(visited(to), True)

    move.add_effect(at(a, curr), False)
    move.add_effect(at(a, to), True)
    problem.add_action(move)


    clean = InstantaneousAction("clean", curr=tile_type, a=agent_type)
    curr, a = clean.parameters
    clean.add_precondition(at(a, curr))
    clean.add_precondition(trace_left(curr))  # Can only clean if a trace is left
    clean.add_precondition(visited(curr))
    clean.add_effect(trace_left(curr), False)  # Cleaning removes the trace
    problem.add_action(clean)


    steal = InstantaneousAction("steal", curr=tile_type, a=agent_type)
    curr, a = steal.parameters
    steal.add_precondition(at(a, tiles["t31"])) # The diamond is at t31
    steal.add_effect(diamond_stolen(), True)
    problem.add_action(steal)


    guard_tiles = [tiles["t20"], tiles["t21"], tiles["t22"], tiles["t32"], tiles["t42"], tiles["t41"], tiles["t40"], tiles["t30"]]
    guard_move = InstantaneousAction("guard_move", curr=tile_type, a=agent_type)
    curr, a = guard_move.parameters
    guard_move.add_precondition(at(a, curr))

    for i in range(len(guard_tiles)):
        from_tile = guard_tiles[i]
        to_tile = guard_tiles[(i+1) % len(guard_tiles)]  # Cycle back to start after last tile
        guard_move.add_effect(at(a, from_tile), False, Equals(curr, from_tile))
        guard_move.add_effect(at(a, to_tile), True, Equals(curr, from_tile))

    problem.add_action(guard_move)

    # Define attacker
    attacker_obj = Object("houdini", agent_type)
    problem.add_object(attacker_obj)

    # Define guard
    guard_obj = Object("blart", agent_type)
    problem.add_object(guard_obj)

    # Initial Attacker Position
    problem.set_initial_value(at(attacker_obj, tiles["t00"]), True)

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

    # Ensure no traces are left at the end
    for tile in tiles.values():
        problem.add_goal(Not(trace_left(tile)))

    problem.add_goal(diamond_stolen)  # Ensure the diamond is stolen
    problem.add_goal(at(attacker_obj, tiles["t00"]))

    return problem

problem = create_problem()
print(problem.kind)

with OneshotPlanner(problem_kind=problem.kind) as planner:
    result = planner.solve(problem)
    plan = result.plan
    if plan is not None:
        print("%s returned:" % planner.name)
        print(plan)
    else:
        print("No plan found.")
