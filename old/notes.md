### Analogy Explained
Begin with a 5x5 grid world.

#### Agents:
- Thief -> Attacker
- Guard -> Scanner/Security

#### Environment:
- Grid tile -> Node or machine in a network
- Furniture -> Logs, audit trails, or modified metadata
- Diamond -> Sensitive data or valuable information
- Attacker movement -> Lateral movement through a network
- Cleaning -> Covering tracks or restoring system state

#### Domain Specific Goals:
- Thief's Goals:
	- Steal diamond
	- Avoid guard
	- Escape back to starting tile
- Guard's Goals:
	- Patrol route
	- (define more when partial observability is established)

#### Domain Independent Goals:
- Ensure final state matches initial state
	- Measured via initially true fluents
- Inherit all domain specific goals

### Introducing POMDP

#### Initial Understanding:
- Attacker has full observability
	- Knows where diamond is
	- Knows where furniture tiles are
	- Knows where the defender is and their route
- Guard has partial observability
	- TBD

#### Grounding partial observability in formulas:


#### Topics of Discussion with Sarath
- **Make all tiles furniture tiles?**
	- wouldn't all machines/nodes in a network have logging capabilities?
- Implementing guard partial observability
	- **Short term memory**
		- "I saw a trace here 3 turns ago"
		- Limit it to some # of turns to prevent state space exploding?
	- **Fog of war**: can only see tiles directly adjacent
	- Death tiles: guard can always see certain tiles. Attacker instant fail if they move to these
		- "critical points in a network"
		- If attacker always sees these, then challenge is reduced
		- If they're unknown then it becomes a game of risk management for the attacker
			- Make tiles probabilistic: attacker knows there is a 70% chance this tile will fail them instantly
	- Alert tiles: If attacker steps in this tile, the guard will navigate towards it to investigate
	- **Noisy alert tiles:** true positives, false positives, and false negatives
		- Probabilistic indications of attacker presence
		- guard has some confidence based on current beliefs
- Additional attacker actions
	- Leave decoy
		- "exploit a known or zero-day vulnerability on adjacent tile alerting defender to investigate"
		- "mimic legitimate traffic"
			- adds some defender uncertainty to alert
		- fake alert trigger to divert attention
- Additional defender actions
	- Scan cell
		- Allows defender to scan any specified cell
		- Maybe have probabilistic outcome?
	- Deploy honeypot
		- defender decoy on some adjacent cell with a probability of changing to attacker's goal to try to steal the new honeypot

#### Designing Defender Strategies
Defender should be able to make informed decisions about how to allocate their efforts across the grid. 
1. **Strategic patrolling**
	1. Chooses which paths to patrol based on current beliefs about the attacker's likely location or areas deemed critical
2. Strategic scanning
	1. Scans cells driven by defender's belief state
		1. Alert tiles
		2. Decoys left by attacker





end goals
- designing the world in such a way that its easier to defend

seperate out the problem
- algorithm for the attacker
- then put the attacker in different environments and see which they're more and less effective in


attacker doesn't know what the defender will do besides the fact that they will patrol these 4 tiles


fully observable non-determinstic planning


attacker can see where defender is at all times, but don't know what they'll do next

attacker:
full observability, knows where the defender is but doesn't know what they'll do next

defender:
partial observility (fog of war). Start with a fully determined path. Then move towards random actions
beliefs mechanisms

world designer:
reinforcement learning??



next steps:
formulate beliefs
"I can see my current cell, and the next cell I'll walk into."



misc notes:
formulation where 3 copies of every fluent

what the attacker knows

what the guard belives

what the guard sees is true

  

whenever there is a mismatch between what the guard believes and what the guard sees, that would be consi

  

when the guar dmodifies something then their belief about that thing is updated

  

only partial observablility for defender

  

have conditional effects that will check for discrepancies between believed and true

  

whenever you execute a guard action, just contrast between what is believed and what is true
