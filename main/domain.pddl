(define (domain generalized_domain-domain)
 (:requirements :strips :typing :negative-preconditions :equality :conditional-effects)
 (:types agent tile)
 (:constants
   houdini blart - agent
   t31 - tile
 )
 (:predicates (at_ ?a - agent ?t - tile) (diamond_stolen) (no_trace_left ?t - tile) (guard_visited ?t - tile) (connected ?x - tile ?y - tile) (next_in_path ?t1 - tile ?t2 - tile) (attacker_turn) (guard_turn) (fail_state))
 (:action move
  :parameters ( ?curr - tile ?to - tile ?a - agent)
  :precondition (and (at_ ?a ?curr) (connected ?curr ?to) (= ?a houdini) (attacker_turn))
  :effect (and (not (no_trace_left ?to)) (not (at_ ?a ?curr)) (at_ ?a ?to) (not (attacker_turn)) (guard_turn) (when (at_ blart ?to) (fail_state))))
 (:action wait
  :parameters ( ?loc - tile ?a - agent)
  :precondition (and (at_ ?a ?loc) (= ?a houdini) (attacker_turn))
  :effect (and (not (attacker_turn)) (guard_turn)))
 (:action clean
  :parameters ( ?curr - tile ?a - agent)
  :precondition (and (at_ ?a ?curr) (not (no_trace_left ?curr)) (attacker_turn))
  :effect (and (no_trace_left ?curr) (not (attacker_turn)) (guard_turn)))
 (:action steal
  :parameters ( ?curr - tile ?a - agent)
  :precondition (and (at_ ?a ?curr) (= ?curr t31) (attacker_turn))
  :effect (and (diamond_stolen) (not (attacker_turn)) (guard_turn)))
 (:action guard_move
  :parameters ( ?curr - tile ?to - tile ?a - agent)
  :precondition (and (= ?a blart) (at_ ?a ?curr) (next_in_path ?curr ?to) (guard_turn))
  :effect (and (not (at_ ?a ?curr)) (at_ ?a ?to) (guard_visited ?to) (not (guard_turn)) (attacker_turn) (when (at_ houdini ?to) (fail_state)) (when (not (no_trace_left ?to)) (fail_state))))
)
