#!/usr/bin/python
############################################################################
#    Copyright (C) 2009 by Michael Goerz                                   #
#    http://www.physik.fu-berlin.de/~goerz                                 #
#                                                                          #
#    This program is free software; you can redistribute it and/or modify  #
#    it under the terms of the GNU General Public License as published by  #
#    the Free Software Foundation; either version 3 of the License, or     #
#    (at your option) any later version.                                   #
#                                                                          #
#    This program is distributed in the hope that it will be useful,       #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of        #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         #
#    GNU General Public License for more details.                          #
#                                                                          #
#    You should have received a copy of the GNU General Public License     #
#    along with this program; if not, write to the                         #
#    Free Software Foundation, Inc.,                                       #
#    59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.             #
############################################################################
"""
This script shows an ascii-art graph of all git commits in the repository.
If the output is not redirected, it is shown in a pager.

The command is more or less  a wrapper around 'git log --graph', but with
better formatting of the refs and the option to show svn commit numbers, which
is useful for planning a svn merge.
"""
import os
import re
import sys
from optparse import OptionParser


BOLD = '\033[1m'
RED = '\033[31m'
BLUE = '\033[34m'
GREEN = '\033[32m'
ENDC = '\033[0m'


def get_refs():
    """
    Collect a dictionary of all the references in the repository
    """
    ref_for_hash = {}
    refs = os.popen('git show-ref', 'r', 0)
    pref = re.compile(r'^(?P<hash>[0-9a-f]+) refs/(?P<name>.*)')
    for line in refs:
        refmatch = pref.match(line)
        if refmatch:
            name = refmatch.group('name')
            if ref_for_hash.has_key(refmatch.group('hash')):
                ref_for_hash[refmatch.group('hash')].append(name)
            else:
                ref_for_hash[refmatch.group('hash')] = [name]
        else:
            print >> sys.stderr, ("Unexpected ref format")
            print >> sys.stderr, (line)
            return None
    return ref_for_hash


def turn_off_colors():
    """
    Disable all (global) color codes
    """
    global BOLD
    BOLD = ''
    global RED
    RED = ''
    global BLUE
    BLUE = ''
    global GREEN
    GREEN = ''
    global ENDC
    ENDC = ''


def format_commit_ref(commit_ref):
    """
    Format a commit reference

    Remote refs are prefixed with 'r:' and colored in blue.
    Local refs are colored in green.
    Unknown refs are colored in red.
    """
    if commit_ref.startswith('remotes/'):
        commit_ref = commit_ref.replace('remotes/', 'r:', 1)
        commit_ref = BOLD + BLUE + '[' + commit_ref + '] ' + ENDC
    elif commit_ref.startswith('heads/'):
        commit_ref = commit_ref.replace('heads/', '', 1)
        commit_ref = BOLD + GREEN + '[' + commit_ref + '] ' + ENDC
    else:
        commit_ref = BOLD + RED + '[' + commit_ref + '] ' + ENDC
    return commit_ref


def get_svn_revision(commit_hash):
    """ 
    For a given commit hash, get the svn revision number
    """
    commit_message = os.popen( "git log %s -n 1" % commit_hash)
    for line in commit_message:
        if 'git-svn-id' in line:
            match = re.search('@([0-9]+)', line)
            return "(R"+match.group(1)+")"
    return ''


def main(options=None):
    """
    Print a graph of all commits
    """
    if sys.stdout.isatty():
        pager = os.popen(options.pager, 'w')
    else:
        pager = sys.stdout
        if (not options.color):
            turn_off_colors()

    ref_for_hash = get_refs()
    if ref_for_hash is None: return 1

    pgraph1 = re.compile(
        r'^(?P<graph>[\s\\/\*|]+)(?P<longhash>[0-9a-f]+) '
        +r'(?P<hash>[0-9a-f]+) : (?P<info>.*)$')
    pgraph2 = re.compile(
        r'^(?P<graph>[\s\\/\*|]+) (?P<message>.*)$')
    pgraph3 = re.compile(
        r'^(?P<graph>[\s\\/\*|]+)$')

    if options.oneline:
        graph = os.popen(
            "git log --all --date=%s " % options.date +
            "--pretty=format:'%H %h : %an %ad -- %s' "+
            "--graph", 'r', 0)
    else:
        graph = os.popen(
            "git log --all --date=%s " % options.date +
            "--pretty=format:'%H %h : %an %ad %n %s%n' "+
            "--graph", 'r', 0)

    if options.no_color: turn_off_colors()

    for line in graph:

        commit_graph = ''
        commit_hash = ''
        commit_ref = ''
        commit_info = ''

        handled = False

        if not handled:
            graphmatch = pgraph1.match(line)
            if graphmatch:
                handled = True
                commit_graph = graphmatch.group('graph')
                if options.svn:
                    commit_hash = get_svn_revision(graphmatch.group('hash'))
                    commit_hash += " "
                if not options.no_hash:
                    commit_hash  += graphmatch.group('hash')
                    commit_hash += " "
                if len(commit_hash) > 0:
                    commit_hash += ": "
                commit_info  = graphmatch.group('info')
                longhash = graphmatch.group('longhash')
                if ref_for_hash.has_key(longhash):
                    commit_refs = [format_commit_ref(commit_ref) for commit_ref 
                                  in ref_for_hash[graphmatch.group('longhash')]]
                    commit_ref = "".join(commit_refs)

        if not handled:
            graphmatch = pgraph2.match(line)
            if graphmatch:
                handled = True
                commit_graph = graphmatch.group('graph')
                commit_info  = graphmatch.group('message')

        if not handled:
            graphmatch = pgraph3.match(line)
            if graphmatch:
                handled = True
                commit_graph = line.rstrip()

        if not handled:
            print >> sys.stderr, ("Unexpected graph format")
            print >> sys.stderr, (line)
            return 1

        line = "%s%s%s%s" % (commit_graph, commit_hash, commit_ref, commit_info)
        if ((options.max_length > 0) and (len(line) > options.max_length)):
            line = line[:options.max_length]
        print >> pager, (line)

    return 0


if __name__ == "__main__":
    arg_parser = OptionParser(usage = "git_graph.py [options] [path] ",
                              description = __doc__)

    arg_parser.add_option('--no-hash', action='store_true', dest='no_hash',
                        default=False, help="Don't print the commit hash")
    arg_parser.add_option('--no-color', action='store_true', dest='no_color',
                        default=False, help="Don't mark refs with color")
    arg_parser.add_option('--color', action='store_true', dest='color',
                        default=False, help="Mark refs with color even if "
                        "output is redirected")
    arg_parser.add_option('--oneline', action='store_true', dest='oneline',
                        default=False, help="Print only one line per commit")
    arg_parser.add_option('--svn', action='store_true', dest='svn',
                        default=False, help="Print svn revision number")
    arg_parser.add_option('--pager', action='store', dest='pager', 
                          default='less -RS', help="Set pager "
                          "(default: less -RS)")
    arg_parser.add_option('--date', action='store', dest='date', 
                          default='short',
                          help="Set date format. Possible values are "
                          "'relative', 'local', 'iso', 'fc', "
                          "'short' (default), 'raw', "
                          "'default'. For an explanation, see 'git help log'")
    arg_parser.add_option('--max-length', action='store', type=int,
                          dest='max_length', default=0,
                          help="Set maximum line length")

    options, args = arg_parser.parse_args(sys.argv)
    if len(args) > 1:
        os.chdir(args[1])

    try:
        sys.exit(main(options))
    except IOError:
        pass
