(define (problem steal-and-escape)
    (:domain gridworld-attacker)

    ;; Define all 16 locations for a 4x4 grid (loc-x-y)
    (:objects
        attacker-agent - attacker
        guard-agent - guard
        diamond-item - diamond
        loc-0-0 loc-0-1 loc-0-2 loc-0-3
        loc-1-0 loc-1-1 loc-1-2 loc-1-3
        loc-2-0 loc-2-1 loc-2-2 loc-2-3
        loc-3-0 loc-3-1 loc-3-2 loc-3-3 - location
    )

    ;; Initial State
    (:init
        ;; Attacker starts at top-left
        (at attacker-agent loc-0-0)
        ;; Guard starts at bottom-right column, top row (arbitrary, away from attacker/diamond)
        (at guard-agent loc-3-0)
        ;; Diamond is at bottom-right
        (diamond-at loc-3-3)

        ;; Initial state predicates
        (not (has-diamond attacker-agent))
        (not (is-caught))
        (not (guard-found-trace))

        ;; No traces initially
        (not (is-traced loc-0-0)) (not (is-traced loc-0-1)) (not (is-traced loc-0-2)) (not (is-traced loc-0-3))
        (not (is-traced loc-1-0)) (not (is-traced loc-1-1)) (not (is-traced loc-1-2)) (not (is-traced loc-1-3))
        (not (is-traced loc-2-0)) (not (is-traced loc-2-1)) (not (is-traced loc-2-2)) (not (is-traced loc-2-3))
        (not (is-traced loc-3-0)) (not (is-traced loc-3-1)) (not (is-traced loc-3-2)) (not (is-traced loc-3-3))

        ;; No locations visited initially
        (not (visited loc-0-0)) (not (visited loc-0-1)) (not (visited loc-0-2)) (not (visited loc-0-3))
        (not (visited loc-1-0)) (not (visited loc-1-1)) (not (visited loc-1-2)) (not (visited loc-1-3))
        (not (visited loc-2-0)) (not (visited loc-2-1)) (not (visited loc-2-2)) (not (visited loc-2-3))
        (not (visited loc-3-0)) (not (visited loc-3-1)) (not (visited loc-3-2)) (not (visited loc-3-3))

        ;; Generated connections for a 4x4 grid
        (connected loc-0-0 loc-0-1)
        (connected loc-0-0 loc-1-0)
        (connected loc-0-1 loc-0-0)
        (connected loc-0-1 loc-0-2)
        (connected loc-0-1 loc-1-1)
        (connected loc-0-2 loc-0-1)
        (connected loc-0-2 loc-0-3)
        (connected loc-0-2 loc-1-2)
        (connected loc-0-3 loc-0-2)
        (connected loc-0-3 loc-1-3)
        (connected loc-1-0 loc-0-0)
        (connected loc-1-0 loc-1-1)
        (connected loc-1-0 loc-2-0)
        (connected loc-1-1 loc-0-1)
        (connected loc-1-1 loc-1-0)
        (connected loc-1-1 loc-1-2)
        (connected loc-1-1 loc-2-1)
        (connected loc-1-2 loc-0-2)
        (connected loc-1-2 loc-1-1)
        (connected loc-1-2 loc-1-3)
        (connected loc-1-2 loc-2-2)
        (connected loc-1-3 loc-0-3)
        (connected loc-1-3 loc-1-2)
        (connected loc-1-3 loc-2-3)
        (connected loc-2-0 loc-1-0)
        (connected loc-2-0 loc-2-1)
        (connected loc-2-0 loc-3-0)
        (connected loc-2-1 loc-1-1)
        (connected loc-2-1 loc-2-0)
        (connected loc-2-1 loc-2-2)
        (connected loc-2-1 loc-3-1)
        (connected loc-2-2 loc-1-2)
        (connected loc-2-2 loc-2-1)
        (connected loc-2-2 loc-2-3)
        (connected loc-2-2 loc-3-2)
        (connected loc-2-3 loc-1-3)
        (connected loc-2-3 loc-2-2)
        (connected loc-2-3 loc-3-3)
        (connected loc-3-0 loc-2-0)
        (connected loc-3-0 loc-3-1)
        (connected loc-3-1 loc-2-1)
        (connected loc-3-1 loc-3-0)
        (connected loc-3-1 loc-3-2)
        (connected loc-3-2 loc-2-2)
        (connected loc-3-2 loc-3-1)
        (connected loc-3-2 loc-3-3)
        (connected loc-3-3 loc-2-3)
        (connected loc-3-3 loc-3-2)
    )

    ;; Goal State
    (:goal (and (at attacker-agent loc-0-0)     ; Attacker returns to start
                 (has-diamond attacker-agent)     ; Attacker has the diamond
                 ;; All locations that were visited by the attacker must be cleaned (no trace left)
                 (forall (?l - location) (imply (visited ?l) (not (is-traced ?l))))
           )
    )
)