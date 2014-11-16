#!/usr/bin/env python
import sys
import os
import shutil
import dotfiles
import nose
import __builtin__
from os.path import join, isfile, isdir, realpath
from os import readlink
"""
Run tests of dotfiles.py

Options:

--nocapture  print the STDOUT from all tests
-v           give more information about tests
"""

class DummyOptions(object):
    def __init__(self, quiet=False, overwrite=False, uninstall=False):
        self.quiet = quiet
        self.overwrite = overwrite
        self.uninstall = uninstall


def clean_home():
    try:
        shutil.rmtree(join("test", "HOME"))
    except OSError:
        pass


@nose.with_setup(clean_home, clean_home)
def test_make_link():

    dotfiles.HOME = join('test', 'HOME')
    dotfiles.DOTFILES = join('test', 'DOTFILES')

    # create simple file
    dotfiles.make_link('.bashrc', '.bashrc', DummyOptions())
    src_file = join(dotfiles.DOTFILES, '.bashrc')
    target_file = join(dotfiles.HOME, '.bashrc')
    assert isfile(target_file)

    # If the file exists and is linked correctly, making another link will do
    # nothing
    dotfiles.make_link('.bashrc', '.bashrc', DummyOptions())
    assert isfile(target_file)

    # if the file exists as a proper file, an error should be raised
    os.unlink(target_file)
    with open(target_file, 'w') as out_fh:
        out_fh.write("# .bashrc")
    try:
        dotfiles.make_link('.bashrc', '.bashrc', DummyOptions(quiet=True))
        raise AssertionError("linking over existing proper file should fail")
    except OSError:
        pass

    # we may also confirm the overwrite interactively
    old_raw_input = __builtin__.raw_input
    __builtin__.raw_input = lambda query: 'yes'
    dotfiles.make_link('.bashrc', '.bashrc', DummyOptions(quiet=False))
    __builtin__.raw_input = old_raw_input
    assert isfile(target_file)

    # or give the overwrite option
    os.unlink(target_file)
    with open(target_file, 'w') as out_fh:
        out_fh.write("# .bashrc")
    dotfiles.make_link('.bashrc', '.bashrc', DummyOptions(overwrite=True))
    assert isfile(target_file)
    assert (realpath(target_file) == realpath(src_file))

    # What should never work, however, is to overwrite a folder
    os.unlink(target_file)
    dotfiles.mkdir(target_file)
    try:
        dotfiles.make_link('.bashrc', '.bashrc', DummyOptions(overwrite=True))
        raise AssertionError("overwriting existing folder should fail")
    except OSError:
        pass
    shutil.rmtree(target_file)

    # The uninstall option should remove the file
    dotfiles.make_link('.bashrc', '.bashrc', DummyOptions())
    assert isfile(target_file)
    dotfiles.make_link('.bashrc', '.bashrc', DummyOptions(uninstall=True))
    assert not isfile(target_file)

    # but only if the file is actually linked correctly
    dotfiles.mkdir(dotfiles.HOME)
    with open(target_file, 'w') as out_fh:
        out_fh.write("# .bashrc")
    assert isfile(target_file)
    dotfiles.make_link('.bashrc', '.bashrc', DummyOptions(uninstall=True))
    assert isfile(target_file)


@nose.with_setup(clean_home, clean_home)
def test_get():

    dotfiles.HOME = join('test', 'HOME')

    # Standard download
    url = 'https://raw.githubusercontent.com/goerz/dotfiles/master/'\
          'README.markdown'
    target_file = join('test', 'HOME', 'README')
    dotfiles.get(url, 'README', DummyOptions(), make_exec=False)
    assert isfile(target_file)

    # Should fail if file already exists
    try:
        dotfiles.get(url, 'README', DummyOptions(), make_exec=False)
        raise AssertionError("downloading over existing file should fail")
    except OSError:
        pass

    # Unless overwrite is True
    dotfiles.get(url, 'README', DummyOptions(overwrite=True))
    assert isfile(target_file) and not os.access(target_file, os.X_OK)

    # If make_exec is True, the resulting file should be executable
    dotfiles.get(url, 'README', DummyOptions(overwrite=True), make_exec=True)
    assert isfile(target_file) and os.access(target_file, os.X_OK)


@nose.with_setup(clean_home, clean_home)
def test_deploy_vim():

    dotfiles.HOME = join('test', 'HOME')
    dotfiles.DOTFILES = join('test', 'DOTFILES')

    dotfiles.mkdir(dotfiles.HOME)
    dotfiles.deploy_vim('https://github.com/goerz/vimrc.git', DummyOptions())
    assert isfile(join(dotfiles.HOME, '.vimrc'))
    assert isdir(join(dotfiles.HOME, '.vim'))
    assert isfile(join(dotfiles.HOME, '.vim', 'vimrc'))
    # A second call should update the repository
    dotfiles.deploy_vim('https://github.com/goerz/vimrc.git', DummyOptions())


@nose.with_setup(clean_home, clean_home)
def test_make_links():

    dotfiles.HOME = join('test', 'HOME')
    shutil.copytree(join('test', 'DOTFILES'),
                    join(dotfiles.HOME, '.dotfiles', 'HOME'))
    dotfiles.DOTFILES = join(dotfiles.HOME, '.dotfiles')

    dotfiles.make_links('HOME', DummyOptions())

    def check_link(link_file, dest):
        assert readlink(os.sep.join(link_file.split("/"))) \
                == os.sep.join(dest.split("/"))

    check_link('test/HOME/bin/ack', '../.dotfiles/HOME/bin/ack')
    assert os.access(join(dotfiles.HOME, 'bin', 'ack'), os.X_OK)
    check_link('test/HOME/.bashrc', '.dotfiles/HOME/.bashrc')
    check_link('test/HOME/.grace/gracerc.user',
               '../.dotfiles/HOME/.grace/gracerc.user')
    check_link('test/HOME/.grace/templates/Default.agr',
               '../../.dotfiles/HOME/.grace/templates/Default.agr')
    check_link('test/HOME/.config/Terminal/terminalrc',
               '../../.dotfiles/HOME/.config/Terminal/terminalrc')

    # Running make_links again should not change anything
    dotfiles.make_links('HOME', DummyOptions())

    check_link('test/HOME/.bashrc', '.dotfiles/HOME/.bashrc')
    check_link('test/HOME/.grace/gracerc.user',
               '../.dotfiles/HOME/.grace/gracerc.user')
    check_link('test/HOME/.grace/templates/Default.agr',
               '../../.dotfiles/HOME/.grace/templates/Default.agr')
    check_link('test/HOME/.config/Terminal/terminalrc',
               '../../.dotfiles/HOME/.config/Terminal/terminalrc')

    # uninstall should remove all linked files and empty folders
    dotfiles.make_links('HOME', DummyOptions(uninstall=True))
    assert isdir(dotfiles.DOTFILES)
    assert not isfile(join(dotfiles.HOME, '.bashrc'))
    assert not isdir(join(dotfiles.HOME, '.grace'))



if __name__ == "__main__":
    dotfiles.HOME = join('test', 'HOME')
    dotfiles.DOTFILES = join('test', 'DOTFILES')
    if isdir(dotfiles.HOME):
        shutil.rmtree(dotfiles.HOME)
    dotfiles.mkdir(dotfiles.HOME)
    nose.runmodule()
