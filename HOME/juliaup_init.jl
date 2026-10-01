import Pkg
Pkg.activate()  # activate base environment

# Only libraries that get `using`-ed from a REPL session belong here. Nothing
# that an editor or a shell invokes as a separate process: those get their own
# environment so their dependency bounds cannot reach into this one.
pkgs = ["Revise", "Infiltrator", "Debugger", "IJulia", "TestEnv"];
Pkg.add(pkgs)

# Command line tools go in as standalone Pkg apps, which resolve in a private
# environment and expose a shim in ~/.julia/bin:
#
#     Pkg.Apps.add("JuliaFormatter")   # -> ~/.julia/bin/jlfmt
#     Pkg.Apps.add(; url="https://github.com/aviatesk/JETLS.jl", rev="release")
#
# `Pkg.Apps` shims hardcode the path of the Julia that installed them, so
# re-run these after juliaup removes a version, or the shim points at an
# interpreter that is no longer there.

# LanguageServer is deliberately NOT here. It is a separate process that only
# needs to read a project, never to share an environment with one, and putting
# it in the default environment drags its whole resolution in: it pins
# JuliaFormatter to 1.x (every release from 4.2 on), and through that held
# CommonMark at 0.8 and OrderedCollections at 1.x. It lives in its own shared
# environment instead:
#
#     julia +1.12 --project=@languageserver -e 'import Pkg; Pkg.add("LanguageServer")'
#
# Pinned to 1.12 because it does not load on 1.13 at all: SymbolServer 8.0.1
# fails to precompile (`MethodError: no method matching
# haskey(::SymbolServer.VarRef, ::Symbol)`), and both SymbolServer.jl and
# StaticLint.jl were archived in June 2026, so no fix is coming through the
# General registry. That does not matter in practice, since the server is its
# own process and can index a 1.13 project perfectly well while running under
# 1.12. julia-vscode sidesteps the whole thing by vendoring a patched
# SymbolServer that was never released.

# import IJulia
# IJulia.installkernel("Julia", "--project=@.")
