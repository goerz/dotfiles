#!/usr/bin/env python
""" Utilitiy functions to deploy dotfiles """

import os
import sys
import shutil
from subprocess import call, STDOUT
from optparse import OptionParser


HOME          = os.environ['HOME']
DOTFILES      = os.path.split(os.path.realpath(__file__))[0]
DOT           = '.'


def make_link(src, dst, overwrite=False, quiet=False, uninstall=False):
    """ Create a symbolic link pointing to src named dst.

        src is a path relative to DOTFILES
        dst is a path relative to HOME

        If 'overwrite' is given as True and dst already exists, remove the
        existing file before creating the link.

        If 'uninstall' is True, don't create any symbolic links, but remove
        them if they exist.

        If the dst already exists and is a symbolic link to src, the routine
        will exit silently.

        For every newly created link, a message will be printed to screen,
        unless 'quiet' is given als False
    """
    abs_src = os.path.join(DOTFILES, src)
    abs_dst = os.path.join(HOME, dst)
    dst_path = os.path.split(abs_dst)[0]
    if overwrite:
        if os.path.isfile(abs_dst):
            os.unlink(abs_dst)
        if os.path.isfolder(abs_dst):
            shutil.rmtree(abs_dst)
    link_file   = abs_dst
    link_target = os.path.relpath(abs_src, dst_path)
    if uninstall:
        if (os.path.realpath(abs_dst) == abs_src):
            if not quiet:
                print "removing %s" % abs_dst
            os.unlink(abs_dst)
    else:
        if (os.path.realpath(abs_dst) != abs_src):
            try:
                if not quiet:
                    print "%s -> %s" % (link_file, abs_src)
                os.symlink(link_target, link_file)
            except OSError as msg:
                print "ERROR %s -> %s: %s" % (link_file, link_target, msg)
                raise


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
        deploy(options.overwrite, options.quiet, options.uninstall)
    except Exception as msg:
        print "ERROR: %s" % msg
