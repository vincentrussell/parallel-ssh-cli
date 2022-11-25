# This file is part of parallel-ssh-cli.
#
# Copyright (C) 2022 Vincent Russell
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation, version 2.1.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

import optparse
import fnmatch
import sys
import os
import re
from .version import VERSION
from pssh.clients import ParallelSSHClient
from pssh.config import HostConfig
from pssh.exceptions import Timeout
from gevent import joinall
from termcolor import colored

_DEFAULT_PARALLELISM = 32
_DEFAULT_TIMEOUT = 0 # "infinity" by default


def read_host_files(paths, host_glob, default_user=None, default_port=None):
    """Reads the given host files.
    Returns a list of (host, port, user, proxy_host, proxy_port ) quintuple.
    """
    hosts = []
    if paths:
        for path in paths:
            hosts.extend(read_host_file(path, host_glob, default_user=default_user))
    return hosts

def read_host_file(path, host_glob, default_user=None, default_port=None):
    """Reads the given host file.
    Lines are of the form: [user@][proxyhost:]host[:port][:proxyport].
    Returns a list of (host, port, user, proxy_host, proxy_port ) quintuple.
    """
    lines = []
    f = open(path)
    for line in f:
        lines.append(line.strip())
    f.close()

    hosts = []
    for line in lines:
        # remove trailing comments
        line = re.sub('#.*', '', line)
        line = line.strip()
        # skip blank lines (or lines with only comments)
        if not line:
            continue
        host, port, user, proxy_host, proxy_port = parse_host_entry_line(line, default_user, default_port)
        if host and (not host_glob or fnmatch.fnmatch(host, host_glob)):
            hosts.append((host, port, user, proxy_host, proxy_port))
    return hosts

# [user@][proxyhost:]host[:port][:proxyport] format.
def parse_host_entry_line(line, default_user, default_port):
    """Parses a single host entry.
    This takes the of the form [user@][proxyhost:]host[:port][:proxyport]
    Returns a (host, port, user, proxy_host, proxy_port ) quintuple.
    """
    line_elements = line.split()
    if len(line_elements) > 2:
        sys.stderr.write('Bad line: "%s". Format should be'
                         ' [user@][proxyhost:]host[:port][:proxyport] [user]\n' % line)
        return None, None, None, None, None
    host_line_element = line_elements[0]
    host, port, user, proxy_host, proxy_port = parse_host_and_proxy_host(host_line_element, default_port=default_port)
    if len(line_elements) == 2:
        if user is None:
            user = line_elements[1]
        else:
            sys.stderr.write('User specified twice in line: "%s"\n' % line)
            return None, None, None, None, None
    if user is None:
        user = default_user
    return host, port, user, proxy_host, proxy_port


def parse_hosts_string(hosts_string, default_user=None, default_port=None):
    """Parses a whitespace-delimited string of "[user@][proxyhost:]host[:port][:proxyport]" entries.
    Returns a list of (host, port, user, proxy_host, proxy_port ) quintuples.
    """
    hosts = []
    entries = hosts_string.split()
    for entry in entries:
        hosts.append(parse_host_and_proxy_host(entry, default_user, default_port))
    return hosts


def parse_host_and_proxy_host(host_string, default_user=None, default_port=None):
    """Parses host entries of the form "[user@][proxyhost:]host[:port][:proxyport]".
    Returns a (host, port, user, proxy_host, proxy_port ) quintuple.
    """
    user = default_user
    port = default_port
    proxy_host = None
    proxy_port = default_port

    count = host_string.count(':')

    if count == 2:
        proxy_host, host_string, port = host_string.rsplit(':', 2)
        if '@' in proxy_host:
            user, proxy_host = proxy_host.split('@', 1)
        proxy_port = port
    elif count == 3:
        proxy_host, host_string, port, proxy_port = host_string.rsplit(':', 3)
        if '@' in proxy_host:
            user, proxy_host = proxy_host.split('@', 1)
        proxy_port = port
    else:
        if '@' in host_string:
            user, host_string = host_string.split('@', 1)
        if ':' in host_string:
            host_string, port = host_string.rsplit(':', 1)
    return (host_string, port, user, proxy_host, proxy_port)

def cli_parser():
    """
    Create a basic OptionParser with arguments common to all pssh programs.
    """
    # The "resolve" conflict handler avoids errors from the hosts option
    # conflicting with the help option.
    usage = "usage: %prog [options] command"
    parser = optparse.OptionParser(conflict_handler='resolve',
                                   version=str(VERSION), usage=usage)
    # Ensure that options appearing after the command are sent to ssh.
    parser.disable_interspersed_args()
    parser.epilog = "Example: parallel-ssh -h nodes.txt -l irb2 uptime"

    parser.add_option('-h', '--hosts', dest='host_files', action='append',
                      metavar='HOST_FILE',
                      help='hosts file (each line "[user@][proxyhost:]host[:port][:proxyport]")')
    parser.add_option('-H', '--host', dest='host_strings', action='append',
                      metavar='HOST_STRING',
                      help='additional host entries ("[user@][proxyhost:]host[:port][:proxyport]")')
    parser.add_option('-p', '--par', dest='par', type='int',
                      help='max number of parallel threads (OPTIONAL)')
    parser.add_option('-P', '--password', dest='password', type='string',
                      help='Password to use for login. Defaults to no password (Optional)')
    parser.add_option('-k', '--key', dest='pkey', type='string',
                      help='Private key file path or private key data to use. Paths must be str type and either absolute path or relative to user home directory like ~/. Bytes type input is used as private key data for authentication. (OPTIONAL)')
    parser.add_option('-l', '--user', dest='user',
                      help='username (OPTIONAL)')
    parser.add_option('-t', '--timeout', dest='timeout', type='int',
                      help='timeout (secs) (0 = no timeout) per host (OPTIONAL)')
    parser.add_option('-g', '--host-glob', dest='host_glob', type='string',
                      help='Shell-style glob to filter hosts (OPTIONAL)')
    parser.add_option("-s", "--sourceFile",
                      action="store", type="string", dest="sourceFile", help="source file (or directory) to parallel scp to remote hosts (OPTIONAL)")
    parser.add_option("-d", "--destinationFile",
                      action="store", type="string", dest="destinationFile", help="destination of file (or directory) that will be parallel scp'd to remote hosts (OPTIONAL)")
    parser.add_option("-r", "--recursiveCopy", action="store_true", dest="recursiveCopy", default=False, help="flag to indicate a recursive copy of the source diretory (like prsync) (OPTIONAL)")

    return parser

def main():
    (options, args) = cli_parser().parse_args()

    try:
        hosts_and_proxy_infos = read_host_files(options.host_files, options.host_glob,
                                         default_user=options.user)
    except IOError:
        _, e, _ = sys.exc_info()
        sys.stderr.write('Could not open hosts file: %s\n' % e.strerror)
        sys.exit(1)
    if options.host_strings:
        for s in options.host_strings:
            hosts_and_proxy_infos.extend(parse_hosts_string(s, default_user=options.user))

    #needed to get termcolor to work on windows
    if sys.platform.lower() == "win32":
        os.system('color')

    timeout = _DEFAULT_TIMEOUT
    par = _DEFAULT_PARALLELISM
    hostList = []
    hostConfigList = []
    for host_and_proxy_info in hosts_and_proxy_infos:
        host, port, user, proxy_host, proxy_port = host_and_proxy_info
        hostList.append(host)

        if port is not None:
            port = int(port)
        if proxy_port is not None:
            proxy_port = int(proxy_port)

        hostConfigList.append(HostConfig(proxy_host=proxy_host, proxy_port=proxy_port, port=port, proxy_user=user, user=user, timeout=timeout, proxy_password=options.password, password=options.password, private_key=options.pkey))

    if options.timeout is not None:
        timeout = options.timeout
    if options.par is not None:
        par = options.par

    errorDetected = False
    client = ParallelSSHClient(hostList, host_config=hostConfigList, pool_size=par, timeout=timeout, password=options.password, pkey=options.pkey)
    if options.sourceFile is not None and options.destinationFile is not None:
        cmds = client.copy_file(options.sourceFile, options.destinationFile, recurse=options.recursiveCopy)
        greenletList = joinall(cmds, raise_error=False)

        for greenlet in greenletList:
             if greenlet.exception is not None:
                 print(greenlet.exception)
                 errorDetected = True

    else:
        output = client.run_command(' '.join(args), stop_on_errors=False)
        for host_out in output:
            try:
                if host_out.stdout is None:
                    errorDetected = True
                    print(colored("[ERROR] ", "red") + host_out.host)
                else:
                    print(colored("[SUCCESS] ", "green") + host_out.host)
                if host_out.stdout is not None:
                    for line in host_out.stdout:
                        print(line)
                if host_out.stderr is not None:
                    for line in host_out.stderr:
                        print(line)
            except Timeout:
                pass

    if errorDetected == True:
        sys.exit(1)

if __name__ == "__main__":
    main()