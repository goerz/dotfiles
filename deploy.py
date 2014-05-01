#!/usr/bin/env python

"""Link dotfiles to their appropriate location in HOME"""

# requires Python >= 2.6

import sys
import os
from functools import partial

# bootstrap code to get the dotfiles.py module from the master branch
os.chdir(os.path.split(os.path.realpath(__file__))[0])
os.system(r'git cat-file -p $(git ls-tree master "dotfiles.py" | cut -d " " -f 3 | cut -f 1) > dotfiles.py')

from dotfiles import make_link, git_update, run_duti, main, DOT

def deploy(overwrite=False, quiet=False, uninstall=False):
    """ Create all necessary symbolic links """
    link = partial(make_link, overwrite=overwrite,
                   quiet=quiet, uninstall=uninstall)
    for file in ['ackrc', 'bashrc', 'git-completion.bash', 'gitconfig',
                 'gitignore_global', 'grace', 'inputrc', 'screenrc',
                 'tmux.conf', 'tmux-completion.sh']:
        link(file, "%s%s" % (DOT, file))
    run_duti(quiet)

main(deploy)
