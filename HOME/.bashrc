# Startup files for bash *login* shells: /etc/profile, then .bash_profile OR
# .bash_login OR .profile, NOT .bashrc (hence, source .bashrc in .bash_profile)
# SSH shells are usually like login shells.
# A non-login interactive shell reads .bashrc (and inherits login variables)
# A non-interative shell (e.g. running a shell script) reads only the file
# given in $BASH_ENV, if defined.

arch_name="$(uname -m)"

if [ "${arch_name}" = "x86_64" ]; then
    if [ "$(sysctl -in sysctl.proc_translated)" = "1" ]; then
        export SHELL_ARCH="rosetta2"
        export PYENV_ROOT="$HOME/.pyenv-rosetta"
    else
        export SHELL_ARCH="intel"
        export PYENV_ROOT="$HOME/.pyenv"
    fi
    export HOMEBREW_PREFIX="/usr/local";
    export HOMEBREW_CELLAR="/usr/local/Cellar";
    export HOMEBREW_REPOSITORY="/usr/local/Homebrew";
    export GNUBIN="/usr/local/opt/make/libexec/gnubin"
elif [ "${arch_name}" = "arm64" ]; then
    export SHELL_ARCH="arm"
    export HOMEBREW_PREFIX="/opt/homebrew";
    export HOMEBREW_CELLAR="/opt/homebrew/Cellar";
    export HOMEBREW_REPOSITORY="/opt/homebrew";
    export PYENV_ROOT="$HOME/.pyenv"
else
    echo "Unknown architecture: ${arch_name}"
fi

export JULIAUP_ROOT=$HOME/.juliaup/
export PLENV_ROOT="$HOME/.plenv"
export PREFIX="$HOME/.local"
export EDITOR=$HOMEBREW_PREFIX/bin/nvim
export GNUBIN="$HOMEBREW_PREFIX/opt/make/libexec/gnubin"
export PATH="/usr/local/sbin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/usr/X11/bin:/usr/X11R6/bin:/usr/X11/bin"
export PATH="/Library/TeX/texbin:$PATH"
export PATH="$HOMEBREW_PREFIX/bin:$HOMEBREW_PREFIX/sbin:$GNUBIN:$PATH"
export PATH="$PLENV_ROOT/bin:$PLENV_ROOT/shims:$PATH"
export PATH="$PYENV_ROOT/bin:$PYENV_ROOT/shims:$PATH"
export PATH="$JULIAUP_ROOT/bin:$PATH"
export PATH="$HOME/bin:$PREFIX/bin:$PATH"
export FORTUNE_PATH=$HOME/.fortunes/
export LANG="en_US.UTF-8"
export LC_ALL="en_US.UTF-8"
export LC_CTYPE="en_US.UTF-8" # this has to be set in ~/.MacOSX/environment.plist as well
export MANPATH="$HOMEBREW_PREFIX/share/man:$MANPATH"
export INFOPATH="$HOMEBREW_PREFIX/share/info:${INFOPATH:-}";
export PROC_IMAP_PROFILE=$HOME/.procimap/mailboxes.cfg
export GNUTERM=wxt
export WORKON_HOME=$HOME/.virtualenvs
export SYNCTEXREADER=/Applications/Skim.app/Contents/SharedSupport/displayline
export PASSWORD_STORE_ENABLE_EXTENSIONS=true
export GPG_TTY="$(tty)"
export SSH_AUTH_SOCK="${HOME}/.gnupg/S.gpg-agent.ssh"
export BAT_THEME="Monokai Extended Light"
export JULIA_PKG_PRESERVE_TIERED_INSTALLED=true

# Note on ~/.MacOSX/environment.plist post Mountain Lion:
# EnvPane (https://github.com/hschmidt/EnvPane) must be installed in order to
# re-activate support for environment.plist


alias rbash='/usr/local/bin/bash'
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


if [ ! -z "$PS1" ]; then # interactive terminal

    if [ -f `brew --prefix`/etc/bash_completion ]; then
        . `brew --prefix`/etc/bash_completion
    fi

    shopt -s checkwinsize
    #if [ $TERM == 'xterm' ]; then
        #export TERM='xterm-256color'
    #fi
    if [ "$SHELL_ARCH" = "rosetta2" ]; then
        export PS1="\$(if [ \$? == 0 ]; then echo \\[\\e[0\;32m\\]●\\[\\e[m\\]; else echo \\[\\e[0\;31m\\]●\\[\\e[m\\]; fi) \u@\h(r):\w> "
        if [ "\$(type -t __git_ps1)" ]; then
            PS1="\$(if [ \$? == 0 ]; then echo \\[\\e[0\;32m\\]●\\[\\e[m\\]; else echo \\[\\e[0\;31m\\]●\\[\\e[m\\]; fi) \u@\h(r)\$(__git_ps1 ' %s'):\w> "
        fi
    else
        export PS1="\$(if [ \$? == 0 ]; then echo \\[\\e[0\;32m\\]●\\[\\e[m\\]; else echo \\[\\e[0\;31m\\]●\\[\\e[m\\]; fi) \u@\h:\w> "
        if [ "\$(type -t __git_ps1)" ]; then
            PS1="\$(if [ \$? == 0 ]; then echo \\[\\e[0\;32m\\]●\\[\\e[m\\]; else echo \\[\\e[0\;31m\\]●\\[\\e[m\\]; fi) \u@\h\$(__git_ps1 ' %s'):\w> "
        fi
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

if [ -d "$PYENV_ROOT" ]; then
    eval "$(pyenv init -)"
fi
