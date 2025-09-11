(define (problem delivery-problem)
(:domain package-delivery)
(:objects
home - location
warehouse - location
destination - location
packageA - package
)

(:init
    (leader_at home)
    (follower_at destination)
    (at_location packageA warehouse)
)

(:goal
    (at_location packageA destination)
)

)