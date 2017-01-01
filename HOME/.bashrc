# Startup files for bash *login* shells: /etc/profile, then .bash_profile OR
# .bash_login OR .profile, NOT .bashrc (hence, source .bashrc in .bash_profile)
# SSH shells are usually like login shells.
# A non-login interactive shell reads .bashrc (and inherits login variables)
# A non-interative shell (e.g. running a shell script) reads only the file
# given in $BASH_ENV, if defined.
export PATH=$HOME/bin:$HOME/anaconda3/bin:/Library/TeX/texbin:/usr/local/sbin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/usr/X11/bin:/usr/X11R6/bin:/usr/X11/bin
export EDITOR=/usr/bin/vim
export FORTUNE_PATH=$HOME/.fortunes/
export LANG="en_US.UTF-8"
export LC_ALL="en_US.UTF-8"
export LC_CTYPE="en_US.UTF-8" # this has to be set in ~/.MacOSX/environment.plist as well
export MANPATH=/opt/local/man:$MANPATH
export PROC_IMAP_PROFILE=$HOME/.procimap/mailboxes.cfg
export GNUTERM=wxt
export WORKON_HOME=$HOME/.virtualenvs
export SYNCTEXREADER=/Applications/Skim.app/Contents/SharedSupport/displayline

# Note on ~/.MacOSX/environment.plist post Mountain Lion:
# EnvPane (https://github.com/hschmidt/EnvPane) must be installed in order to
# re-activate support for environment.plist

source /usr/local/opt/modules/Modules/init/bash
if type -t module > /dev/null; then
    # only if module command is loaded!
    module use --append $HOME/.modules
fi

export PREFIX=$HOME/local
export PATH=$PATH:$PREFIX/bin

alias ls='ls -G -h'
alias fortune='fortune.py -a'
#alias vim='vim -X'
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
alias vim=nvim
alias tm='tmux new-window'
alias skim='open -a Skim'
alias preview='open -a Preview'
alias units='gunits'
alias gitx='open -a GitX'
alias wlan='networksetup -setairportpower en1'
alias ssh-x='ssh -c arcfour,blowfish-cbc -XC'
alias virtualenvwrapper='source /usr/local/bin/virtualenvwrapper.sh'
alias mosh_bigboy='mosh --server="LD_LIBRARY_PATH=/home/goerz/local/lib /home/goerz/local/bin/mosh-server" bigboy'
alias vimpure='vim --noplugin -u /dev/null -n'
alias sc='ssh_clipboard.py -c'
alias sp='ssh_clipboard.py -p'
alias serve='python -m SimpleHTTPServer'
alias lightbg='export "COLORFGBG=0;15"'
alias darkbg='export "COLORFGBG=15;0"'
alias keyboardoff='sudo kextunload /System/Library/Extensions/AppleUSBTopCase.kext/Contents/PlugIns/AppleUSBTCKeyboard.kext/'
alias keyboardon='sudo kextload /System/Library/Extensions/AppleUSBTopCase.kext/Contents/PlugIns/AppleUSBTCKeyboard.kext'
alias canopyenv='env PATH=$HOME/Library/Enthought/Canopy_64bit/User/bin:$PATH MPLCONFIGDIR=$HOME/.matplotlib.canopy'
alias dodssh='/usr/local/ossh/bin/ssh'
alias dodscp='/usr/local/ossh/bin/scp'

# sudo pmset -a hibernatemode /n/.
# 0 - Old style - just goes to sleep.
# 1 - Only Hibernate
# 3 - Default - goes to sleep but writes RAM contents to disk just in case.
# 5 - Only Hibernate mode but if you use secure virtual memory.
# 7 - The Default but if you use secure virtual memory.
alias hibernateon="sudo pmset -a hibernatemode 5"
alias hibernateoff="sudo pmset -a hibernatemode 7"


if [ ! -z "$PS1" ]; then # interactive terminal

    function epoch()
    {
        perl -e "print scalar(localtime(${1})), \"\n\""
    }

    function wifi-password()
    # http://lifehacker.com/find-the-wi-fi-password-for-your-current-network-with-t-1717978747
    {
        security find-generic-password -ga ${1} | grep password
    }


    if [ -f `brew --prefix`/etc/bash_completion ]; then
        . `brew --prefix`/etc/bash_completion
    fi

    shopt -s checkwinsize
    #if [ $TERM == 'xterm' ]; then
        #export TERM='xterm-256color'
    #fi
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

    source $HOME/.bash/copy.sh
fi
