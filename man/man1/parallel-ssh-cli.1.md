---
title: parallel-ssh-cli
section: 1
header: User Manual
footer: parallel-ssh-cli 1.0.0
date: November 26, 2022
---
# NAME
parallel-ssh-cli - A wrapper arround parallel-ssh.  See: https://parallel-ssh.readthedocs.io/en/latest/

# SYNOPSIS
**parallel-ssh-cli** [*OPTIONS*] [ COMMANDS... ]

# DESCRIPTION
**parallel-ssh-cli** A wrapper arround parallel-ssh written in python.

# OPTIONS
**--version** 
: show program's version number and exit

**--help** 
: show this help message and exit

**-h, --hosts** 
: hosts file (each line "[user@][proxyhost:]host[:port][:proxyport]")

**-H, --host** 
: additional host entries ("[user@][proxyhost:]host[:port][:proxyport]")

**-p, --par** 
: max number of parallel threads (OPTIONAL)

**-P, --password** 
: Password to use for login. Defaults to no password (Optional)

**-k, --key** 
: Private key file path or private key data to use. Paths must be str type and either absolute path or relative to user home directory like ~/. Bytes type input is used as private key data for authentication. (OPTIONAL)

**-l, --user** 
: username (OPTIONAL)

**-t, --timeout** 
: timeout (secs) (0 = no timeout) per host (OPTIONAL)

**-g, --host-glob** 
: Shell-style glob to filter hosts (OPTIONAL)

**-s, --sourceFile** 
: source file (or directory) to parallel scp to remote hosts (OPTIONAL)

**-d, --destinationFile** 
: destination of file (or directory) that will be parallel scp'd to remote hosts (OPTIONAL)

**-r, --recursiveCopy** 
: flag to indicate a recursive copy of the source diretory (like prsync) (OPTIONAL)