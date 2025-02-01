(clear-all)

;observation_space_size_x = 40
;observation_space_size_y = 60
;scaling = 14

; TODO: Utility for diff. granularities
;       Left Drift, None, Right Drift productions, visual buffer

(define-model compas-model

(chunk-type screen-size height width)
(chunk-type goal decision-state vision-state action start)
(chunk-type obstacle pos-x pos-y)
(chunk-type agent pos-x pos-y)
(chunk-type comet screen-x screen-y comet-id)


(chunk-type screen-size height width)
(chunk-type conv-tile pos-x pos-y)


(chunk-type ll-soc value)
(chunk-type hl-soc value)


;Visuelle Env, Action-Goal, Shapes von Objekten
(add-dm
    (main-goal isa goal decision-state start vision-state idle action nil)
)

(check-act-r-command "add-visicon-features")
(defun my-custom-press-key-monitor ()
  ;; Assume 'key' contains information about which key was pressed
  (model-output "Key has been pressed."))
(monitor-act-r-command "press-key" "(my-custom-press-key-monitor)")
(install-device '("motor" "keyboard"))

(goal-focus main-goal)


(p init-agent
    =goal>
        decision-state start
        vision-state idle
==>
    =goal>
        decision-state find-obstacles
        vision-state searching
        action-goal-x nil
        action-goal-y nil
        drift-x nil
        horizontal-movement nil
        perceived-step-size nil
        action nil

    !eval! (py4cl:import-module "time")
    !eval! (py4cl:import-module "math")
    !eval! (py4cl:import-module "numpy" :as "np")
    !eval! (py4cl:import-module "mmap")
    !eval! (py4cl:import-module "os")
    !eval! (py4cl:import-module "pygame")
    !eval! (py4cl:import-module "datetime")
    !eval! (py4cl:import-module "sys")
    !eval! (py4cl:python-exec "sys.path.insert(0, '/home/scifaipy/dev/compas/moonlander-visualization')")
    !eval! (py4cl:import-module "shm_read")
    !eval! (py4cl:import-module "scipy.stats" :as "sts")
    !eval! (py4cl:import-module "action_planner")
    !eval! (py4cl:import-module "action_planner.helper_functions" :as "helper_funcs")
    !eval! (py4cl:import-module "action_planner.action_planner" :as "ap")
    !eval! (py4cl:python-exec "ActionPlanner = ap.ActionPlanner")
    !eval! (py4cl:import-module "action_planner.CCL_action_selection" :as "CCL")

)
;eventuell situated-state 

(p find-obstacles
    =goal>
        decision-state find-obstacles
        vision-state searching
==>
    =goal>
        decision-state find-action

)

(p select-action
    =goal>
        decision-state find-action
        - action "Right"
        - action "Left"
==>
    !eval! (py4cl:python-exec "parameters = helper_funcs.load_parameters_dict(\"../action_planner/Data/parameters.txt\")")
    !eval! (py4cl:python-exec "playersprite_rect_x = shm_read.get_shared_array_2()")
    !eval! (py4cl:python-exec "agent = ActionPlanner(free_parameters=parameters, initial_position_x=playersprite_rect_x[0]+14, observation_space_in_pixel=[40*14, 60*14])")
    !eval! (py4cl:python-exec "reference_point = shm_read.get_shared_object_3()")
    !eval! (py4cl:python-exec "surface_array = shm_read.get_shared_array_1()")
        
    !eval! (py4cl:python-exec "agent.action_goal, agent.action_goal_col, _, agent.HL_SoC = CCL.select_action_goal(PAR=agent.parameters, HL_SoC=agent.HL_SoC, observation_in_pixel=surface_array, reference=reference_point, agent_pos_x=playersprite_rect_x, min_percentage_for_rejection=agent.min_percentage_for_rejection)")
    
    !eval! (py4cl:python-exec "agent.apply_motor_control()")


    !eval! (py4cl:python-exec "current_input = agent.action")
    !eval! (py4cl:python-exec "print(f\"ACTION IS: {current_input}\")")
    ; TODO: Move action to LISP process
    !eval! (py4cl:python-exec "current_input = \"None\" if current_input is None else current_input")
    !eval! (defvar myvar)
    ; (py4cl:python-eval "[i for i in range(4)]")
    !eval! (setq myvar (py4cl:python-eval "current_input")) ;Agent can return None
    ;!eval! (setq myvar (py4cl:python-eval "[i for i in range(4)]")) ;Agent can return None
    ;!eval! (print (py4cl:python-eval "[i for i in range(4)]")) #(0 1 2 3) =myvar2 is: #(0 1 2 3)
    !eval! (print (py4cl:python-eval "current_input"))
   ; (py4cl:python-eval "[1, 2, 3]")
    !eval! (print myvar)
    ;(print myvar) try

    !bind! =myvar2 (eval myvar)
    !eval! (model-output "=myvar2 is: ~a" =myvar2)

    =goal>
        decision-state find-action
        action =myvar2  ;Check before whether action returned None

    !eval! (if (buffer-chunk 'goal)
                 (let ((action-value (buffer-slot-value 'goal 'action)))
                   (model-output "Action slot value: ~a" action-value))
                 (model-output "Goal buffer is empty or action slot not set."))
)


(p move-left
    =goal>
        decision-state find-action
        action "Left"
    ==>
    +manual>
        cmd press-key
        key "z"
    =goal>
        action nil

    !safe-eval! (model-output "Starting move-left command")
    !eval! (evaluate-act-r-command "moveleft")
    ;!eval! (py4cl:python-exec "time.sleep(500)")
)

 (p move-right
    =goal>
        decision-state find-action
        action "Right"
==>
    +manual>
        cmd press-key
        key "m"
    =goal>
        action nil

    !safe-eval! (model-output "Starting move-right command")
    !eval! (evaluate-act-r-command "moveright")
 )

(p update-1
    =goal>
        decision-state update-1
    ==>
    =goal>
        decision-state move-left

    !eval! (py4cl:python-exec "green_array = shm_read.get_shared_array_1()")
    !eval! (py4cl:python-exec "print(f\"#1s: {np.count_nonzero(green_array == 1)}\")")
    !eval! (py4cl:python-exec "print(f\"time: {datetime.datetime.now()}\")")
)
    ;    # surface_array = np.transpose(pygame.surfarray.array2d(surface_subsection))  # to test
    ;    surface_array[surface_array > 1] = 1
    ; Need to pass complete screen matrix
    ; -            self.agent.prediction_error() #Call upon 2D ARRAY Updates 
        ; Activation values
        ; 72: 0.07,
        ; 56: 0.05,
        ; 42: 0.04,
        ; 30: 0.03,
        ; 20: 0.02

    ; Screenshot an Nils schicken, Convolution, Generation Action field in
    ; verschiedene Pools, production compilen eine production in 56 pools n_pools
    ; Produktionen für alle n_pools 5 verschiedene Werte
    ; 5 verschiedene Produktion 
    ; generation action field
    ; ccl_action_selecton
    ;!eval! (py4cl:python-call "st.uniform.pdf" "1.0" "1.0")
    ;!eval! (defun compute-and-print-uniform-dist (observation-space-x-in-pixel)
    ;(let* ((pdf-value (py4cl:python-call "st.uniform.pdf" :args (list observation-space-x-in-pixel)))
    ;     (uniform-dist (+ pdf-value 1)))
    ;(format t "The value of uniform_dist is: ~a~%" uniform-dist)))
    ;!eval! (compute-and-print-uniform-dist 10)

(p update-2-1
    =goal>
        decision-state update-2
        - horizontal-movement 0
        horizontal_movement =mov
    ==>
    =goal>
        decision-state update-3
    ;(py4cl:python-exec (format nil "perceived_step_size = abs(~a)" =mov))
)

;(p update-3
;    =goal>
;        decision-state update-3
;        perceived-step-size =percvd-step-size
;    ==>
;    =goal>
;        decision-state update-4
;    ;(py4cl:python-exec "observation_space_x_in_pixel = np.linspace(0, 40, num=40)")
;    ;mu=self.perceived_step_size
;    ;sigma = self.visual_acuity
;    (py4cl:python-exec (format nil "likelihood_out = sts.norm.pdf(observation_space_x_in_pixel, loc=~a, scale=sigma)" percvd-step-size))
;)


;Tuesday 13:30 IFIS
)




