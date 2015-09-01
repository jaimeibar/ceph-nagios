#!/usr/bin/env python
#
#  Copyright (c) 2013 SWITCH http://www.switch.ch
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

"""
Ceph nagios plugins
"""


import argparse
import os
import subprocess
import sys

__version__ = '1.0.1'

# default ceph values
CEPH_COMMAND = '/usr/bin/ceph'
CEPH_CONFIG = '/etc/ceph/ceph.conf'

# nagios exit code
STATUS_OK = 0
STATUS_WARNING = 1
STATUS_ERROR = 2
STATUS_UNKNOWN = 3


def _parse_arguments():
    """
    Parse arguments
    """
    parser = argparse.ArgumentParser(description="'ceph health' nagios plugin.")
    parser.add_argument('-e', '--exe', help='ceph executable [%s]' % CEPH_COMMAND)
    parser.add_argument('-c', '--conf', help='alternative ceph conf file [{0}]'.format(CEPH_CONFIG))
    parser.add_argument('-m', '--monaddress', help='ceph monitor address[:port]')
    parser.add_argument('-i', '--id', help='ceph client id')
    parser.add_argument('-n', '--name', help='ceph client name')
    parser.add_argument('-k', '--keyring', help='ceph client keyring file')
    parser.add_argument('-v', '--version', action='version', version=__version__, help='show version and exit')

    ceph = parser.add_mutually_exclusive_group()
    ceph.add_argument('--status', action='store_true', help='Show ceph status')
    ceph.add_argument('--health', action='store_true', help='Show ceph health')

    return parser

def compose_command(arguments):
    """
    :param arguments: Command line arguments
    :return: Ceph command or False in case of missing params
    """
    cmd = list()
    cephcmd = arguments.exe if arguments.exe is not None else CEPH_COMMAND
    altconf = arguments.conf if arguments.conf is not None else CEPH_CONFIG
    monaddress = arguments.monaddress
    clientid = arguments.id
    clientname = arguments.name
    keyring = arguments.keyring
    status = arguments.status
    health = arguments.health
    if not status and not health:
        return False
    if check_file_exist(cephcmd):
        cmd.append(cephcmd)
    if check_file_exist(altconf):
        cmd.append('-c')
        cmd.append(altconf)
    if monaddress is not None:
        cmd.append('-m')
        cmd.append(monaddress)
    if clientid is not None:
        cmd.append('--id')
        cmd.append(clientid)
    if clientname is not None:
        cmd.append('--name')
        cmd.append(clientname)
    if keyring is not None:
        cmd.append('--keyring')
        cmd.append(keyring)
    extra = 'status' if status else 'health'
    cmd.append(extra)
    return cmd

def check_file_exist(cfile):
    """
    Check if file exists
    :param cfile
    :return: True if it exists STATUS_ERROR otherwise
    """
    if not os.path.exists(cfile):
        print >> sys.stderr, 'No such file'
        return STATUS_ERROR
    else:
        return True

"""
    # validate args
    ceph_exec = args.exe if args.exe else CEPH_COMMAND
    if not os.path.exists(ceph_exec):
        print "ERROR: ceph executable '%s' doesn't exist" % ceph_exec
        return STATUS_UNKNOWN

    if args.conf and not os.path.exists(args.conf):
        print "ERROR: ceph conf file '%s' doesn't exist" % args.conf
        return STATUS_UNKNOWN

    if args.keyring and not os.path.exists(args.keyring):
        print "ERROR: keyring file '%s' doesn't exist" % args.keyring
        return STATUS_UNKNOWN

    # build command
    ceph_health = [ceph_exec]
    if args.monaddress:
        ceph_health.append('-m')
        ceph_health.append(args.monaddress)
    if args.conf:
        ceph_health.append('-c')
        ceph_health.append(args.conf)
    if args.id:
        ceph_health.append('--id')
        ceph_health.append(args.id)
    if args.name:
        ceph_health.append('--name')
        ceph_health.append(args.name)
    if args.keyring:
        ceph_health.append('--keyring')
        ceph_health.append(args.keyring)
    ceph_health.append('health')

    # exec command
    p = subprocess.Popen(ceph_health, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, err = p.communicate()

    if output:
        # merge multi-lines of output in one line
        one_line = output.replace('\n', '; ')
        if one_line.startswith('HEALTH_OK'):
            #print 'HEALTH OK:', one_line[len('HEALTH_OK')+1:]
            one_line = one_line[len('HEALTH_OK') + 1:].strip()
            if one_line:
                print 'HEALTH OK:', one_line
            else:
                print 'HEALTH OK'
            return STATUS_OK
        elif one_line.startswith('HEALTH_WARN'):
            print 'HEALTH WARNING:', one_line[len('HEALTH_WARN') + 1:]
            return STATUS_WARNING
        elif one_line.startswith('HEALTH_ERR'):
            print 'HEALTH ERROR:', one_line[len('HEALTH_ERR') + 1:]
            return STATUS_ERROR
        else:
            print one_line

    elif err:
        # read only first line of error
        one_line = err.split('\n')[0]
        if '-1 ' in one_line:
            idx = one_line.rfind('-1 ')
            print 'ERROR: %s: %s' % (ceph_exec, one_line[idx + len('-1 '):])
        else:
            print one_line

    return STATUS_UNKNOWN
"""

def main():
    """
    Main function
    """
    parser = _parse_arguments()
    nargs = len(sys.argv[1:])
    if not nargs:
        parser.print_help()
        return STATUS_ERROR
    arguments = parser.parse_args()
    command = compose_command(arguments)
    if not command:
        parser.error('Missing mandatory argument --status or --health')




if __name__ == "__main__":
    sys.exit(main())
