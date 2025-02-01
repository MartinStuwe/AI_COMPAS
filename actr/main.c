#include <stdlib.h>

int main(void)
{
    // Activate the conda environment and then run SBCL with all Lisp forms
    // in one single shell command.  Use conda's "run" instead of "activate",
    // because "activate" doesn't persist for subsequent calls.
    system(
        "conda run -p ../conda sbcl --dynamic-space-size 4096 "
        "--eval '(load \"/home/scifaipy/quicklisp/setup.lisp\")' "
        "--eval '(ql:quickload \"py4cl\")' "
        "--eval '(load \"~/git/ACT-R/load-act-r.lisp\")' "
        "--eval '(load-act-r-model \"./cognitive_model.lisp\")' "
        "--eval '(quit)'"
    );

    return 0;
}
