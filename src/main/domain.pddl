(define (domain generalized_domain-domain)
 (:requirements :strips :typing :negative-preconditions :equality :conditional-effects)
 (:types agent tile time)
 (:constants
   adversary_houdini leader_blart - agent
   t00 - tile
 )
 (:predicates (escaped) (is_current_timestep ?t - time) (is_next_timestep ?t1 - time ?t2 - time) (at_ ?a - agent ?t_0 - tile) (diamond_stolen) (diamond_at ?t_0 - tile) (no_trace_left ?t_0 - tile) (connected ?x - tile ?y - tile) (is_trace_tile ?t_0 - tile) (attacker_caught))
 (:action fix_move
  :parameters ( ?curr - tile ?to - tile ?a - agent ?t1 - time ?t2 - time)
  :precondition (and (= ?a leader_blart) (at_ ?a ?curr) (connected ?curr ?to) (is_current_timestep ?t1) (is_next_timestep ?t1 ?t2))
  :effect (and (not (at_ ?a ?curr)) (at_ ?a ?to) (when (at_ adversary_houdini ?to) (attacker_caught)) (when (not (no_trace_left ?to)) (attacker_caught)) (not (is_current_timestep ?t1)) (is_current_timestep ?t2)))
 (:action fix_wait
  :parameters ( ?loc - tile ?a - agent ?t1 - time ?t2 - time)
  :precondition (and (at_ ?a ?loc) (= ?a leader_blart) (is_current_timestep ?t1) (is_next_timestep ?t1 ?t2))
  :effect (and (at_ ?a ?loc) (not (is_current_timestep ?t1)) (is_current_timestep ?t2)))
 (:action attack_move
  :parameters ( ?curr - tile ?to - tile ?a - agent ?t1 - time ?t2 - time)
  :precondition (and (at_ ?a ?curr) (connected ?curr ?to) (= ?a adversary_houdini) (is_current_timestep ?t1) (is_next_timestep ?t1 ?t2))
  :effect (and (when (is_trace_tile ?to) (not (no_trace_left ?to))) (not (at_ ?a ?curr)) (at_ ?a ?to) (when (at_ leader_blart ?to) (attacker_caught)) (not (is_current_timestep ?t1)) (is_current_timestep ?t2)))
 (:action attack_wait
  :parameters ( ?loc - tile ?a - agent ?t1 - time ?t2 - time)
  :precondition (and (at_ ?a ?loc) (= ?a adversary_houdini) (is_current_timestep ?t1) (is_next_timestep ?t1 ?t2))
  :effect (and (at_ ?a ?loc) (not (is_current_timestep ?t1)) (is_current_timestep ?t2)))
 (:action attack_clean
  :parameters ( ?curr - tile ?a - agent ?t1 - time ?t2 - time)
  :precondition (and (at_ ?a ?curr) (not (no_trace_left ?curr)) (is_current_timestep ?t1) (is_next_timestep ?t1 ?t2))
  :effect (and (no_trace_left ?curr) (not (is_current_timestep ?t1)) (is_current_timestep ?t2)))
 (:action attack_steal
  :parameters ( ?curr - tile ?a - agent ?t1 - time ?t2 - time)
  :precondition (and (at_ ?a ?curr) (diamond_at ?curr) (is_current_timestep ?t1) (is_next_timestep ?t1 ?t2))
  :effect (and (diamond_stolen) (not (is_current_timestep ?t1)) (is_current_timestep ?t2)))
 (:action attack_escape
  :parameters ( ?curr - tile ?a - agent ?t1 - time ?t2 - time)
  :precondition (and (at_ ?a ?curr) (= ?curr t00) (is_current_timestep ?t1) (is_next_timestep ?t1 ?t2) (diamond_stolen))
  :effect (and (escaped) (not (is_current_timestep ?t1)) (is_current_timestep ?t2)))
)
