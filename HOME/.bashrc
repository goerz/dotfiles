# Startup files for bash *login* shells: /etc/profile, then .bash_profile OR
# .bash_login OR .profile, NOT .bashrc (hence, source .bashrc in .bash_profile)
# SSH shells are usually like login shells.
# A non-login interactive shell reads .bashrc (and inherits login variables)
# A non-interative shell (e.g. running a shell script) reads only the file
# given in $BASH_ENV, if defined.

export HOMEBREW_PREFIX="/opt/homebrew";
export HOMEBREW_CELLAR="/opt/homebrew/Cellar";
export HOMEBREW_REPOSITORY="/opt/homebrew";

export QUARTO_PYTHON=$HOME/.local/share/uv/tools/jupyterlab/bin/python
export JULIAUP_ROOT=$HOME/.juliaup/
export PREFIX="$HOME/.local"
export EDITOR=nvim
export GNUBIN="$HOMEBREW_PREFIX/opt/make/libexec/gnubin"

export PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
export PATH="/Library/TeX/texbin:$PATH"
export PATH="$HOMEBREW_PREFIX/bin:$HOMEBREW_PREFIX/sbin:$GNUBIN:$PATH"
export PATH="$JULIAUP_ROOT/bin:$PATH"

# "Julia Apps" exist since Julia 1.12 and are installed into ~/.julia/bin. E.g. `jetls`
export PATH="$HOME/.julia/bin:$PATH"

export PATH="$HOME/bin:$PREFIX/bin:$PATH"

export FORTUNE_PATH=$HOME/.fortunes/
export LANG="en_US.UTF-8"
export LC_ALL="en_US.UTF-8"
export LC_CTYPE="en_US.UTF-8" # this has to be set in ~/.MacOSX/environment.plist as well
export MANPATH="$HOMEBREW_PREFIX/share/man:$MANPATH"
export INFOPATH="$HOMEBREW_PREFIX/share/info:${INFOPATH:-}";
export PROC_IMAP_PROFILE=$HOME/.procimap/mailboxes.cfg
export GNUTERM=wxt
export SYNCTEXREADER=/Applications/Skim.app/Contents/SharedSupport/displayline
export PASSWORD_STORE_ENABLE_EXTENSIONS=true
export GPG_TTY="$(tty)"
export SSH_AUTH_SOCK="${HOME}/.gnupg/S.gpg-agent.ssh"
export BAT_THEME="Monokai Extended Light"
export JULIA_PKG_PRESERVE_TIERED_INSTALLED=true
export PYTHONBREAKPOINT=ipdb.set_trace

export JULIA_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export VECLIB_MAXIMUM_THREADS=1

# Note on ~/.MacOSX/environment.plist post Mountain Lion:
# EnvPane (https://github.com/hschmidt/EnvPane) must be installed in order to
# re-activate support for environment.plist


alias ls='ls -G -h'
alias ..='cd ..'
alias ...='cd ../..'
alias -- +='pushd .'
alias -- -='popd'
alias cd..='cd ..'
alias dir='ls -l'
alias l='ls -a -l -F -G'
alias la='ls -l -a -G'
alias ll='ls -G -h -l'
alias ls-l='ls -l -G'
alias md='mkdir -p'
alias rd='rmdir'
alias less='less -R'
alias :make='make'
alias :wq='exit'
alias :q='exit'
alias :e='vim'
alias vi="'vim' --noplugin -u /dev/null -n"
alias vim="NVIM_APPNAME=vim nvim"
alias tm='tmux new-window'
alias skim='open -a Skim'
alias units='gunits'
alias gitx='open -a GitX'
alias vi='"vim" --noplugin -u /dev/null -n'
alias serve='python -m http.server'
alias lightbg='export "COLORFGBG=0;15" "BAT_THEME=Monokai Extended Light"'
alias darkbg='export "COLORFGBG=15;0" "BAT_THEME=default"'

cppath() {
    if [ "$#" -eq 0 ]; then
        # No arguments → current directory
        realpath "$(pwd)" | tr -d '\n' | pbcopy
    elif [ "$#" -eq 1 ]; then
        # Exactly one argument
        realpath "$1" | tr -d '\n' | pbcopy
    else
        echo "cppath: error: only one path at a time" >&2
        return 1
    fi
}

if [ ! -z "$PS1" ]; then # interactive terminal

    if [ -f `brew --prefix`/etc/bash_completion ]; then
        . `brew --prefix`/etc/bash_completion
    fi

    shopt -s checkwinsize
    #if [ $TERM == 'xterm' ]; then
        #export TERM='xterm-256color'
    #fi
    export PS1="\$(if [ \$? == 0 ]; then echo \\[\\e[0\;32m\\]●\\[\\e[m\\]; else echo \\[\\e[0\;31m\\]●\\[\\e[m\\]; fi) \u@\h:\w> "
    if [ "\$(type -t __git_ps1)" ]; then
        PS1="\$(if [ \$? == 0 ]; then echo \\[\\e[0\;32m\\]●\\[\\e[m\\]; else echo \\[\\e[0\;31m\\]●\\[\\e[m\\]; fi) \u@\h\$(__git_ps1 ' %s'):\w> "
    fi
    source $HOME/.bash/copy.sh
else

    export SHELL_NONINTERACTIVE=1

fi

if [ -f ~/.fzf.bash ]; then
    source ~/.fzf.bash
    export FZF_DEFAULT_COMMAND='fd --type file --follow --hidden --exclude .git --exclude .venv'
    export FZF_CTRL_T_COMMAND="$FZF_DEFAULT_COMMAND"
    export FZF_DEFAULT_OPTS="--ansi"
    _fzf_compgen_dir() {
        fd --type d --hidden --follow --exclude ".git" --exclude ".venv" . "$1"
    }
    _fzf_compgen_path() {
        fd --follow --exclude ".git" --exclude ".venv" . "$1"
    }
fi

if command -v direnv >/dev/null 2>&1; then
    eval "$(direnv hook bash)"
fi
