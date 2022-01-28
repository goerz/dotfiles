# Startup files for bash *login* shells: /etc/profile, then .bash_profile OR
# .bash_login OR .profile, NOT .bashrc (hence, source .bashrc in .bash_profile)
# SSH shells are usually like login shells.
# A non-login interactive shell reads .bashrc (and inherits login variables)
# A non-interative shell (e.g. running a shell script) reads only the file
# given in $BASH_ENV, if defined.
umask 027

export PREFIX=$HOME/.local
export PATH=$PREFIX/bin:$PATH
export LD_LIBRARY_PATH=$PREFIX/lib
export MANPATH=$PREFIX/man:$MANPATH

export PYENV_ROOT=$HOME/.pyenv
export PATH=$PYENV_ROOT/bin:$PYENV_ROOT/shims:$PATH

export EDITOR=vim
export PASSWORD_STORE_ENABLE_EXTENSIONS=true

alias ..='cd ..'
alias ...='cd ../..'
alias -- +='pushd .'
alias -- -='popd'
alias cd..='cd ..'
alias dir='ls -l'
alias l='ls -alF'
alias la='ls -la'
alias ll='ls -l'
alias ls='ls --color -h'
alias ls-l='ls -l'
alias md='mkdir -p'
alias rd='rmdir'
alias less='less -R'
alias tm='tmux new-window'
alias hexdump8='hexdump -e "\"%08.8_ax  \" 4/1 \"%02x \" \"  \" 4/1 \"%02x \"" -e"\"  |\" 8/1 \"%1_p\" \"|\n\""'
alias vimpure='vim --noplugin -u /dev/null -n'
alias open='xdg-open'
alias lightbg='export "COLORFGBG=0;15"'
alias darkbg='export "COLORFGBG=15;0"'
alias serve='python -m http.server 8765'

if [ ! -z "$PS1" ]; then # interactive terminal

    source $HOME/.git-completion.sh
    source $HOME/.tmux-completion.sh
    # Fix bug where completion of $PREFIX -> \$PREFIX
    #complete -F _cd $nospace $filenames cd

    shopt -s checkwinsize
    export PS1="\u@\h:\w> "
    if [ "\$(type -t __git_ps1)" ]; then
        PS1="\u@\h\$(__git_ps1 ' %s'):\w> "
    fi

    # Add loaded envirnomnent modules to prompt
    __module_ps1(){
        # Loaded modules should add a short version of their name to the
        # $PS1_LOADEDMODULES list environment variable if they want this name
        # to appear in the prompt
        if [[ $PS1_LOADEDMODULES && ${PS1_LOADEDMODULES-_} ]]
        then
            printf "[%s] " $PS1_LOADEDMODULES
        else
            printf ""
        fi
    }
    PS1="\$(__module_ps1)$PS1"

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

if [ -d $PYENV_ROOT ]; then
    eval "$(pyenv init -)"
fi
export PATH=$HOME/bin:$PATH
