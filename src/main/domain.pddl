(define (domain generalized_domain-domain)
 (:requirements :strips :typing :negative-preconditions :equality :conditional-effects)
 (:types agent tile)
 (:constants
   adversary_houdini leader_blart - agent
   t44 - tile
 )
 (:predicates (at_ ?a - agent ?t - tile) (diamond_stolen) (no_trace_left ?t - tile) (connected ?x - tile ?y - tile) (is_trace_tile ?t - tile) (fail_state))
 (:action fix_move
  :parameters ( ?curr - tile ?to - tile ?a - agent)
  :precondition (and (= ?a leader_blart) (at_ ?a ?curr) (connected ?curr ?to))
  :effect (and (not (at_ ?a ?curr)) (at_ ?a ?to) (when (at_ adversary_houdini ?to) (fail_state)) (when (not (no_trace_left ?to)) (fail_state))))
 (:action fix_wait
  :parameters ( ?loc - tile ?a - agent)
  :precondition (and (at_ ?a ?loc) (= ?a leader_blart))
  :effect (and (at_ ?a ?loc)))
 (:action attack_move
  :parameters ( ?curr - tile ?to - tile ?a - agent)
  :precondition (and (at_ ?a ?curr) (connected ?curr ?to) (= ?a adversary_houdini))
  :effect (and (when (is_trace_tile ?to) (not (no_trace_left ?to))) (not (at_ ?a ?curr)) (at_ ?a ?to) (when (at_ leader_blart ?to) (fail_state))))
 (:action attack_wait
  :parameters ( ?loc - tile ?a - agent)
  :precondition (and (at_ ?a ?loc) (= ?a adversary_houdini))
  :effect (and (at_ ?a ?loc)))
 (:action attack_clean
  :parameters ( ?curr - tile ?a - agent)
  :precondition (and (at_ ?a ?curr) (not (no_trace_left ?curr)))
  :effect (and (no_trace_left ?curr)))
 (:action attack_steal
  :parameters ( ?curr - tile ?a - agent)
  :precondition (and (at_ ?a ?curr) (= ?curr t44))
  :effect (and (diamond_stolen)))
)
