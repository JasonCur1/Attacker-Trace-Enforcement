# --------------------------------------------------------------

# trace left after every SSH movement
# connected fluent acts as can_ping

# Defender can only block one host at a time. Not all router connections

# Basic pattern:
# 1. Exploit a vulnerability
# 2. Raise my privilege level
# 3. move from one section to another

# If in external, I can only move to internal
# Once in internal, I can move to critical

# External privileges
# User privileges
# Sudo privileges

# Set up segment based movement restrictions

# --------------------------------------------------------------

from unified_planning.shortcuts import *
from unified_planning.model import Problem, Fluent
import random

random.seed(42)

diamond_location = 'PC01'
attacker_starting_location = 'PC10'



def setup_domain(problem: Problem):
    # --- Type Hierarchy ---
    service = UserType('service')
    vulnerability = UserType('vulnerability')
    segment_type = UserType('segment') # network segmentation/zones

    agent_type = UserType('agent')
    attacker = Object('attacker_agent', agent_type)
    defender = Object('defender_agent', agent_type)
    problem.add_object(attacker)
    problem.add_object(defender)

    privilege_level = UserType('privilege-level')
    user_privilege = UserType('user', father=privilege_level)
    root_privilege = UserType('root', father=privilege_level)

    network_node = UserType('network-node')
    host = UserType('host', network_node)
    infrastructure_device = UserType('infrastructure-device', network_node)
    pc = UserType('pc', host)
    # server = UserType('server', host) # idk yet
    router = UserType('router', infrastructure_device)
    firewall = UserType('firewall', infrastructure_device)
    switch = UserType('switch', infrastructure_device)

    # --- Fluents ---
    connected = Fluent('static_connected', n1=network_node, n2=network_node)
    connected.symmetric = True
    at = Fluent('static_at', a=agent_type, h=host)
    vulnerable = Fluent('static_vulnerable', h=host, v=vulnerability)
    can_ssh = Fluent('static_can_ssh', src=network_node, dest=network_node)
    has_local_privilege = Fluent('static_has_local_privilege', a=agent_type, h=host, p=privilege_level)
    traffic_allowed = Fluent('static_traffic_allowed', src=network_node, dest=network_node)
    separated_by = Fluent('static_separated_by', s1=segment_type, s2=segment_type, f=firewall)
    in_segment = Fluent('static_in_segment', n=network_node, s=segment_type)
    is_patch_available = Fluent('static_is_patch_available', v=vulnerability)

    data_stolen = Fluent('data_stolen')
    logs_cleaned = Fluent('logs_cleaned', h=host)
    escaped = Fluent('escaped')

    fluent_list = [
        connected, at, vulnerable, can_ssh, has_local_privilege, traffic_allowed, separated_by, in_segment, is_patch_available, data_stolen, logs_cleaned, escaped
    ]

    for f in fluent_list:
        problem.add_fluent(f)


    # --- Object Creation ---
    # -- Hosts --
    pc_dict = {}
    for i in range(1, 37):
        name = f"pc{i}"
        obj = Object(name, pc)
        problem.set_initial_value(logs_cleaned(obj), True)
        pc_dict[name] = obj
        problem.add_object(obj) # TODO: might be problematic

    # -- Infrastructure Devices --
    router_dict = {}
    for i in range(1, 11):
        name = f"router{i}"
        obj = Object(name, router)
        router_dict[name] = obj
        problem.add_object(obj) # TODO: might be problematic

    switch_dict = {}
    for i in range(1, 10):
        name = f"switch{i}"
        obj = Object(name, switch)
        switch_dict[name] = obj
        problem.add_object(obj) # TODO: might be problematic

    internal_firewall = Object('internal_firewall', firewall)
    external_firewall = Object('external_firewall', firewall)

    internal_segment = Object('internal_segment', segment_type)
    external_segment = Object('external_segment', segment_type)
    critical_segment = Object('critical_segment', segment_type)

    problem.add_object(internal_firewall)
    problem.add_object(external_firewall)
    problem.add_object(internal_segment)
    problem.add_object(external_segment)
    problem.add_object(critical_segment)

    # --- Topology & Connectivity ---
    # -- Switch 1 --
    problem.set_initial_value(connected(pc_dict['pc1'], switch_dict['switch1']), True)
    problem.set_initial_value(connected(pc_dict['pc2'], switch_dict['switch1']), True)
    problem.set_initial_value(connected(pc_dict['pc3'], switch_dict['switch1']), True)
    problem.set_initial_value(connected(pc_dict['pc4'], switch_dict['switch1']), True)
    problem.set_initial_value(connected(pc_dict['pc5'], switch_dict['switch1']), True)
    problem.set_initial_value(connected(pc_dict['pc6'], switch_dict['switch1']), True)
    problem.set_initial_value(connected(pc_dict['pc7'], switch_dict['switch1']), True)
    problem.set_initial_value(connected(switch_dict['switch1'], router_dict['router1']), True)

    # -- Switch 2 --
    problem.set_initial_value(connected(pc_dict['pc8'], switch_dict['switch2']), True)
    problem.set_initial_value(connected(pc_dict['pc9'], switch_dict['switch2']), True)
    problem.set_initial_value(connected(pc_dict['pc10'], switch_dict['switch2']), True)
    problem.set_initial_value(connected(switch_dict['switch2'], router_dict['router2']), True)

    # -- Switch 3 --
    problem.set_initial_value(connected(pc_dict['pc11'], switch_dict['switch3']), True)
    problem.set_initial_value(connected(pc_dict['pc12'], switch_dict['switch3']), True)
    problem.set_initial_value(connected(pc_dict['pc13'], switch_dict['switch3']), True)
    problem.set_initial_value(connected(switch_dict['switch3'], router_dict['router3']), True)

    # -- Switch 4 --
    problem.set_initial_value(connected(pc_dict['pc14'], switch_dict['switch4']), True)
    problem.set_initial_value(connected(pc_dict['pc15'], switch_dict['switch4']), True)
    problem.set_initial_value(connected(pc_dict['pc16'], switch_dict['switch4']), True)
    problem.set_initial_value(connected(switch_dict['switch4'], router_dict['router4']), True)

    # -- Switch 5 --
    problem.set_initial_value(connected(pc_dict['pc17'], switch_dict['switch5']), True)
    problem.set_initial_value(connected(pc_dict['pc18'], switch_dict['switch5']), True)
    problem.set_initial_value(connected(pc_dict['pc19'], switch_dict['switch5']), True)
    problem.set_initial_value(connected(pc_dict['pc20'], switch_dict['switch5']), True)
    problem.set_initial_value(connected(switch_dict['switch5'], router_dict['router5']), True)

    # -- Switch 6 --
    problem.set_initial_value(connected(pc_dict['pc21'], switch_dict['switch6']), True)
    problem.set_initial_value(connected(pc_dict['pc22'], switch_dict['switch6']), True)
    problem.set_initial_value(connected(pc_dict['pc23'], switch_dict['switch6']), True)
    problem.set_initial_value(connected(pc_dict['pc24'], switch_dict['switch6']), True)
    problem.set_initial_value(connected(pc_dict['pc25'], switch_dict['switch6']), True)
    problem.set_initial_value(connected(pc_dict['pc26'], switch_dict['switch6']), True)
    problem.set_initial_value(connected(pc_dict['pc27'], switch_dict['switch6']), True)
    problem.set_initial_value(connected(switch_dict['switch6'], router_dict['router5']), True)

    # -- Switch 7 --
    problem.set_initial_value(connected(pc_dict['pc28'], switch_dict['switch7']), True)
    problem.set_initial_value(connected(pc_dict['pc29'], switch_dict['switch7']), True)
    problem.set_initial_value(connected(pc_dict['pc30'], switch_dict['switch7']), True)
    problem.set_initial_value(connected(switch_dict['switch7'], router_dict['router7']), True)

    # -- Switch 8 --
    problem.set_initial_value(connected(pc_dict['pc31'], switch_dict['switch8']), True)
    problem.set_initial_value(connected(pc_dict['pc32'], switch_dict['switch8']), True)
    problem.set_initial_value(connected(pc_dict['pc33'], switch_dict['switch8']), True)
    problem.set_initial_value(connected(switch_dict['switch8'], router_dict['router8']), True)

    # -- Switch 9 --
    problem.set_initial_value(connected(pc_dict['pc34'], switch_dict['switch9']), True)
    problem.set_initial_value(connected(pc_dict['pc35'], switch_dict['switch9']), True)
    problem.set_initial_value(connected(pc_dict['pc36'], switch_dict['switch9']), True)
    problem.set_initial_value(connected(switch_dict['switch9'], router_dict['router9']), True)

    # -- Router/Firewall connectivity --
    problem.set_initial_value(connected(router_dict['router1'], external_firewall), True)
    problem.set_initial_value(connected(router_dict['router2'], router_dict['router6']), True)
    problem.set_initial_value(connected(router_dict['router2'], router_dict['router10']), True)
    problem.set_initial_value(connected(router_dict['router3'], router_dict['router6']), True)
    problem.set_initial_value(connected(router_dict['router3'], router_dict['router10']), True)
    problem.set_initial_value(connected(router_dict['router4'], router_dict['router6']), True)
    problem.set_initial_value(connected(router_dict['router4'], router_dict['router10']), True)
    problem.set_initial_value(connected(router_dict['router5'], router_dict['router10']), True)
    problem.set_initial_value(connected(router_dict['router6'], external_firewall), True)
    problem.set_initial_value(connected(router_dict['router7'], internal_firewall), True)
    problem.set_initial_value(connected(router_dict['router8'], internal_firewall), True)
    problem.set_initial_value(connected(router_dict['router9'], internal_firewall), True)
    problem.set_initial_value(connected(router_dict['router10'], internal_firewall), True)

    # -- Segments --
    for i in range(1, 11):
        problem.set_initial_value(in_segment(pc_dict[f'pc{i}'], external_segment), True)
    for i in range(11, 28):
        problem.set_initial_value(in_segment(pc_dict[f'pc{i}'], internal_segment), True)
    for i in range(28, 37):
        problem.set_initial_value(in_segment(pc_dict[f'pc{i}'], critical_segment), True)

    # External Firewall separates the outside from the internal network
    problem.set_initial_value(separated_by(external_segment, internal_segment, external_firewall), True)
    problem.set_initial_value(separated_by(internal_segment, external_segment, external_firewall), True)

    # Internal Firewall separates the internal network from the critical segment
    problem.set_initial_value(separated_by(internal_segment, critical_segment, internal_firewall), True)
    problem.set_initial_value(separated_by(critical_segment, internal_segment, internal_firewall), True)

    # - Critical Segment (sensitive data) -
    problem.set_initial_value(in_segment(switch_dict['switch7'], critical_segment), True)
    problem.set_initial_value(in_segment(switch_dict['switch8'], critical_segment), True)
    problem.set_initial_value(in_segment(switch_dict['switch9'], critical_segment), True)
    for i in range(28, 37):
        problem.set_initial_value(in_segment(pc_dict[f'pc{i}'], critical_segment), True)

    # can_ssh initialization
    for p1 in pc_dict.values():
        for p2 in pc_dict.values():
            if p1 != p2:
                problem.set_initial_value(can_ssh(p1, p2), True)

    # --- Starting Values ---
    problem.set_initial_value(at(attacker, pc_dict['pc1']), True)


    # --- Actions ---
    # -- Attacker Actions --
    # - Move -
    attack_ssh_move = InstantaneousAction('attack_move_ssh', a=agent_type, src=host, dest=host)
    a, src, dest = attack_ssh_move.parameters
   #attack_ssh_move.add_precondition(connected(src, dest))
    attack_ssh_move.add_precondition(Equals(a, attacker))
    attack_ssh_move.add_precondition(at(a, src))
    attack_ssh_move.add_precondition(can_ssh(src, dest))
    attack_ssh_move.add_effect(at(a, src), False)
    attack_ssh_move.add_effect(at(a, dest), True)
    attack_ssh_move.add_effect(logs_cleaned(dest), False)
    problem.add_action(attack_ssh_move)

    # - Wait -
    attack_wait = InstantaneousAction('attack_wait', a=agent_type, h=host)
    a, h = attack_wait.parameters
    attack_wait.add_precondition(at(a, h))
    attack_wait.add_precondition(Equals(a, attacker))
    attack_wait.add_effect(at(a, h), True)
    problem.add_action(attack_wait)

    # - Clean -
    attack_clean = InstantaneousAction('attack_clean', a=agent_type, h=host)
    a, h = attack_clean.parameters
    attack_clean.add_precondition(Equals(a, attacker))
    attack_clean.add_precondition(at(a, h))
    attack_clean.add_precondition(Not(logs_cleaned(h)))
    attack_clean.add_effect(logs_cleaned(h), True)
    problem.add_action(attack_clean)

    # - Steal -
    attack_steal = InstantaneousAction('attack_steal', a=agent_type, h=host, seg=segment_type)
    a, h, seg = attack_steal.parameters
    attack_steal.add_precondition(Equals(a, attacker))
    attack_steal.add_precondition(at(a, h))
    attack_steal.add_precondition(in_segment(h, seg))
    attack_steal.add_precondition(Equals(seg, critical_segment))
    attack_steal.add_precondition(Not(data_stolen))
    attack_steal.add_effect(data_stolen, True)
    problem.add_action(attack_steal)

    # - Escape -
    attack_log_off = InstantaneousAction('attack_log_off', a=agent_type)
    a = attack_log_off.parameters
    attack_log_off.add_precondition(Equals(a, attacker))
    attack_log_off.add_precondition(data_stolen)
    attack_log_off.add_effect(escaped, True)
    problem.add_action(attack_log_off)

    # -- Defender Actions --
    # - Disallaow ssh -
    fix_update_firewall_ruleset = InstantaneousAction('fix_update_firewall_ruleset', a=agent_type, f=firewall, src=host, dest=host, s_src=segment_type, s_dest=segment_type)
    a, f, src, dest, s_src, s_dest = fix_update_firewall_ruleset.parameters
    fix_update_firewall_ruleset.add_precondition(Equals(a, defender))
    fix_update_firewall_ruleset.add_precondition(can_ssh(src, dest))
    fix_update_firewall_ruleset.add_precondition(in_segment(src, s_src))
    fix_update_firewall_ruleset.add_precondition(in_segment(dest, s_dest))
    fix_update_firewall_ruleset.add_precondition(separated_by(s_src, s_dest, f))
    fix_update_firewall_ruleset.add_effect(can_ssh(src, dest), False)
    problem.add_action(fix_update_firewall_ruleset)

    # --- Domain Specific Goals ---
    return {
        "success_conditions": [
            escaped
        ]
    }


