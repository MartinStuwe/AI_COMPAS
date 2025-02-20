conda activate ../conda

sbcl --dynamic-space-size 4096

(load "/home/scifaipy/quicklisp/setup.lisp")

(ql:quickload "py4cl")

(load "~/git/ACT-R/load-act-r.lisp")

(load "/home/scifaipy/git/ACT-R/environment/environment-cmds.lisp")
(load "/home/scifaipy/git/ACT-R/environment/server.lisp")
(load-act-r-model "./cognitive_model.lisp")

Now start start-environment-Linux

Now start Dodge Asteroids PyGame:
conda activate ./conda
python run_exp*

(run 5) or (run-step)


Current problem:

* (run 100)
     0.000   GOAL                   SET-BUFFER-CHUNK GOAL MAIN-GOAL NIL
     0.000   VISION                 SET-BUFFER-CHUNK VISUAL-LOCATION CHUNK71 NIL
     0.000   VISION                 visicon-update
     0.000   PROCEDURAL             CONFLICT-RESOLUTION
     0.050   PROCEDURAL             PRODUCTION-FIRED INIT-AGENT
loc: 7; decision_space_y_probs: [3.03954846e-11 2.02173023e-08 4.94701075e-06 4.45315717e-04
 1.47468312e-02 1.79653182e-01 8.05149704e-01]; decision_space_y: [np.int64(5)]
     0.050   PROCEDURAL             CONFLICT-RESOLUTION
     0.100   PROCEDURAL             PRODUCTION-FIRED FIND-OBSTACLES
     0.100   PROCEDURAL             CONFLICT-RESOLUTION
     0.150   PROCEDURAL             PRODUCTION-FIRED SELECT-ACTION
sprite is:658
Move-left Production Print
[[0 0 0 ... 0 0 0]
 [0 0 0 ... 0 0 0]
 [0 0 0 ... 0 0 0]
 ...
 [0 0 0 ... 0 0 0]
 [0 0 0 ... 0 0 0]
 [0 0 0 ... 0 0 0]]
11092
ACT-R Surface Array Shape: {surface_array.shape})
loc: 7; decision_space_y_probs: [3.03954846e-11 2.02173023e-08 4.94701075e-06 4.45315717e-04
 1.47468312e-02 1.79653182e-01 8.05149704e-01]; decision_space_y: [np.int64(6)]

debugger invoked on a PY4CL:PYTHON-ERROR in thread
#<THREAD "main thread" RUNNING {100107A183}>:
  Python error: "min() arg is an empty sequence"

Type HELP for debugger help, or (SB-EXT:EXIT) to exit from SBCL.

restarts (invokable by number or by possibly-abbreviated name):
  0: [ABORT] Exit debugger, returning to top level.

(PY4CL::DISPATCH-MESSAGES #<UIOP/LAUNCH-PROGRAM::PROCESS-INFO {1001F39663}>)
   source: (ERROR 'PYTHON-ERROR :TEXT (STREAM-READ-STRING READ-STREAM))
0] ^C

debugger invoked on a SB-SYS:INTERACTIVE-INTERRUPT @7611AA49B63D in thread
#<THREAD "main thread" RUNNING {100107A183}>:
  Interactive interrupt at #x7611AA49B63D.

Type HELP for debugger help, or (SB-EXT:EXIT) to exit from SBCL.

restarts (invokable by number or by possibly-abbreviated name):
  0: [CONTINUE] Return from SB-UNIX:SIGINT.
  1: [ABORT   ] Reduce debugger level (to debug level 1).
  2:            Exit debugger, returning to top level.

("bogus stack frame")
0[2] 



TODO:
First debug with plot, create gif/video.
Less granularity eventually, would prob. crash then.

clone https://github.com/nilsheinrich/DodgeAsteroids_lockedSections.git connect agent to new env. New branch