from unified_planning.shortcuts import *
from unified_planning.model.multi_agent import *

def create_multiagent_museum_problem():
    problem = MultiAgentProblem('museum')

    # Define Types (Objects)
    tile = UserType("tile")

    # Define Agents
    attacker_agent = Agent("attacker", problem)
    guard_agent = Agent("guard", problem)

    # Define Fluents
    # Attacker fluents
    attacker_at = Fluent("at", t=tile)
    trace_left = Fluent("trace_left", t=tile)
    visited = Fluent("visited", t=tile)
    diamond_stolen = Fluent("diamond_stolen")
    
    # Guard fluents
    guard_at = Fluent("guard_at", t=tile)
    
    # Shared/public fluents
    furniture_at = Fluent("furniture_at", t=tile)
    connected = Fluent("connected", x=tile, y=tile)
    connected.symmetric = True
    
    # Add fluents to agents
    # Private fluents for attacker
    attacker_agent.add_fluent(attacker_at, default_initial_value=False)
    attacker_agent.add_fluent(trace_left, default_initial_value=False)
    attacker_agent.add_fluent(visited, default_initial_value=False)
    attacker_agent.add_fluent(diamond_stolen, default_initial_value=False)
    attacker_agent.add_fluent(furniture_at, default_initial_value=False)
    attacker_agent.add_fluent(connected, default_initial_value=False)
    
    # Private fluents for guard
    guard_agent.add_fluent(guard_at, default_initial_value=False)
    
    
    # Define objects and add them to the problem
    tiles = {}
    for i in range(5):
        for j in range(5):
            t_name = f"t{i}{j}"
            t = Object(t_name, tile)
            tiles[t_name] = t
            problem.add_object(t)
    
    # Define Attacker Actions
    move_to_furniture = InstantaneousAction("move_to_furniture", curr=tile, to=tile)
    curr, to = move_to_furniture.parameters
    move_to_furniture.add_precondition(attacker_at(curr))
    move_to_furniture.add_precondition(connected(curr, to))
    move_to_furniture.add_precondition(furniture_at(to))
    move_to_furniture.add_effect(trace_left(to), True)
    move_to_furniture.add_effect(visited(to), True)
    move_to_furniture.add_effect(attacker_at(curr), False)
    move_to_furniture.add_effect(attacker_at(to), True)
    attacker_agent.add_action(move_to_furniture)

    move_to_non_furniture = InstantaneousAction("move_to_non_furniture", curr=tile, to=tile)
    curr, to = move_to_non_furniture.parameters
    move_to_non_furniture.add_precondition(attacker_at(curr))
    move_to_non_furniture.add_precondition(connected(curr, to))
    move_to_non_furniture.add_precondition(Not(furniture_at(to)))
    move_to_non_furniture.add_effect(visited(to), True)
    move_to_non_furniture.add_effect(attacker_at(curr), False)
    move_to_non_furniture.add_effect(attacker_at(to), True)
    attacker_agent.add_action(move_to_non_furniture)
    
    clean = InstantaneousAction("clean", curr=tile)
    curr = clean.parameters[0]
    clean.add_precondition(attacker_at(curr))
    clean.add_precondition(trace_left(curr))
    clean.add_precondition(visited(curr))
    clean.add_effect(trace_left(curr), False)
    attacker_agent.add_action(clean)
    
    steal = InstantaneousAction("steal", curr=tile)
    curr = steal.parameters[0]
    steal.add_precondition(attacker_at(curr))
    steal.add_precondition(Equals(curr, tiles["t31"]))  # Diamond location
    steal.add_effect(diamond_stolen(), True)
    attacker_agent.add_action(steal)

    wait = InstantaneousAction("wait", curr=tile)
    curr = wait.parameters[0]
    wait.add_precondition(attacker_at(curr))
    # No effects - just allows the attacker to stay in place for one time step
    attacker_agent.add_action(wait)
    
    # Define Guard Actions
    # guard_tiles = [tiles["t20"], tiles["t21"], tiles["t22"], tiles["t32"], 
    #               tiles["t42"], tiles["t41"], tiles["t40"], tiles["t30"]]
    
    # for i in range(len(guard_tiles)):
    #     from_tile = guard_tiles[i]
    #     to_tile = guard_tiles[(i+1) % len(guard_tiles)]
        
    #     guard_move_action = InstantaneousAction(f"patrol_{i}")
    #     guard_move_action.add_precondition(guard_at(from_tile))
    #     guard_move_action.add_effect(guard_at(from_tile), False)
    #     guard_move_action.add_effect(guard_at(to_tile), True)
    #     guard_agent.add_action(guard_move_action)
    
    # Add agents to the problem
    problem.add_agent(attacker_agent)
    problem.add_agent(guard_agent)
    
    # Set initial values
    # Attacker initial position
    problem.set_initial_value(Dot(attacker_agent, attacker_at(tiles["t00"])), True)
    
    # Guard initial position (starting at t20 in the patrol route)
    problem.set_initial_value(Dot(guard_agent, guard_at(tiles["t21"])), True)
    
    # Define adjacency relations
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
    
    # Define furniture locations
    # furniture_tiles = {"t10", "t20", "t30", "t11", "t21", "t12", "t32", "t34"}
    # for tile_name in furniture_tiles:
    #     problem.set_initial_value(furniture_at(tiles[tile_name]), True)
    
    # Define goals
    # Ensure diamond is stolen
    problem.add_goal(Dot(attacker_agent, diamond_stolen()))
    
    # Ensure attacker returns to starting point
    problem.add_goal(Dot(attacker_agent, attacker_at(tiles["t00"])))
    
    # Ensure no traces are left
    for tile in tiles.values():
        problem.add_goal(Not(Dot(attacker_agent, trace_left(tile))))
    
    return problem

# Create the problem
problem = create_multiagent_museum_problem()

# Try to solve with FMAP planner
with OneshotPlanner(problem_kind=problem.kind) as planner:
    result = planner.solve(problem)
    plan = result.plan
    if plan is not None:
        print("FMAP returned: %s" % result.plan)
    else:
        print("No plan found.")