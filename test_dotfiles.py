#!/usr/bin/env python
import sys
import os
import shutil
import dotfiles
import nose

class DummyOptions(object):
    def __init__(self, quiet=False, overwrite=False, uninstall=False):
        self.quiet = quiet
        self.overwrite = overwrite
        self.uninstall = uninstall


def clean_home():
    try:
        shutil.rmtree(os.path.join("test", "HOME"))
    except OSError:
        pass


@nose.with_setup(clean_home, clean_home)
def test_make_link():

    # create simple file
    dotfiles.make_link('.bashrc', '.bashrc', DummyOptions())
    src_file = os.path.join('test', 'DOTFILES', '.bashrc')
    target_file = os.path.join('test', 'HOME', '.bashrc')
    assert os.path.isfile(target_file)

    # If the file exists and is linked correctly, making another link will do
    # nothing
    dotfiles.make_link('.bashrc', '.bashrc', DummyOptions())
    assert os.path.isfile(target_file)

    # if the file exists as a proper file, an error should be raised
    os.unlink(target_file)
    with open(target_file, 'w') as out_fh:
        out_fh.write("# .bashrc")
    try:
        dotfiles.make_link('.bashrc', '.bashrc', DummyOptions())
        raise AssertionError("linking over existing proper file should fail")
    except OSError:
        pass

    # unless we give the overwrite option
    dotfiles.make_link('.bashrc', '.bashrc', DummyOptions(overwrite=True))
    assert os.path.isfile(target_file)
    assert (os.path.realpath(target_file) == os.path.realpath(src_file))

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
    assert os.path.isfile(target_file)
    dotfiles.make_link('.bashrc', '.bashrc', DummyOptions(uninstall=True))
    assert not os.path.isfile(target_file)

    # but only if the file is actually linked correctly
    with open(target_file, 'w') as out_fh:
        out_fh.write("# .bashrc")
    assert os.path.isfile(target_file)
    dotfiles.make_link('.bashrc', '.bashrc', DummyOptions(uninstall=True))
    assert os.path.isfile(target_file)


@nose.with_setup(clean_home, clean_home)
def test_get():

    # Standard download
    url = 'https://raw.githubusercontent.com/goerz/dotfiles/master/'\
          'README.markdown'
    target_file = os.path.join('test', 'HOME', 'README')
    dotfiles.get(url, 'README', DummyOptions(), make_exec=False)
    assert os.path.isfile(target_file)

    # Should fail if file already exists
    try:
        dotfiles.get(url, 'README', DummyOptions(), make_exec=False)
        raise AssertionError("downloading over existing file should fail")
    except OSError:
        pass

    # Unless overwrite is True
    dotfiles.get(url, 'README', DummyOptions(overwrite=True))
    assert os.path.isfile(target_file) and not os.access(target_file, os.X_OK)

    # If make_exec is True, the resulting file should be executable
    dotfiles.get(url, 'README', DummyOptions(overwrite=True), make_exec=True)
    assert os.path.isfile(target_file) and os.access(target_file, os.X_OK)




if __name__ == "__main__":
    dotfiles.HOME = os.path.join('test', 'HOME')
    dotfiles.DOTFILES = os.path.join('test', 'DOTFILES')
    if os.path.isdir(dotfiles.HOME):
        shutil.rmtree(dotfiles.HOME)
    dotfiles.mkdir(dotfiles.HOME)
    nose.runmodule()
