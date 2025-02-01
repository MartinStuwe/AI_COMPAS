
(load "~/quicklisp/setup.lisp")
(ql:quickload "py4cl")



(load "~/git/ACT-R/load-act-r.lisp")

(load-act-r-model "cognitive_model.lisp")

(run 10)
