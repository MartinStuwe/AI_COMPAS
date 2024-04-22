(clear-all)
(define-model compas-model
(chunk-type goal decision-state vision-state)

(chunk-type obstactle pos-x pos-y)
(chunk-type agent pos-x pos-y)


(add-dm
    (goal isa goal decision-state start vision-state idle)
)

(add-visicon-features
    '(screen-x 0 screen-y 0)
)

(check-act-r-command "add-visicon-features")
(goal-focus goal)

(p init-agent
    =goal>
        decision-state start
        vision-state idle
==>
    =goal>
        decision-state find-obstacles
        vision-state searching
)

(p find-obstacles
    =goal>
        decision-state find-obstacles
        vision-state searching
    =)

)




