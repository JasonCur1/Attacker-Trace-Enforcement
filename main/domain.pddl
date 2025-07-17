(define (domain gridworld-attacker)
    (:requirements :strips :typing :adl :non-deterministic)

    (:types
        location
        agent
        attacker - agent
        guard - agent
        item
        diamond - item
    )

    (:predicates
        (at ?a - agent ?l - location)
        (has-diamond ?a - attacker)
        (diamond-at ?l - location)
        (is-caught)
        (is-traced ?l - location)
        (visited ?l - location)
        (connected ?l1 - location ?l2 - location)
        (guard-found-trace)
    )

    ;; Attacker movement with non-deterministic guard behavior
    (:action move-attacker
        :parameters (?from - location ?to - location ?g-curr - location ?g-next - location)
        :precondition (and (at attacker-agent ?from)
                           (connected ?from ?to)
                           (not (is-caught))
                           (at guard-agent ?g-curr)
                           ;; Guard can either stay put or move to adjacent location
                           (or (= ?g-curr ?g-next) (connected ?g-curr ?g-next)))
        :effect (and (not (at attacker-agent ?from))
                     (at attacker-agent ?to)
                     (is-traced ?to)
                     (visited ?to)
                     (not (at guard-agent ?g-curr))
                     ;; Non-deterministic guard movement
                     (oneof
                         ;; Outcome 1: Guard moves as specified
                         (and (at guard-agent ?g-next)
                              (when (= ?g-next ?to) (is-caught))
                              (when (is-traced ?g-next) (guard-found-trace)))
                         ;; Outcome 2: Guard stays at current location (regardless of ?g-next)
                         (and (at guard-agent ?g-curr)
                              (when (= ?g-curr ?to) (is-caught))
                              (when (is-traced ?g-curr) (guard-found-trace)))
                     )
                )
    )

    ;; Action: pick-up-diamond
    (:action pick-up-diamond
        :parameters (?l - location ?a - attacker)
        :precondition (and (at ?a ?l)
                           (diamond-at ?l)
                           (not (has-diamond ?a))
                           (not (is-caught)))
        :effect (and (has-diamond ?a)
                     (not (diamond-at ?l)))
    )

    ;; Action: clean-trace
    (:action clean-trace
        :parameters (?l - location ?a - attacker)
        :precondition (and (at ?a ?l)
                           (is-traced ?l)
                           (not (is-caught)))
        :effect (not (is-traced ?l))
    )
)