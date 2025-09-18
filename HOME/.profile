eval `/opt/homebrew/bin/keychain -q --eval --ssh-allow-forwarded --noinherit --host ophelia`
export PROFILE_LOADED=1
if [ -f $HOME/.bashrc ]; then source $HOME/.bashrc; fi
