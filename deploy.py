#!/usr/bin/env python

"""Link dotfiles to their appropriate location in HOME"""

# requires Python >= 2.6

import os

# bootstrap code to get the dotfiles.py module from the master branch
os.chdir(os.path.split(os.path.realpath(__file__))[0])
os.system(r'git cat-file -p $(git ls-tree origin/master "dotfiles.py" | cut -d " " -f 3 | cut -f 1) > dotfiles.py')

from dotfiles import dot_link, deploy_vim, get, main

def get_scripts(options):
    """ Download various scripts into ~/bin """
    get('https://raw.githubusercontent.com/goerz/git-graph/master/git-graph.py',
         'bin/git-graph', options, make_exec=True)
    get('http://michaelgoerz.net/blog/2009/10/three-little-git-scripts/git-cat',
        'bin/git-cat', options, make_exec=True)
    get('http://michaelgoerz.net/blog/2009/10/three-little-git-scripts/git-vimdiff',
        'bin/git-vimdiff', options, make_exec=True)
    get('https://raw.githubusercontent.com/goerz/git-repos/master/git-repos',
        'bin/git-repos', options, make_exec=True)
    get('http://beyondgrep.com/ack-2.12-single-file',
        'bin/ack', options, make_exec=True)

def deploy(options):
    """ Routine to be called by dotfiles.main. It will be supplied the parsed
        command line options
    """
    dot_link(options)
    deploy_vim('git@github.com:goerz/vimrc.git', options)
    get_scripts(options)

main(deploy)
