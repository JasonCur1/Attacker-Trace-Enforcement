from unified_planning.shortcuts import *
from unified_planning.model.problem import Problem
import unified_planning as up


def create_problem():
    problem = Problem('museum')

    # Define Types (Objects)
    tile = UserType("tile")
    attacker = UserType("attacker")
    trace_counter = UserType("trace_counter")

    


    # Define Predicates (relationships)
    attacker_at = Fluent("at", BoolType(), a=attacker, t=tile) # Attacker is at this tile
    diamond_stolen = Fluent("diamond_stolen", BoolType()) # Has the diamond been stolen?
    furniture_at = Fluent("furniture_at", BoolType(), t=tile) # Furniture is at this tile
    connected = Fluent("connected", BoolType(), x=tile, y=tile)
    connected.symmetric = True
    trace_left = Fluent("trace_left", BoolType(), t=tile) # The furniture has been moved at this tile (trace left behind)
    trace_count = Fluent("trace_count", IntType(), m=trace_counter)

    # Add fluents to problems
    problem.add_fluent(attacker_at, default_initial_value=False)
    problem.add_fluent(diamond_stolen, default_initial_value=False)
    problem.add_fluent(furniture_at, default_initial_value=False)
    problem.add_fluent(connected, default_initial_value=False)
    problem.add_fluent(trace_left, default_initial_value=False)
    problem.add_fluent(trace_count, default_initial_value=0)

    # Initialize the world
    tiles = {}

    for i in range(5):
        for j in range(5):
            t_name = f"t{i}{j}"
            t = Object(t_name, tile)
            tiles[t_name] = t
            problem.add_object(t)


    # Define Actions
    move_to_normal_tile = InstantaneousAction("move_to_normal_tile", curr=tile, to=tile, a=attacker)
    curr, to, a = move_to_normal_tile.parameters
    move_to_normal_tile.add_precondition(attacker_at(a, curr)) # Must be at current tile
    move_to_normal_tile.add_precondition(Not(furniture_at(to))) # Can't move into a furniture tile (must use furniture_move)
    move_to_normal_tile.add_precondition(connected(curr, to))
    move_to_normal_tile.add_effect(attacker_at(a, curr), False) # Attacker is no longer at initial position
    move_to_normal_tile.add_effect(attacker_at(a, to), True) # Move to destination tile
    problem.add_action(move_to_normal_tile)

    move_to_furniture_tile = InstantaneousAction("move_to_furniture_tile", curr=tile, to=tile, a=attacker, c=trace_counter)
    curr, to, a, c = move_to_furniture_tile.parameters
    move_to_furniture_tile.add_precondition(attacker_at(a, curr))
    move_to_furniture_tile.add_precondition(furniture_at(to))
    move_to_furniture_tile.add_precondition(connected(curr, to))
    move_to_furniture_tile.add_effect(attacker_at(a, curr), False)
    move_to_furniture_tile.add_effect(attacker_at(a, to), True)
    move_to_furniture_tile.add_effect(trace_left(to), True)
    move_to_furniture_tile.add_increase_effect(trace_count(c), 1)
    problem.add_action(move_to_furniture_tile)

    steal = InstantaneousAction("steal", curr=tile, a=attacker)
    curr, a = steal.parameters
    steal.add_precondition(attacker_at(a, curr))  # Attacker must be at some tile
    steal.add_precondition(Equals(curr, tiles["t31"]))  # That tile must be t31
    steal.add_effect(diamond_stolen(), True) # Don't need to keep track of where, just need to know if it's gone
    problem.add_action(steal)


    # Use positions list to fill out the stuff below  
    attacker = Object("houdini", attacker)
    trace_counter_obj = Object("trace_counter_instance", trace_counter)

    problem.add_object(trace_counter_obj)
    problem.add_object(attacker)


    # Initial Attacker Position
    problem.set_initial_value(attacker_at(attacker, tiles["t00"]), True)

    #Furniture Tiles
    # problem.set_initial_value(furniture_at(tiles["t10"]), True)
    # problem.set_initial_value(furniture_at(tiles["t20"]), True)
    # problem.set_initial_value(furniture_at(tiles["t30"]), True)
    # problem.set_initial_value(furniture_at(tiles["t11"]), True)
    # problem.set_initial_value(furniture_at(tiles["t21"]), True)
    # problem.set_initial_value(furniture_at(tiles["t12"]), True)
    # problem.set_initial_value(furniture_at(tiles["t32"]), True)
    # #problem.set_initial_value(furniture_at(tiles["t33"]), True) # Enable if you want to force attacker to leave a trace
    # problem.set_initial_value(furniture_at(tiles["t34"]), True)

    # Adjacency Relations
    for i in range(5):
        for j in range(5):
            tile_name = f"t{i}{j}"
            if tile_name in tiles:
                current_tile = tiles[tile_name]
                
                # Left neighbor (j-1)
                if j > 0:
                    problem.set_initial_value(connected(current_tile, tiles[f"t{i}{j-1}"]), True)
                    problem.set_initial_value(connected(tiles[f"t{i}{j-1}"], current_tile), True)

                # Right neighbor (j+1)
                if j < 4:  # Max index is 4 in a 5x5 grid
                    problem.set_initial_value(connected(current_tile, tiles[f"t{i}{j+1}"]), True)
                    problem.set_initial_value(connected(tiles[f"t{i}{j+1}"], current_tile), True)

                # Top neighbor (i-1)
                if i > 0:
                    problem.set_initial_value(connected(current_tile, tiles[f"t{i-1}{j}"]), True)
                    problem.set_initial_value(connected(tiles[f"t{i-1}{j}"], current_tile), True)

                # Bottom neighbor (i+1)
                if i < 4:
                    problem.set_initial_value(connected(current_tile, tiles[f"t{i+1}{j}"]), True)
                    problem.set_initial_value(connected(tiles[f"t{i+1}{j}"], current_tile), True)

    # Set goal state
    problem.add_goal(diamond_stolen)
    problem.add_goal(attacker_at(attacker, tiles["t00"]))

    # problem.add_quality_metric(
    #     up.model.metrics.MinimizeActionCosts({move_to_normal_tile: 0, move_to_furniture_tile: 1, steal: 0})
    # )

    # Leaving traces is bad, therefore, minimize this count
    problem.add_quality_metric(up.model.metrics.MinimizeExpressionOnFinalState(trace_count(trace_counter_obj)))


    return problem



problem = create_problem()
print(problem.kind)

with OneshotPlanner(name='fast-downward-opt', problem_kind=problem.kind) as planner:
    result = planner.solve(problem)
    plan = result.plan
    if plan is not None:
        print("%s returned:" % planner.name)
        print(plan)
    else:
        print("No plan found.")