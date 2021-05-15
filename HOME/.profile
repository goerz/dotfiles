eval `/opt/homebrew/bin/keychain -q --eval --agents ssh --host ophelia --inherit any`
export PROFILE_LOADED=1
if [ -f $HOME/.bashrc ]; then source $HOME/.bashrc; fi

test -e "${HOME}/.iterm2_shell_integration.bash" && source "${HOME}/.iterm2_shell_integration.bash"
