eval `/opt/homebrew/bin/keychain -q --eval --agents ssh --host ophelia --inherit any`
export PROFILE_LOADED=1
if [ -f $HOME/.bashrc ]; then source $HOME/.bashrc; fi
