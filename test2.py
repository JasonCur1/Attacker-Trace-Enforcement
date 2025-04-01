from unified_planning.shortcuts import *
from unified_planning.model.multi_agent import *

def create_simplified_problem():
    problem = MultiAgentProblem('simplified')

    # Define UserTypes
    tile_type = UserType("tile")
    agent_type = UserType("agent")

    # Define Fluents - all must be boolean or numerical for FMAP
    location = Fluent("location", BoolType(), a=agent_type, t=tile_type)
    connected = Fluent("connected", BoolType(), x=tile_type, y=tile_type)
    connected.symmetric = True
    
    # Define position as a boolean fluent with a tile parameter
    at = Fluent("at", BoolType(), t=tile_type)  # Boolean fluent with tile parameter

    # Define Actions
    move = InstantaneousAction("move", a=agent_type, from_tile=tile_type, to_tile=tile_type)
    a, from_tile, to_tile = move.parameters
    move.add_precondition(location(a, from_tile))
    move.add_precondition(connected(from_tile, to_tile))
    move.add_effect(location(a, from_tile), False)
    move.add_effect(location(a, to_tile), True)

    # Create Agents
    attacker_agent = Agent("attacker", problem)
    
    # Add public fluent to the agent
    attacker_agent.add_public_fluent(at, default_initial_value=False)
    
    # Add environment fluent
    problem.ma_environment.add_fluent(location, default_initial_value=False)
    problem.ma_environment.add_fluent(connected, default_initial_value=False)
    
    # Add action to agent
    attacker_agent.add_action(move)

    # Create Objects
    attacker = Object("houdini", agent_type)
    tile1 = Object("tile1", tile_type)
    tile2 = Object("tile2", tile_type)

    # Add agent to problem
    problem.add_agent(attacker_agent)
    
    # Add objects
    problem.add_object(attacker)
    problem.add_object(tile1)
    problem.add_object(tile2)
    
    # Set initial values
    # Set agent's position using Dot notation with boolean fluent
    problem.set_initial_value(Dot(attacker_agent, at(tile1)), True)
    
    # Then set environment fluents
    problem.set_initial_value(location(attacker, tile1), True)
    problem.set_initial_value(connected(tile1, tile2), True)
    problem.set_initial_value(connected(tile2, tile1), True)
    
    # Add goal to the agent - this was missing in previous attempts
    #attacker_agent.add_goal(location(attacker, tile2))
    
    # Also set global goal
    problem.add_goal(location(attacker, tile2))

    return problem

# Create the problem
problem = create_simplified_problem()
print(problem)

# Try to solve with a planner compatible with the problem kind
with OneshotPlanner(problem_kind=problem.kind) as planner:
    result = planner.solve(problem)
    plan = result.plan
    if plan is not None:
        print("Plan found: %s" % result.plan)
    else:
        print("No plan found.")