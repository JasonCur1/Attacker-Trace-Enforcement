(define (domain simple-fond)
  (:requirements :strips :non-deterministic)
  
  (:predicates
    (at-a)
    (at-b)
    (goal-reached)
  )

  ;; Action: try-move
  ;; It can nondeterministically result in being at either a or b
  (:action try-move
    :parameters ()
    :precondition ()
    :effect (oneof
      (and (at-a))
      (and (at-b))
    )
  )

  ;; Action: finish if at the correct location
  (:action finish
    :parameters ()
    :precondition (at-b)
    :effect (goal-reached)
  )
)
