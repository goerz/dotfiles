#!/usr/bin/env python
""" Utilitiy functions to deploy dotfiles """

import os
import stat
import sys
import shutil
from glob import glob
from subprocess import call, STDOUT
from optparse import OptionParser
from urllib import urlretrieve


HOME          = os.environ['HOME']
DOTFILES      = os.path.split(os.path.realpath(__file__))[0]
DOT           = '.'


def make_link(src, dst, options):
    """ Create a symbolic link pointing to src named dst.

        src is a path relative to DOTFILES
        dst is a path relative to HOME

        If options.overwrite is True and dst already exists, remove the
        existing file before creating the link.

        If options.uninstall is True, don't create any symbolic links, but
        remove them if they exist. Any empty folder that results from this will
        also be deleted.

        If the dst already exists and is a symbolic link to src, the routine
        will exit silently.

        For every newly created link, a message will be printed to screen,
        unless options.quiet is given als False

        Raises OSError if an operation cannot be completed
    """
    abs_src = os.path.join(DOTFILES, src)
    abs_dst = os.path.join(HOME, dst)
    dst_path = os.path.split(abs_dst)[0]
    if options.overwrite and not options.uninstall:
        if os.path.isfile(abs_dst) or os.path.islink(abs_dst):
            os.unlink(abs_dst)
        elif os.path.isdir(abs_dst):
            if os.path.isdir(abs_src):
                shutil.rmtree(abs_dst)
            else:
                raise OSError("Existing directory %s " % abs_dst
                            + "would be overwritten by file %s" % abs_src)
    link_file   = abs_dst
    link_target = os.path.relpath(abs_src, dst_path)
    if options.uninstall:
        if (os.path.realpath(abs_dst) == os.path.realpath(abs_src)):
            if not options.quiet:
                print("removing %s" % abs_dst)
            os.unlink(abs_dst)
            # remove empty folder
            try:
                folder = os.path.split(abs_dst)[0]
                while folder != '':
                    os.rmdir(folder)
                    folder = os.path.split(folder)[0]
            except OSError:
                pass # folder is not empty
    else:
        if (os.path.realpath(abs_dst) != os.path.realpath(abs_src)):
            if not options.quiet:
                print("%s -> %s" % (link_file, abs_src))
            mkdir(dst_path)
            os.symlink(link_target, link_file)


def dot_link(options, files=None, exclude=None):
    """ Run make_link for every file name in 'files' that is not also in
        'exclude'. Both 'files' and 'exclude' must contain filenames relative
        to the DOTFILES folder. A DOT is pre-pended to the link destination.

        For example

            >>> dot_link(['bashrc', ], exclude=[])

        will call

            make_link('bashrc', '.bashrc')

        which crates a symlink ~/.bashrc, pointing to ~/.dotfiles/.bashrc,
        assuming that DOTFILES is ~/.dotfiles

        If 'files' is not specified (i.e., files is None), it is set to include
        all files in DOTFILE. This should usually be used in conjuction with
        exclude.

        The 'exlude' array will automatically be expanded to include the files
        'deploy.py', 'deploy.pyc', 'dotfiles.py', and 'dotfiles.pyc'.

        The options are passed to the make_link routine directly
    """
    if files is None:
        files = glob(os.path.join(DOTFILES, '*'))
    if exclude is None:
        exclude = []
    exclude += ['deploy.py', 'deploy.pyc', 'dotfiles.py', 'dotfiles.pyc']
    for filename in files:
        filename = os.path.basename(filename)
        if not filename in exclude:
            make_link(filename, DOT+filename, options)


def which(program):
    """ Return the absolute path of the given program, or None if the program
        is not available -- like Unix which utility)
    """
    def is_exe(fpath):
        """Is fpath an executable?"""
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath = os.path.split(program)[0]
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None


def deploy_vim(repo, options):
    """ Deploy vimrc from the given git repository.

        If ~/.vim does not exist already, the given repo will be cloned to
        ~/.vim, and a symlink ~/.vimrc -> ~/.vim/vimrc will be created.

        If ~/.vim does exist and is a git repository, it will be updated to the
        latest revision.

        If optins.overwrite is True, and ~/.vim/vimrc exists, any existing file
        ~/.vimrc will be removed and be replaced with a symlink to ~/.vim/vimrc

        The flag options.uninstall will only affect the file ~/.vimrc, the .vim
        folder is never touched.
    """
    vimdir       = os.path.join(HOME,".vim")
    vimrc        = os.path.join(HOME,".vimrc")
    vimrc_target = os.path.join(vimdir,"vimrc")
    stdout = None
    if options.quiet:
        stdout = open(os.devnull, 'w')
    if (not os.path.exists(vimdir)):
        cmd = ['git', 'clone', repo, '.vim']
        if not options.quiet:
            print(" ".join(cmd))
        ret = call(cmd, cwd=HOME, stderr=STDOUT, stdout=stdout)
        if ret != 0:
            if not options.quiet:
                print("WARNING: git returned nonzero exist status (%s)")
    else:
        git_update(vimdir, options.quiet)
    if options.overwrite:
        if os.path.isfile(vimrc) or os.path.islink(vimrc):
            os.unlink(vimrc)
    if os.path.isfile(vimrc_target):
        make_link(os.path.abspath(vimrc_target), os.path.abspath(vimrc),
                  options)
    else:
        raise OSError("Missing file %s" % (vimrc))


def mkdir(directory):
    """ Recursive mkdir

        If directory already exists, do nothing.
        If directory cannot be created, raise OSError
        If parent directories do not exist, make them as well
    """
    if os.path.isdir(directory):
        pass
    elif os.path.isfile(directory):
        raise OSError("a file with the same name as the desired " \
                       "dir, '%s', already exists." % directory)
    else:
        head, tail = os.path.split(directory)
        if head and not os.path.isdir(head):
            mkdir(head)
        if tail:
            os.mkdir(directory)


def get(url, destination, options, make_exec=False):
    """ Download the file at the given URL to destination (relative to HOME).
        If make_exec is True, also make it executable.

        If the file already exists, an OSError will be raise, unless
        options.overwrite is True.

        If options.uninstall is True, destination will be deleted if it exists.
    """
    destination = os.path.join(HOME, destination)
    mkdir(os.path.split(destination)[0])
    if os.path.isfile(destination):
        if (options.overwrite or options.uninstall):
            if (options.uninstall and not options.quiet):
                print("removing %s" % destination)
            os.unlink(destination)
            if (options.uninstall):
                return
        else:
            raise OSError("File %s already exists" % destination)
    if os.path.isdir(destination):
        raise OSError("%s is folder, must be file" % destination)
    if not options.quiet:
        print("%s -> %s" % (url, destination))
    urlretrieve(url, destination)
    if make_exec:
        perms = os.stat(destination)
        # chmod a+x
        os.chmod(destination, perms.st_mode
                 |  stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def git_update(folder=DOTFILES, quiet=False):
    """ Perform an update of the repository in the given folder """
    git = which('git')
    stdout = None
    if quiet:
        stdout = open(os.devnull, 'w')
    if git is not None:
        if not quiet:
            print("Updating %s" % folder)
        cmd = [git, 'remote', 'update', '-p']
        ret = call(cmd, cwd=folder, stderr=STDOUT, stdout=stdout)
        if ret != 0:
            if not quiet:
                print("WARNING: git returned nonzero exist status (%s)")
        cmd = [git, 'merge', '--ff-only', '@{u}']
        ret = call(cmd, cwd=folder, stderr=STDOUT, stdout=stdout)
        if ret != 0:
            if not quiet:
                print("WARNING: git returned nonzero exist status (%s)")
    else:
        if not quiet:
            print("WARNING: git is not available")


def run_duti(quiet=False):
    """ Run the duti utility, which sets up handlers for opening files on
        MacOS
    """
    duti = which('duti')
    if duti is not None:
        cmd = [duti, os.path.join(DOTFILES, "handlers.duti")]
        if not quiet:
            print(" ".join(cmd))
        ret = call(cmd)
        if ret != 0:
            raise OSError("duti returned nonzero exist status (%s)" % ret)
    else:
        if not quiet:
            print("WARNING: duti is not available")


def get_options(argv=None):
    """ Parse command line options. return options object """
    if argv is None:
        argv = sys.argv
    arg_parser = OptionParser(usage="usage: %prog [options]")
    arg_parser.add_option(
        '--quiet', action='store_true', dest='quiet',
        default=False, help="Suppress all output")
    arg_parser.add_option(
        '--overwrite', action='store_true', dest='overwrite',
        default=False, help="Overwrite link targets if they exist already")
    arg_parser.add_option(
        '--uninstall', action='store_true', dest='uninstall',
        default=False, help="Remove any existing links to dotfiles")
    return arg_parser.parse_args(argv)[0]


def main(deploy, argv=None):
    """ Main function """
    options = get_options(argv)
    try:
        git_update(folder=DOTFILES, quiet=options.quiet)
        deploy(options)
    finally:
        # self-destruct
        # We wouldn't want to accidentally edit this script in a a 'system'
        # branch
        try:
            os.unlink(os.path.join(DOTFILES, 'dotfiles.py'))
        except OSError:
            pass
