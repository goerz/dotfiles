#!/usr/bin/env python

"""Link dotfiles to their appropriate location in HOME"""

# requires Python >= 2.6

import os

# bootstrap code to get the dotfiles.py module from the master branch
os.chdir(os.path.split(os.path.realpath(__file__))[0])
os.system(r'git cat-file -p $(git ls-tree origin/master "dotfiles.py" | cut -d " " -f 3 | cut -f 1) > dotfiles.py')

from dotfiles import dot_link, make_link, deploy_vim, main

def deploy(options):
    """ Routine to be called by dotfiles.main. It will be supplied the parsed
        command line options
    """
    dot_link(options)
    deploy_vim('git@github.com:goerz/vimrc.git', options)

main(deploy)
