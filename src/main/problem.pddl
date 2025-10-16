(define (problem generalized_domain-problem)
 (:domain generalized_domain-domain)
 (:objects
   t01 t02 t10 t11 t12 t20 t21 t22 - tile
 )
 (:init (static_at adversary_houdini t00) (static_diamond_at t21) (no_trace_left t00) (no_trace_left t01) (no_trace_left t02) (no_trace_left t10) (no_trace_left t11) (no_trace_left t12) (no_trace_left t20) (no_trace_left t21) (no_trace_left t22) (static_is_trace_tile t01) (static_connected t00 t01) (static_connected t00 t10) (static_connected t01 t00) (static_connected t01 t02) (static_connected t01 t11) (static_connected t02 t01) (static_connected t02 t12) (static_connected t10 t11) (static_connected t10 t00) (static_connected t10 t20) (static_connected t11 t10) (static_connected t11 t12) (static_connected t11 t01) (static_connected t11 t21) (static_connected t12 t11) (static_connected t12 t02) (static_connected t12 t22) (static_connected t20 t21) (static_connected t20 t10) (static_connected t21 t20) (static_connected t21 t22) (static_connected t21 t11) (static_connected t22 t21) (static_connected t22 t12))
 (:goal (and (no_trace_left t00) (no_trace_left t01) (no_trace_left t02) (no_trace_left t10) (no_trace_left t11) (no_trace_left t12) (no_trace_left t20) (no_trace_left t21) (no_trace_left t22) (diamond_stolen) (escaped)))
)
