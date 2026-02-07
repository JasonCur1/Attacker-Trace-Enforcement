from unified_planning.shortcuts import *
from unified_planning.model import Problem, Fluent, Object
import random

random.seed(42)

def setup_domain(problem: Problem, pc_count_by_segment=None):
    # Set default PC counts if not provided
    if pc_count_by_segment is None:
        pc_count_by_segment = {
            'external': 3,
            'internal': 5,
            'critical': 3
        }
    
    # Validate the configuration
    required_segments = {'external', 'internal', 'critical'}
    if not all(seg in pc_count_by_segment for seg in required_segments):
        raise ValueError(f"pc_count_by_segment must contain keys: {required_segments}")
    
    if any(count < 1 for count in pc_count_by_segment.values()):
        raise ValueError("Each segment must have at least 1 PC")
    # --- Type Hierarchy ---
    vulnerability = UserType('vulnerability')
    segment_type = UserType('segment') 

    agent_type = UserType('agent')
    attacker = Object('attacker_agent', agent_type)
    defender = Object('defender_agent', agent_type)
    problem.add_object(attacker)
    problem.add_object(defender)

    privilege_level = UserType('privilege-level')
    user_privilege = UserType('user', father=privilege_level)
    root_privilege = UserType('root', father=privilege_level)

    # Create explicit Privilege Objects
    user_lvl = Object('user_lvl', user_privilege)
    root_lvl = Object('root_lvl', root_privilege)
    problem.add_object(user_lvl)
    problem.add_object(root_lvl)

    network_node = UserType('network-node')
    host = UserType('host', network_node)
    infrastructure_device = UserType('infrastructure-device', network_node)
    firewall = UserType('firewall', infrastructure_device)
    
    # Combined PC type (no switches or routers needed for logical SSH connections)
    pc = UserType('pc', host)

    # --- Fluents ---
    at = Fluent('static_at', a=agent_type, h=host)
    vulnerable = Fluent('static_vulnerable', h=host, v=vulnerability)
    can_ssh = Fluent('static_can_ssh', src=network_node, dest=network_node)
    has_local_privilege = Fluent('static_has_local_privilege', a=agent_type, h=host, p=privilege_level)
    separated_by = Fluent('static_separated_by', s1=segment_type, s2=segment_type, f=firewall)
    in_segment = Fluent('static_in_segment', n=network_node, s=segment_type)
    
    data_stolen = Fluent('data_stolen')
    logs_cleaned = Fluent('logs_cleaned', h=host)
    escaped = Fluent('escaped')

    fluent_list = [
        at, vulnerable, can_ssh, has_local_privilege, separated_by, in_segment, data_stolen, logs_cleaned, escaped
    ]

    for f in fluent_list:
        problem.add_fluent(f)

    # --- Object Creation ---
    
    # Generic vulnerability
    cve1 = Object('cve1', vulnerability)
    problem.add_object(cve1)

    # Create segment objects first
    external_segment = Object('external_segment', segment_type)
    internal_segment = Object('internal_segment', segment_type)
    critical_segment = Object('critical_segment', segment_type)
    
    problem.add_object(external_segment)
    problem.add_object(internal_segment)
    problem.add_object(critical_segment)

    # CONFIGURABLE: Create PCs based on pc_count_by_segment
    pc_dict = {}
    pc_segments = [
        ('external', pc_count_by_segment['external'], external_segment),
        ('internal', pc_count_by_segment['internal'], internal_segment),
        ('critical', pc_count_by_segment['critical'], critical_segment)
    ]
    
    counter = 1
    segment_bounds = {}  # Track PC index ranges for each segment
    
    for seg_name, count, seg_obj in pc_segments:
        start_idx = counter
        for i in range(count):
            name = f"pc{counter}"
            obj = Object(name, pc)
            problem.set_initial_value(logs_cleaned(obj), True)
            problem.set_initial_value(vulnerable(obj, cve1), True)
            problem.set_initial_value(in_segment(obj, seg_obj), True)
            pc_dict[name] = obj
            problem.add_object(obj)
            counter += 1
        segment_bounds[seg_name] = (start_idx, counter - 1)
    
    total_pcs = counter - 1
    print(f"Created {total_pcs} PCs:")
    print(f"  External (pc{segment_bounds['external'][0]}-pc{segment_bounds['external'][1]}): {pc_count_by_segment['external']} PCs")
    print(f"  Internal (pc{segment_bounds['internal'][0]}-pc{segment_bounds['internal'][1]}): {pc_count_by_segment['internal']} PCs")
    print(f"  Critical (pc{segment_bounds['critical'][0]}-pc{segment_bounds['critical'][1]}): {pc_count_by_segment['critical']} PCs")

    # Firewalls
    internal_firewall = Object('internal_firewall', firewall)
    external_firewall = Object('external_firewall', firewall)
    problem.add_object(internal_firewall)
    problem.add_object(external_firewall)

    # -- Firewall Rules --
    problem.set_initial_value(separated_by(external_segment, internal_segment, external_firewall), True)
    problem.set_initial_value(separated_by(internal_segment, external_segment, external_firewall), True)

    problem.set_initial_value(separated_by(internal_segment, critical_segment, internal_firewall), True)
    problem.set_initial_value(separated_by(critical_segment, internal_segment, internal_firewall), True)

    # --- can_ssh Initialization ---
    def get_segment_obj(pc_name):
        idx = int(pc_name.replace('pc', ''))
        ext_start, ext_end = segment_bounds['external']
        int_start, int_end = segment_bounds['internal']
        crit_start, crit_end = segment_bounds['critical']
        
        if ext_start <= idx <= ext_end:
            return external_segment
        if int_start <= idx <= int_end:
            return internal_segment
        if crit_start <= idx <= crit_end:
            return critical_segment
        return None

    # Calculate SSH permissions based on segment adjacency
    for p1_name, p1 in pc_dict.items():
        for p2_name, p2 in pc_dict.items():
            if p1 == p2: continue
            
            s1 = get_segment_obj(p1_name)
            s2 = get_segment_obj(p2_name)

            allow_connection = False
            
            # Allow: Same segment
            if s1 == s2: 
                allow_connection = True
            # Allow: External <-> Internal
            elif (s1 == external_segment and s2 == internal_segment) or \
                 (s1 == internal_segment and s2 == external_segment):
                allow_connection = True
            # Allow: Internal <-> Critical
            elif (s1 == internal_segment and s2 == critical_segment) or \
                 (s1 == critical_segment and s2 == internal_segment):
                allow_connection = True
            
            if allow_connection:
                problem.set_initial_value(can_ssh(p1, p2), True)

    # --- Starting Values ---
    problem.set_initial_value(at(attacker, pc_dict['pc1']), True)

    # --- Actions ---
    
    # 1. Exploit
    attack_exploit = InstantaneousAction('attack_exploit', a=agent_type, h=host, v=vulnerability)
    a, h, v = attack_exploit.parameters
    attack_exploit.add_precondition(Equals(a, attacker))
    attack_exploit.add_precondition(at(a, h))
    attack_exploit.add_precondition(vulnerable(h, v))
    attack_exploit.add_effect(has_local_privilege(a, h, user_lvl), True)
    problem.add_action(attack_exploit)

    # 2. Escalate
    attack_escalate = InstantaneousAction('attack_privilege_escalation', a=agent_type, h=host)
    a, h = attack_escalate.parameters
    attack_escalate.add_precondition(Equals(a, attacker))
    attack_escalate.add_precondition(at(a, h))
    attack_escalate.add_precondition(has_local_privilege(a, h, user_lvl))
    attack_escalate.add_effect(has_local_privilege(a, h, root_lvl), True)
    problem.add_action(attack_escalate)

    # 3. Move (Requires Root at Source)
    attack_ssh_move = InstantaneousAction('attack_move_ssh', a=agent_type, src=host, dest=host)
    a, src, dest = attack_ssh_move.parameters
    attack_ssh_move.add_precondition(Equals(a, attacker))
    attack_ssh_move.add_precondition(at(a, src))
    attack_ssh_move.add_precondition(has_local_privilege(a, src, root_lvl))
    attack_ssh_move.add_precondition(can_ssh(src, dest))
    attack_ssh_move.add_effect(at(a, src), False)
    attack_ssh_move.add_effect(at(a, dest), True)
    attack_ssh_move.add_effect(logs_cleaned(dest), False)
    problem.add_action(attack_ssh_move)

    # 4. Clean
    attack_clean = InstantaneousAction('attack_clean', a=agent_type, h=host)
    a, h = attack_clean.parameters
    attack_clean.add_precondition(Equals(a, attacker))
    attack_clean.add_precondition(at(a, h))
    attack_clean.add_precondition(Not(logs_cleaned(h)))
    attack_clean.add_effect(logs_cleaned(h), True)
    problem.add_action(attack_clean)

    # 5. Steal
    attack_steal = InstantaneousAction('attack_steal', a=agent_type, h=host, seg=segment_type)
    a, h, seg = attack_steal.parameters
    attack_steal.add_precondition(Equals(a, attacker))
    attack_steal.add_precondition(at(a, h))
    attack_steal.add_precondition(in_segment(h, seg))
    attack_steal.add_precondition(Equals(seg, critical_segment))
    attack_steal.add_precondition(Not(data_stolen))
    attack_steal.add_effect(data_stolen, True)
    problem.add_action(attack_steal)

    # 6. Escape
    attack_log_off = InstantaneousAction('attack_log_off', a=agent_type)
    a = attack_log_off.parameters
    attack_log_off.add_precondition(Equals(a, attacker))
    attack_log_off.add_precondition(data_stolen)
    attack_log_off.add_effect(escaped, True)
    problem.add_action(attack_log_off)

    # -- Defender Actions --
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