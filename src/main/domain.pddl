(define (domain generalized_domain-domain)
 (:requirements :strips :typing :negative-preconditions :equality :conditional-effects)
 (:types agent tile)
 (:constants
   adversary_houdini leader_bob - agent
   t00 - tile
 )
 (:predicates (static_connected ?x - tile ?y - tile) (static_at ?a - agent ?t - tile) (static_diamond_at ?t - tile) (diamond_stolen) (escaped) (static_is_trace_tile ?t - tile) (no_trace_left ?t - tile))
 (:action fix_place_wall
  :parameters ( ?curr - tile ?to - tile ?a - agent ?b - agent)
  :precondition (and (= ?a leader_bob) (= ?b adversary_houdini) (static_connected ?curr ?to) (static_connected ?to ?curr) (not (static_diamond_at ?curr)) (not (static_diamond_at ?to)) (not (static_at ?b ?curr)) (not (static_at ?b ?to)))
  :effect (and (not (static_connected ?curr ?to)) (not (static_connected ?to ?curr))))
 (:action fix_place_trace_tile
  :parameters ( ?curr - tile ?a - agent)
  :precondition (and (= ?a leader_bob))
  :effect (and (static_is_trace_tile ?curr)))
 (:action attack_move
  :parameters ( ?curr - tile ?to - tile ?a - agent)
  :precondition (and (static_at ?a ?curr) (static_connected ?curr ?to) (= ?a adversary_houdini))
  :effect (and (not (static_at ?a ?curr)) (static_at ?a ?to) (when (static_is_trace_tile ?to) (not (no_trace_left ?to)))))
 (:action attack_wait
  :parameters ( ?curr - tile ?a - agent)
  :precondition (and (static_at ?a ?curr) (= ?a adversary_houdini))
  :effect (and (static_at ?a ?curr)))
 (:action attack_clean
  :parameters ( ?curr - tile ?a - agent)
  :precondition (and (static_at ?a ?curr) (= ?a adversary_houdini) (not (no_trace_left ?curr)))
  :effect (and (no_trace_left ?curr)))
 (:action attack_steal
  :parameters ( ?curr - tile ?a - agent)
  :precondition (and (static_at ?a ?curr) (= ?a adversary_houdini) (static_diamond_at ?curr))
  :effect (and (diamond_stolen)))
 (:action attack_escape
  :parameters ( ?curr - tile ?a - agent)
  :precondition (and (static_at ?a ?curr) (= ?a adversary_houdini) (diamond_stolen) (= ?curr t00))
  :effect (and (escaped)))
)
