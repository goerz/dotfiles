""" Utilitiy functions to deploy dotfiles """
import os
import stat
import sys
import shutil
from fnmatch import fnmatch
import subprocess
from subprocess import call, STDOUT
from optparse import OptionParser

try:
    # Python 2
    from urllib import urlretrieve
except ImportError:
    # Python 3
    from urllib.request import urlretrieve
try:
    # make 'input' available in Python 2
    input = raw_input
except NameError:
    input = input

try:
    from subprocess import check_output

except ImportError:

    def check_output(*popenargs, **kwargs):
        """Run command with arguments and return its output as a byte string.
        Backported from Python 2.7"""
        process = subprocess.Popen(
            stdout=subprocess.PIPE, *popenargs, **kwargs
        )
        output = process.communicate()[0]
        retcode = process.poll()
        if retcode:
            cmd = kwargs.get("args")
            if cmd is None:
                cmd = popenargs[0]
            error = subprocess.CalledProcessError(retcode, cmd)
            error.output = output
            raise error
        return output


HOME = os.environ["HOME"]
DOTFILES = os.path.split(os.path.realpath(__file__))[0]


def is_file_or_link(file):
    return os.path.isfile(file) or os.path.islink(file)


def make_link(src, dst, options):
    """Create a symbolic link pointing to src named dst.

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
    global input
    abs_src = os.path.join(DOTFILES, src)
    abs_dst = os.path.join(HOME, dst)
    dst_path = os.path.split(abs_dst)[0]
    if options.overwrite and not options.uninstall:
        if is_file_or_link(abs_dst):
            os.unlink(abs_dst)
        elif os.path.isdir(abs_dst):
            if os.path.isdir(abs_src):
                shutil.rmtree(abs_dst)
            else:
                raise OSError(
                    "Existing directory %s " % abs_dst
                    + "would be overwritten by file %s" % abs_src
                )
    link_file = abs_dst
    link_target = os.path.relpath(abs_src, dst_path)
    if options.uninstall:
        if os.path.realpath(abs_dst) == os.path.realpath(abs_src):
            if not options.quiet:
                print("removing %s" % abs_dst)
            os.unlink(abs_dst)
            # remove empty folder
            try:
                folder = os.path.split(abs_dst)[0]
                while folder != "":
                    os.rmdir(folder)
                    folder = os.path.split(folder)[0]
            except OSError:
                pass  # folder is not empty
    else:
        if os.path.realpath(abs_dst) != os.path.realpath(abs_src):
            if not options.quiet:
                print("%s -> %s" % (link_file, abs_src))
            if is_file_or_link(dst_path) and not options.quiet:
                overwrite = input(
                    "%s already exists as a file. Overwrite with "
                    "an empty folder? yes/[no]: " % dst_path
                )
                if overwrite.lower().strip() == "yes":
                    os.unlink(dst_path)
            mkdir(dst_path)
            if is_file_or_link(link_file) and not options.quiet:
                overwrite = input(
                    "%s already exists. Overwrite? yes/[no]: " % link_file
                )
                if overwrite.lower().strip() == "yes":
                    os.unlink(link_file)
            os.symlink(link_target, link_file)


def change_extension(filename, new_ext):
    """Replace the extension in the given filename with new_ext"""
    root, ext = os.path.splitext(filename)
    if not new_ext.startswith("."):
        new_ext = "." + new_ext
    return root + new_ext


def make_links(
    folder,
    options,
    recursive=True,
    target=".",
    log_fh=None,
    ignore=(".DS_Store", "*~"),
):
    """For every file in the given `folder`, create a link inside the `target`.

    `folder` is the path of a folder, relative to DOTFILES.
    `target` is the path of a folder in which to create the links, relative to
             HOME
    `options` are passed to the `make_link` routine
    If `recursive` is True, links are also generated for all all subfolders of
    `folder`
    `ignore` is an iterable of filename patterns. Any file in `folder` matching
    a pattern in `ignore` is ignored.

    A list of all generated link destinations is written to the given `log_fh`.
    If `log_fh` is None, a new file DOTFILES/.{folder}.links will be opened and
    used for `log_fh`. If that file already exists, it will be overwritten; the
    original file will be copied to have the 'old_links' extension.
    """
    files = [
        os.path.join(DOTFILES, folder, file)
        for file in os.listdir(os.path.join(DOTFILES, folder))
    ]
    if log_fh is None:
        log_filename = os.path.join(
            DOTFILES, ".%s.links" % folder.replace("/", "_")
        )
        if os.path.isfile(log_filename):
            os.rename(
                log_filename, change_extension(log_filename, "old_links")
            )
        log_fh = open(log_filename, "w")
    for file in files:  # file is relative to CWD
        filename = os.path.basename(file)
        if any([fnmatch(filename, pat) for pat in ignore]):
            continue
        src = os.path.relpath(file, DOTFILES)
        dst = os.path.relpath(file, os.path.join(DOTFILES, folder))
        if target != ".":
            dst = os.path.join(target, dst)
        if os.path.isfile(file):
            make_link(src, dst, options)
            if not options.uninstall:
                log_fh.write("%s\n" % os.path.abspath(os.path.join(HOME, dst)))
        elif os.path.isdir(file):
            if recursive:
                make_links(src, options, recursive, dst, log_fh)
        else:
            raise AssertionError("%s is neither a file nor a folder" % file)


def which(program):
    """Return the absolute path of the given program, or None if the program is
    not available -- like Unix which utility)"""

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
    """Deploy vimrc from the given git repository.

    If ~/.vim does not exist already, the given repo will be cloned to
    ~/.vim, and a symlink ~/.vimrc -> ~/.vim/init.vim will be created, as
    well as a symlink $XDG_CONFIG_HOME/nvim -> ~/.vim (where
    $XDG_CONFIG_HOME defaults to ~/.config)

    If ~/.vim does exist and is a git repository, it will be updated to the
    latest revision.

    If options.overwrite is True, and ~/.vim/vimrc exists, any existing
    file ~/.vimrc will be removed and be replaced with a symlink to
    ~/.vim/init.vim. Likewise, $XDG_CONFIG_HOME/nvim will be replaced.

    The flag options.uninstall will only affect the file ~/.vimrc and the
    link $XDG_CONFIG_HOME/nvim; the .vim folder is never touched. This is
    so that spell check files, buffers, etc. don't get deleted accidentally
    """
    XDG_CONFIG_HOME = os.environ.get(
        "XDG_CONFIG_HOME", os.path.join(HOME, ".config")
    )
    vimdir = os.path.join(HOME, ".vim")
    vimrc = os.path.join(HOME, ".vimrc")
    vimrc_target = os.path.join(vimdir, "init.vim")
    nvimdir = os.path.join(XDG_CONFIG_HOME, "nvim")
    deploy_repo(repo, ".vim", options, allow_uninstall="no")
    # link for standard vim
    if os.path.isfile(vimrc_target):
        if options.overwrite:
            if is_file_or_link(vimrc):
                os.unlink(vimrc)
        make_link(
            os.path.abspath(vimrc_target), os.path.abspath(vimrc), options
        )
    else:
        if not options.uninstall and not options.quiet:
            print("WARNING: Cannot link to %s" % vimrc_target)
    # link for neovim
    if os.path.isdir(vimdir):
        mkdir(XDG_CONFIG_HOME)
        make_link(os.path.abspath(vimdir), os.path.abspath(nvimdir), options)
    else:
        if not options.uninstall and not options.quiet:
            print("WARNING: Cannot link to %s" % vimdir)


def deploy_neovim(neovim_repo, options, vim_repo=None):
    """Deploy neovim configuration from the given git repository.

    It is deployed to $XDG_CONFIG_HOME/nvim.

    If `vim_repo` is given, a vim configuration will be set up parallel to the
    neovim configuration. It is deployed to $XDG_CONFIG_HOME/nvim and linked to
    `~/.vim` and `~/.vimrc`. Legacy `vim` will automatically pick up this
    configuration. Also, `nvim` can pick up the vim-configuration by starting
    it as `NVIM_APPNAME=vim nvim`.

    If options.overwrite is True, and ~/.vim/vimrc exists, any existing
    file ~/.vimrc will be removed and be replaced with a symlink to
    ~/.vim/init.vim. Likewise, $XDG_CONFIG_HOME/nvim will be replaced.

    The flags options.overwrite and options.uninstall will only affect
    symlinks, but it will not delete the checkouts of the configuration repos.
    This is so that spell check files, buffers, etc. don't get deleted
    accidentally.
    """
    XDG_CONFIG_HOME = os.environ.get(
        "XDG_CONFIG_HOME", os.path.join(HOME, ".config")
    )
    nvimdir = os.path.join(XDG_CONFIG_HOME, "nvim")
    vimdir = os.path.join(XDG_CONFIG_HOME, "vim")
    vimdir_home = os.path.join(HOME, ".vim")
    vimrc = os.path.join(HOME, ".vimrc")
    vimrc_target = os.path.join(vimdir, "init.vim")
    if vim_repo is not None:
        deploy_repo(vim_repo, vimdir, options, allow_uninstall="no")
        # link ~/.vimrc (for legacy vim)
        if os.path.isfile(vimrc_target):
            if options.overwrite:
                if is_file_or_link(vimrc):
                    os.unlink(vimrc)
            make_link(
                os.path.abspath(vimrc_target), os.path.abspath(vimrc), options
            )
        else:
            if not options.uninstall and not options.quiet:
                print("WARNING: Cannot link to %s" % vimrc_target)
        # link ~/.vim (for legacy vim)
        if os.path.isdir(vimdir):
            if options.overwrite:
                if is_file_or_link(vimdir_home):
                    os.unlink(vimdir_home)
            make_link(
                os.path.abspath(vimdir), os.path.abspath(vimdir_home), options
            )
        else:
            if not options.uninstall and not options.quiet:
                print("WARNING: Cannot link to %s" % vimdir)
    deploy_repo(neovim_repo, nvimdir, options, allow_uninstall="no")


def check_remote_repo(repo, quiet=False):
    """Check that the given remote git repo is accessible. Returns a boolean.
    If `repo` is not accessible and `quiet` is False, print a warning."""
    stdout = open(os.devnull, "w")
    cmd = ["git", "ls-remote", repo]
    ret = call(cmd, stderr=STDOUT, stdout=stdout)
    if ret == 0:
        return True
    else:
        if not quiet:
            print(
                "WARNING: repo %s is not accessible. Check your "
                "authentication" % repo
            )
        return False


def deploy_repo(
    repo, destination, options, branch="master", allow_uninstall="clean"
):
    """Create a checkout of the given `repo` and `branch` at `destination`
    (relative to HOME), if `destination` does not exist yet.

    If `destination` exists (and `options.uninstall` is False), do one of the
    following:
    * If `destination` is a git checkout, update it.
    * If `destination` is not a git checkout, replace it with a checkout of
      `repo` if `options.overwrite` is True, otherwise print a warning and exit

    If `destination` exists, is a git checkout, and `options.uninstall` is
    True, do one of the following:
    * If `allow_uninstall` is 'clean', remove `destination` only if `git
      status` does not show any uncommited changes (otherwise print an error
      and exit)
    * If `allow_uninstall` is 'dirty', remove `destination` unconditionally
    * If `allow_uninstall` is 'no', do nothing
    """
    stdout = None
    if options.quiet:
        stdout = open(os.devnull, "w")
    create_checkout = True
    checkout_dir = os.path.join(HOME, destination)
    if os.path.exists(checkout_dir):
        create_checkout = False
        if options.uninstall:
            if os.path.exists(os.path.join(checkout_dir, ".git")):
                if allow_uninstall == "dirty":
                    shutil.rmtree(checkout_dir)
                elif allow_uninstall == "clean":
                    cmd = ["git", "status", "--porcelain"]
                    status = check_output(cmd, cwd=checkout_dir)
                    empty = status[0:0]  # `empty` of same type as `status`!
                    if status.strip() == empty:
                        shutil.rmtree(checkout_dir)
                    else:
                        print(
                            "ERROR: Cannot uninstall %s (not clean)"
                            % checkout_dir
                        )
                elif allow_uninstall == "no":
                    pass
                else:
                    raise ValueError(
                        "Invalid value %s for `allow_uninstall`"
                        % allow_uninstall
                    )
            else:
                print(
                    "WARNING: %s cannnot be uninstalled (not a git repo)"
                    % checkout_dir
                )
        else:  # update or overwrite
            if os.path.exists(os.path.join(checkout_dir, ".git")):
                git_update(checkout_dir, options.quiet)
            else:
                if options.overwrite:
                    shutil.rmtree(checkout_dir)
                    create_checkout = True
                else:
                    print(
                        "WARNING: %s already exists and will not be "
                        "overwritten without the --overwrite option"
                        % checkout_dir
                    )
    if create_checkout:
        if not check_remote_repo(repo, options.quiet):
            return
        cmd = ["git", "clone", repo, destination]
        if not options.quiet:
            print(" ".join(cmd))
        ret = call(cmd, cwd=HOME, stderr=STDOUT, stdout=stdout)
        if ret != 0:
            if not options.quiet:
                print("WARNING: git returned nonzero exist status (%s)")
        cmd = ["git", "checkout", branch]
        if not options.quiet:
            print(" ".join(cmd))
        ret = call(cmd, cwd=checkout_dir, stderr=STDOUT, stdout=stdout)
        if ret != 0:
            if not options.quiet:
                print("WARNING: git returned nonzero exist status (%s)")


def mkdir(directory):
    """Recursive mkdir

    If directory already exists, do nothing.
    If directory cannot be created, raise OSError.
    If parent directories do not exist, make them as well.
    """
    if os.path.isdir(directory):
        pass
    elif is_file_or_link(directory):
        raise OSError(
            "a file with the same name as the desired "
            "dir, '%s', already exists." % directory
        )
    else:
        head, tail = os.path.split(directory)
        if head and not os.path.isdir(head):
            mkdir(head)
        if tail:
            os.mkdir(directory)


def get(url, destination, options, make_exec=False):
    """Download the file at the given URL to destination (relative to HOME).

    If `make_exec` is True, also make it executable.

    If the file already exists, an `OSError` will be raised, unless
    `options.overwrite` is True.

    If `options.uninstall` is True, destination will be deleted if it exists.
    """
    destination = os.path.join(HOME, destination)
    mkdir(os.path.split(destination)[0])
    if is_file_or_link(destination):
        if options.overwrite or options.uninstall:
            if options.uninstall and not options.quiet:
                print("removing %s" % destination)
            os.unlink(destination)
            if options.uninstall:
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
        os.chmod(
            destination,
            perms.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH,
        )


def git_update(folder=DOTFILES, quiet=False):
    """Perform an update of the repository in the given folder"""
    git = which("git")
    stdout = None
    if quiet:
        stdout = open(os.devnull, "w")
    if git is not None:
        if not quiet:
            print("Updating %s" % folder)
        cmd = [git, "remote", "update", "-p"]
        ret = call(cmd, cwd=folder, stderr=STDOUT, stdout=stdout)
        if ret != 0:
            if not quiet:
                print("WARNING: git returned nonzero exist status (%s)")
        cmd = [git, "merge", "--ff-only", "@{u}"]
        ret = call(cmd, cwd=folder, stderr=STDOUT, stdout=stdout)
        if ret != 0:
            if not quiet:
                print("WARNING: git returned nonzero exist status (%s)")
    else:
        if not quiet:
            print("WARNING: git is not available")


def run_duti(quiet=False, handlers="handlers.duti"):
    """Run the duti utility, which sets up handlers for opening files on MacOS

    The path to the handlers file is relative to DOTFILES
    """
    duti = which("duti")
    if duti is not None:
        cmd = [duti, os.path.join(DOTFILES, handlers)]
        if not quiet:
            print(" ".join(cmd))
        ret = call(cmd)
        if ret != 0:
            raise OSError("duti returned nonzero exist status (%s)" % ret)
    else:
        if not quiet:
            print("WARNING: duti is not available")


def set_crontab(quiet=False, crontab_file="~/.crontab"):
    """Set the crontab to the given crontab_file"""
    crontab = which("crontab")
    crontab_file = os.path.expanduser(crontab_file)
    if crontab is not None:
        if os.path.isfile(crontab_file):
            cmd = [crontab, crontab_file]
        else:
            print("%s not found: deactivating crontab" % crontab_file)
            cmd = [crontab, "-r"]
        if not quiet:
            print(" ".join(cmd))
        ret = call(cmd)
        if os.path.isfile(crontab_file) and ret != 0:
            raise OSError("crontab returned nonzero exist status (%s)" % ret)


def get_options(argv=None):
    """Parse command line options. return options object"""
    if argv is None:
        argv = sys.argv
    arg_parser = OptionParser(usage="usage: %prog [options]")
    arg_parser.add_option(
        "--quiet",
        action="store_true",
        dest="quiet",
        default=False,
        help="Suppress all output",
    )
    arg_parser.add_option(
        "--overwrite",
        action="store_true",
        dest="overwrite",
        default=False,
        help="Overwrite link targets if they exist already",
    )
    arg_parser.add_option(
        "--uninstall",
        action="store_true",
        dest="uninstall",
        default=False,
        help="Remove any existing links to dotfiles",
    )
    return arg_parser.parse_args(argv)[0]


def main(deploy, argv=None):
    """Main function, executing `deploy` routine"""
    options = get_options(argv)
    try:
        git_update(folder=DOTFILES, quiet=options.quiet)
        deploy(options)
    finally:
        # self-destruct
        # We wouldn't want to accidentally edit this script in a a 'system'
        # branch
        try:
            os.unlink(os.path.join(DOTFILES, "dotfiles.py"))
        except OSError:
            pass
