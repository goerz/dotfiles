#!/usr/bin/env python
""" Utilitiy functions to deploy dotfiles """

import os
import sys
import shutil
from glob import glob
from subprocess import call, STDOUT
from optparse import OptionParser


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
        remove them if they exist.

        If the dst already exists and is a symbolic link to src, the routine
        will exit silently.

        For every newly created link, a message will be printed to screen,
        unless options.quiet is given als False
    """
    abs_src = os.path.join(DOTFILES, src)
    abs_dst = os.path.join(HOME, dst)
    dst_path = os.path.split(abs_dst)[0]
    if options.overwrite:
        if os.path.isfile(abs_dst):
            os.unlink(abs_dst)
        if os.path.isdir(abs_dst):
            shutil.rmtree(abs_dst)
    link_file   = abs_dst
    link_target = os.path.relpath(abs_src, dst_path)
    if options.uninstall:
        if (os.path.realpath(abs_dst) == abs_src):
            if not options.quiet:
                print "removing %s" % abs_dst
            os.unlink(abs_dst)
    else:
        if (os.path.realpath(abs_dst) != abs_src):
            try:
                if not options.quiet:
                    print "%s -> %s" % (link_file, abs_src)
                os.symlink(link_target, link_file)
            except OSError as msg:
                print "ERROR %s -> %s: %s" % (link_file, link_target, msg)
                raise


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


def git_update(folder=DOTFILES, quiet=False):
    """ Perform an update of the repository in the given folder """
    git = which('git')
    stdout = None
    if quiet:
        stdout = open(os.devnull, 'w')
    if git is not None:
        os.chdir(folder)
        cmd = [git, 'remote', 'update', '-p']
        if not quiet:
            print "In %s" % folder, ": ", " ".join(cmd)
        ret = call(cmd, cwd=folder, stderr=STDOUT, stdout=stdout)
        if ret != 0:
            if not quiet:
                print "WARNING: git returned nonzero exist status (%s)"
        cmd = [git, 'merge', '--ff-only', '@{u}']
        if not quiet:
            print "In %s" % folder, ": ", " ".join(cmd)
        ret = call(cmd, cwd=folder, stderr=STDOUT, stdout=stdout)
        if ret != 0:
            if not quiet:
                print "WARNING: git returned nonzero exist status (%s)"
    else:
        if not quiet:
            print "WARNING: git is not available"


def run_duti(quiet=False):
    """ Run the duti utility, which sets up handlers for opening files on
        MacOS
    """
    duti = which('duti')
    if duti is not None:
        cmd = [duti, os.path.join(DOTFILES, "handlers.duti")]
        if not quiet:
            print " ".join(cmd)
        ret = call(cmd)
        if ret != 0:
            raise OSError("duti returned nonzero exist status (%s)" % ret)
    else:
        if not quiet:
            print "WARNING: duti is not available"


def main(deploy, argv=None):
    """ Main function """
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
    options, args = arg_parser.parse_args(argv)
    try:
        git_update(folder=DOTFILES, quiet=options.quiet)
        deploy(options)
    except Exception as msg:
        print "ERROR: %s" % msg
    finally:
        # self-destruct
        # We wouldn't want to accidentally edit this script in a a 'system'
        # branch
        try:
            os.unlink(os.path.join(DOTFILES, 'dotfiles.py'))
        except OSError:
            pass
