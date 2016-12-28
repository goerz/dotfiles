"""
Tests for dotfiles.py

Run with `py.test test_dotfiles.py`
"""
import os
from os import readlink
from os.path import join, isfile, isdir, islink, realpath
import shutil

import pytest

import dotfiles


class DummyOptions(object):
    def __init__(self, quiet=False, overwrite=False, uninstall=False):
        self.quiet = quiet
        self.overwrite = overwrite
        self.uninstall = uninstall


@pytest.fixture
def test_home():
    homedir = join("test", "HOME")
    try:
        shutil.rmtree(homedir)
    except OSError:
        pass
    dotfiles.mkdir(homedir)
    yield homedir
    try:
        shutil.rmtree(homedir)
    except OSError:
        pass


def test_make_link(test_home):

    dotfiles.HOME = test_home
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
    orig_input = dotfiles.input
    dotfiles.input = lambda query: 'yes'
    dotfiles.make_link('.bashrc', '.bashrc', DummyOptions(quiet=False))
    dotfiles.input = orig_input
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


def test_get(test_home):

    dotfiles.HOME = test_home

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


def test_check_remote_repo():
    """Test checking accessability of remote repo"""
    assert dotfiles.check_remote_repo('https://github.com/goerz/vimrc.git')
    assert not dotfiles.check_remote_repo('http://example.com')


def test_deploy_repo(test_home):
    """Test deployment of a git repo"""
    dotfiles.HOME = test_home
    dotfiles.DOTFILES = join('test', 'DOTFILES')
    dotfiles.mkdir(dotfiles.HOME)
    # checkout (failing)
    dotfiles.mkdir(os.path.join(dotfiles.HOME, 'myvimdir'))
    dotfiles.deploy_repo('https://github.com/goerz/vimrc.git', 'myvimdir',
                         DummyOptions())
    assert isdir(join(dotfiles.HOME, 'myvimdir'))
    assert not isfile(join(dotfiles.HOME, 'myvimdir', 'init.vim'))
    # overwrite checkout
    dotfiles.deploy_repo('https://github.com/goerz/vimrc.git', 'myvimdir',
                         DummyOptions(overwrite=True))
    assert isdir(join(dotfiles.HOME, 'myvimdir'))
    assert isfile(join(dotfiles.HOME, 'myvimdir', 'init.vim'))
    # refresh
    dotfiles.deploy_repo('https://github.com/goerz/vimrc.git', 'myvimdir',
                         DummyOptions(), allow_uninstall='clean')
    # clean uninstall
    dotfiles.deploy_repo('https://github.com/goerz/vimrc.git', 'myvimdir',
                         DummyOptions(uninstall=True))
    assert not isfile(join(dotfiles.HOME, 'myvimdir', 'init.vim'))
    assert not isdir(join(dotfiles.HOME, 'myvimdir'))
    # new checkout
    dotfiles.deploy_repo('https://github.com/goerz/vimrc.git', 'myvimdir',
                         DummyOptions())
    with open(os.path.join(dotfiles.HOME, 'myvimdir', 'new_file.txt'), 'w') \
            as out_fh:
        out_fh.write("Hello World")
    assert isdir(join(dotfiles.HOME, 'myvimdir'))
    assert isfile(join(dotfiles.HOME, 'myvimdir', 'init.vim'))
    assert isfile(join(dotfiles.HOME, 'myvimdir', 'new_file.txt'))
    # clean uninstall (failing)
    dotfiles.deploy_repo('https://github.com/goerz/vimrc.git', 'myvimdir',
                         DummyOptions(uninstall=True), allow_uninstall='clean')
    assert isfile(join(dotfiles.HOME, 'myvimdir', 'new_file.txt'))
    # dirty uninstall
    dotfiles.deploy_repo('https://github.com/goerz/vimrc.git', 'myvimdir',
                         DummyOptions(uninstall=True), allow_uninstall='dirty')
    assert not isdir(join(dotfiles.HOME, 'myvimdir'))


def test_deploy_vim(test_home, monkeypatch):
    """Test vim deployment"""

    dotfiles.HOME = test_home
    dotfiles.DOTFILES = join('test', 'DOTFILES')
    monkeypatch.delenv('XDG_CONFIG_HOME', raising=False)

    dotfiles.mkdir(dotfiles.HOME)
    dotfiles.deploy_vim('https://github.com/goerz/vimrc.git', DummyOptions())
    assert islink(join(dotfiles.HOME, '.vimrc'))
    assert isdir(join(dotfiles.HOME, '.vim'))
    assert isfile(join(dotfiles.HOME, '.vim', 'init.vim'))
    assert islink(join(dotfiles.HOME, '.config', 'nvim'))
    assert isfile(join(dotfiles.HOME, '.config', 'nvim', 'init.vim'))
    # A second call should update the repository
    dotfiles.deploy_vim('https://github.com/goerz/vimrc.git', DummyOptions())
    # uninstall
    dotfiles.deploy_vim('https://github.com/goerz/vimrc.git',
                        DummyOptions(uninstall=True))
    assert not isfile(join(dotfiles.HOME, '.vimrc'))
    assert not islink(join(dotfiles.HOME, '.config', 'nvim'))
    assert not isfile(join(dotfiles.HOME, '.config', 'nvim', 'init.vim'))


def test_make_links(test_home):

    dotfiles.HOME = test_home
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
