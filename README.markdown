Dotfiles & Management Scripts
=============================

This repository contains dotfiles (configuration files) for various Unix-based
systems (MacOS, Linux), along with management scripts to deploy, update, and
synchronize them.


## System Overview ##

The collection for dotfiles for each system is in a separate branch; The
`master` branch only contains a Python `dotfiles` module that provides utility
functions for deploying and managing the dotfiles.

Each system branch should contain a `deploy.py` script which uses the master
branch `dotfiles` module.

The recommended design is to have a checkout of a system branch in
`$HOME/.dotfiles`, containing something like the following file structure:

    ~/.dotfiles
    ├── HOME
    │   ├── .bashrc
    │   ├── .config
    │   │   └── Terminal
    │   │       └── terminalrc
    │   ├── .crontab
    │   ├── .gitconfig
    │   ├── .grace
    │   │   ├── gracerc.user
    │   │   └── templates
    │   │       ├── Default.agr
    │   └── .tmux.conf
    └── deploy.py

The main purpose of the `deploy.py` script is to link the contents of
`~/.dotfiles/HOME` to your home folder. The links will be intermixed with
existing files and folders, e.g. `~/.config/Terminal/terminalrc` will link to
`~/.dotfiles/HOME/.config/Terminal/terminalrc`, while other files and folders
in `~/.config` will remain unaffected.

Running `deploy.py` repeatedly will update the dotfiles to the latest version.


## Structure of the deploy.py Script ##

Each deploy script should start with code to bootstrap the latest dotfiles
script:

    import os
    os.chdir(os.path.split(os.path.realpath(__file__))[0])
    os.system(r'rm -rf *.pyc __pycache__')
    os.system(r'git cat-file -p $(git ls-tree origin/master "dotfiles.py" | cut -d " " -f 3 | cut -f 1) > dotfiles.py')
    import dotfiles

Then, a `deploy` routine must be defined, e.g.

    def deploy(options):
        """ Routine to be called by dotfiles.main. It will be supplied the parsed
            command line options
        """
        dotfiles.make_links('HOME', options)
        dotfiles.deploy_vim('https://github.com/goerz/vimrc.git', options)
        dotfiles.set_crontab(options.quiet)

Finally, the `dotfiles.main` routine is called. This routine will handle parsing
of command line options (`deploy.py -h`). It also pulls in the current version
of the entire dotfiles folder via git.

The `deploy.py` script takes the following options:

    --quiet      Suppress all output
    --overwrite  Overwrite link targets if they exist already
    --uninstall  Remove any existing links to dotfiles

Note that the name of the folder collecting all the dotfiles is `HOME` in the
above example simply by convention; any other name will work as well, as long it
is properly passed to the `make_links` routine.


## Deployment ##

The deploy e.g. the 'mac' branch to a new computer, the following steps should
be taken from within the home folder:

    git clone git@github.com:goerz/dotfiles.git .dotfiles
    cd .dotfiles
    git checkout -t origin/mac
    ./deploy.py --overwrite

Rerunning the `deploy.py` script at a later point (possibly with the `--quiet`
option) will pull the latest changes from `origin` and update symlinks as
necessary. It is recommended to run `deploy.py` automatically at regular
intervals as a cronjob.


## Creating a New System Configuration ##

In order to define a new configuration ("system branch"), run something like

    git clone git@github.com:goerz/dotfiles.git .dotfiles
    cd .dotfiles
    git checkout --orphan name_of_new_system
    git rm -f *
    mkdir HOME
    # copy in dotfiles, to HOME subfolder
    # write deploy.py script
    git add .
    git commit -m 'New system "name_of_new_system"'
    git push -u origin name_of_new_system
    ./deploy.py --overwrite


