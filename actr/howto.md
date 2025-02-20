conda env create --prefix ./conda --file=conda_env_actr.yml

conda activate ../conda

sbcl --dynamic-space-size 4096

(load "/home/scifaipy/quicklisp/setup.lisp")

(ql:quickload "py4cl")

(load "~/git/ACT-R/load-act-r.lisp")

(load "/home/scifaipy/git/ACT-R/environment/environment-cmds.lisp")
(load "/home/scifaipy/git/ACT-R/environment/server.lisp")
(load-act-r-model "./cognitive_model.lisp")

Now start start-environment-Linux

Now start Dodge Asteroids PyGame in another terminal
conda activate ./conda
python run_exp*

(run 5) or (run-step)


Current problem: After a few seconnds action always none

TODO:
First debug with plot, create gif/video.
Less granularity eventually, would prob. crash then.

clone https://github.com/nilsheinrich/DodgeAsteroids_lockedSections.git connect agent to new env. New branch