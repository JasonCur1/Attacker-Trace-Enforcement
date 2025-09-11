(define (domain package-delivery)
(:requirements :strips :typing)
(:types
location
package
)

(:predicates
    (leader_at ?l - location)
    (follower_at ?l - location)
    (at_location ?p - package ?l - location)
)

(:action fix_move_leader
    :parameters (?l1 ?l2 - location)
    :precondition (leader_at ?l1)
    :effect (and (not (leader_at ?l1)) (leader_at ?l2))
)

(:action fix_pickup_package
    :parameters (?p - package ?l - location)
    :precondition (and (leader_at ?l) (at_location ?p ?l))
    :effect (and (not (at_location ?p ?l)) (at_location ?p leader))
)

(:action fix_deliver_package
    :parameters (?p - package ?l - location)
    :precondition (and (leader_at ?l) (at_location ?p leader))
    :effect (and (not (at_location ?p leader)) (at_location ?p ?l))
)

(:action attack_steal_package
    :parameters (?p - package ?l - location)
    :precondition (and (follower_at ?l) (at_location ?p ?l))
    :effect (and (not (at_location ?p ?l)) (at_location ?p follower))
)

)