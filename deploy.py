#!/usr/bin/env python

"""Link dotfiles to their appropriate location in $HOME"""

# requires Python >= 2.6

import os

# bootstrap code to get the dotfiles.py module from the master branch
os.chdir(os.path.split(os.path.realpath(__file__))[0])
os.system(r'rm -rf *.pyc __pycache__')
os.system(r'git cat-file -p $(git ls-tree origin/master "dotfiles.py" | cut -d " " -f 3 | cut -f 1) > dotfiles.py')

import dotfiles

def deploy(options):
    """ Routine to be called by dotfiles.main. It will be supplied the parsed
        command line options
    """
    dotfiles.make_links('HOME', options)
    dotfiles.deploy_vim('https://github.com/goerz/vimrc.git', options)
    dotfiles.set_crontab(options.quiet)

dotfiles.main(deploy)
