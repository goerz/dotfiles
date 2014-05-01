Dotfiles & Management Scripts
=============================

This repository contains dotfiles for various Unix-based systems (MacOS, Linux),
along with management scripts to deploy them.

The collection for dotfiles for each system is in a separate branch; The
'master' branch only contains a Python library that provides utility functions
for deploying and managing the dotfiles: Each 'system' branch should contain a
`deploy.py` script, which uses the code from the master branch `dotfiles.py`.

The deploy e.g. the 'mac' branch to a new computer, the following steps should
be taken from within the home folder:

    git clone git@github.com:goerz/dotfiles.git .dotfiles
    cd .dotfiles
    git checkout -t origin/mac
    ./deploy.py --overwrite

Rerunning the `deploy.py` script at a later point (possibly with the `--quiet`
option) will pull the latest changes from `origin` and update symlinks as
necessary.

In order to define a new configuration ("system branch"), run something like

    git clone git@github.com:goerz/dotfiles.git .dotfiles
    cd .dotfiles
    git checkout --orphan name_of_new_system
    git rm -f *
    # copy in dotfiles, write deploy.py script
    git add .
    git commit -m 'New system "name_of_new_system"'
    git push -u origin name_of_new_system
    ./deploy.py --overwrite


