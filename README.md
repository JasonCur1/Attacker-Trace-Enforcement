# Attacker-Trace-Enforcement

1. ssh into venus
2. cd thesis/main/attacker_policy_generation
3. if needed, modify prp makefiles to use static linking option
4. ./prp/src/prp domain.pddl problem.pddl --dump-policy 2 --jic-limit 72000
5. ./prp/prp-scripts/translate_policy.py > human_policy.pol

python sim stuff



1. Navigate to stackelberg/src
2. if needed modify makefiles to use static linking option
3. ./build_all
4. ./stackelberg-planner-sls/src/fast-downward.py domain.pddl problem.pddl --search "sym_stackelberg(optimal_engine=symbolic(plan_reuse_minimal_task_upper_bound=false, plan_reuse_upper_bound=true), upper_bound_pruning=false)"