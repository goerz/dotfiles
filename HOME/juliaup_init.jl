import Pkg
Pkg.activate()  # activate base environment
pkgs = ["Revise", "Infiltrator", "JET", "Debugger", "IJulia"];
Pkg.add(pkgs)

import IJulia
IJulia.installkernel("Julia", "--project=@.")
