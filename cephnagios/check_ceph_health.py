#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Distributed under GNU/GPL 2 license

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see http://www.gnu.org/licenses/


"""
Ceph nagios plugins
"""

import os
import subprocess
import argparse
import sys
import json

# nagios exit code
STATUS_OK = 0
STATUS_WARNING = 1
STATUS_ERROR = 2
STATUS_UNKNOWN = 3

# default ceph values
CEPH_COMMAND = '/usr/bin/ceph'
CEPH_CONFIG = '/etc/ceph/ceph.conf'

__version__ = '0.5.1'


class CephCommandBase:
    """
    Base class
    """
    def __init__(self, cliargs):
        self._cephexec = getattr(cliargs, 'exe')
        self._cephconf = getattr(cliargs, 'conf')
        self._monaddress = getattr(cliargs, 'monaddress')
        self._clientid = getattr(cliargs, 'clientid')
        self._name = getattr(cliargs, 'name')
        self._keyring = getattr(cliargs, 'keyring')
        self._nagiosmessage = ''

    @property
    def cephexec(self):
        """
        Get ceph executable
        :return: ceph executable
        """
        return self._cephexec

    @property
    def cephconf(self):
        """
        Get ceph config file
        :return: ceph config file
        """
        return self._cephconf

    @property
    def monaddress(self):
        """
        Get mon address
        :return: mon address
        """
        return self._monaddress

    @property
    def clientid(self):
        """
        Get mon id
        :return: Mon id
        """
        return self._clientid

    @property
    def name(self):
        """
        Get client name for authentication
        :return: Client name
        """
        return self._name

    @property
    def keyring(self):
        """
        Get keyring
        :return: Keyring
        """
        return self._keyring

    @property
    def nagiosmessage(self):
        """
        Get nagios message
        :return: nagios message
        """
        return self._nagiosmessage

    @nagiosmessage.setter
    def nagiosmessage(self, newmessage):
        """
        Set new nagios message
        :param newmessage: New nagios message
        """
        self._nagiosmessage = newmessage

    def build_base_command(self):
        """
        Build base ceph command from common command line arguments
        :return: Ceph base command
        """
        basecmd = list()
        basecmd.append(self.cephexec)
        if self.cephconf is not None:
            if not os.path.exists(self.cephconf):
                self._nagiosmessage = 'ERROR: No such file - {0}'.format(self.cephconf)
                return False
            basecmd.extend('-c {0}'.format(self.cephconf).split())
        if self.monaddress is not None:
            basecmd.extend('-m {0}'.format(self.monaddress).split())
        if self.clientid is not None:
            basecmd.extend('--id {0}'.format(self.clientid).split())
        if self.name is not None:
            basecmd.extend('--name {0}'.format(self.name).split())
        if self.keyring is not None:
            basecmd.extend('--keyring {0}'.format(self.keyring).split())
        return basecmd

    def run_ceph_command(self, command):
        """
        Run ceph command
        :param command: Ceph command
        :return: Ceph command output
        """
        try:
            runcmd = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=True)
            rescmd = runcmd.stdout.decode()
        except OSError:
            print('ERROR: Ceph executable not found - {0}'.format(self.cephexec))
            sys.exit(STATUS_ERROR)
        except subprocess.CalledProcessError as error:
            print('ERROR running ceph command: {0}'.format(error.output.decode()))
            print('Ceph command: {0}'.format(command))
            sys.exit(STATUS_ERROR)
        return rescmd

    def __str__(self):
        return '{0}'.format(self.nagiosmessage)


class CommonCephCommand(CephCommandBase):
    """
    Class for common command
    """
    def __init__(self, cliargs):
        self._status = getattr(cliargs, 'status')
        self._health = getattr(cliargs, 'health')
        self._quorum = getattr(cliargs, 'quorum')
        self._df = getattr(cliargs, 'df')
        super(CommonCephCommand, self).__init__(cliargs)

    @property
    def status(self):
        """
        :return: True if status is defined False otherwise
        """
        return self._status

    @property
    def health(self):
        """
        :return: True if health is defined False otherwise
        """
        return self._health

    @property
    def quorum(self):
        """
        :return: True if quorum is defined False otherwise
        """
        return self._quorum

    @property
    def dfcmd(self):
        """
        :return: True if df is defined False otherwise
        """
        return self._df

    def build_common_command(self):
        """
        :return: Ceph common command
        """
        cmd = self.build_base_command()
        if not cmd:
            return False
        if self.status:
            cmd.append('status')
        elif self.health:
            cmd.append('health')
        elif self.quorum:
            cmd.append('quorum_status')
        else:
            cmd.append('df')
        return cmd


class MonCephCommand(CephCommandBase):
    """
    Class for mon command
    """

    def __init__(self, cliargs):
        self._monhealth = getattr(cliargs, 'monid')
        self._monstatus = getattr(cliargs, 'monstatus')
        self._monstat = getattr(cliargs, 'monstat')
        super(MonCephCommand, self).__init__(cliargs)

    @property
    def monhealth(self):
        """
        Get monhealth value
        :return: monhealth value
        """
        return self._monhealth

    @property
    def monstatus(self):
        """
        :return: True if monstatus is defined False otherwise
        """
        return self._monstatus

    @property
    def monstat(self):
        """
        :return: True if monstat is defined False otherwise
        """
        return self._monstat

    def build_mon_command(self):
        """
        :return: Ceph mon command
        """
        cmd = self.build_base_command()
        if self.monhealth:
            cmd.extend('ping mon.{0}'.format(self.monhealth).split())
        elif self.monstatus:
            cmd.append('mon_status')
        elif self.monstat:
            cmd.extend('mon stat'.split())
        return cmd


class OsdCephCommand(CephCommandBase):
    """
    Class for osd command
    """

    def __init__(self, cliargs):
        self._osdstat = getattr(cliargs, 'stat')
        self._osdtree = getattr(cliargs, 'tree')
        super(OsdCephCommand, self).__init__(cliargs)

    @property
    def osdstat(self):
        """
        :return: True if osdstat is defined False otherwise
        """
        return self._osdstat

    @property
    def osdtree(self):
        """
        :return: True if osdtree is defined False otherwise
        """
        return self._osdtree

    def build_osd_command(self):
        """
        :return: Ceph osd command
        """
        cmd = self.build_base_command()
        cmd.append('osd')
        if self.osdstat:
            cmd.append('stat')
        else:
            cmd.append('tree')
        return cmd


class MdsCephCommand(CephCommandBase):
    """
    Class for mds command
    """

    def __init__(self, cliargs):
        self._mdsstat = getattr(cliargs, 'mdsstat')
        super(MdsCephCommand, self).__init__(cliargs)

    @property
    def mdsstat(self):
        """
        :return: True if mdsstat is defined False otherwise
        """
        return self._mdsstat

    def build_mds_command(self):
        """
        :return: Ceph mds command
        """
        cmd = self.build_base_command()
        cmd.extend('mds stat'.split())
        return cmd


def _parse_arguments():
    """
    Parse command line arguments
    :return: Command line arguments
    """
    parser = argparse.ArgumentParser(description='ceph nagios plugin')
    parser.add_argument('-e', '--exe', default=CEPH_COMMAND, help='ceph executable [{0}]'.format(CEPH_COMMAND))
    parser.add_argument('-c', '--conf', default=CEPH_CONFIG, help='alternative ceph conf file [{0}]'.format(CEPH_CONFIG))
    parser.add_argument('-m', '--monaddress', help='ceph monitor address[:port]')
    parser.add_argument('-i', '--user', dest='clientid', help='ceph client id')
    parser.add_argument('-n', '--name', help='ceph client name')
    parser.add_argument('-k', '--keyring', help='ceph client keyring file')
    parser.add_argument('--version', action='version', version='%(prog)s {0}'.format(__version__))

    subparsers = parser.add_subparsers(help='Ceph commands options help')

    cephcommonparser = subparsers.add_parser('common', help='Ceph common options')
    cephcommonparsergrp = cephcommonparser.add_mutually_exclusive_group()
    cephcommonparsergrp.add_argument('--status', action='store_true', help='Show ceph status')
    cephcommonparsergrp.add_argument('--health', action='store_true', help='Show ceph health')
    cephcommonparsergrp.add_argument('--quorum', action='store_true', help='Show ceph quorum')
    cephcommonparsergrp.add_argument('--df', action='store_true', help='Show ceph pools status')

    cephmonparser = subparsers.add_parser('mon', help='Ceph monitor options')
    cephmonparsergrp = cephmonparser.add_mutually_exclusive_group()
    cephmonparsergrp.add_argument('--monhealth', dest='monid', help='Check mon health status')
    cephmonparsergrp.add_argument('--monstatus', action='store_true', help='Show ceph mon status')
    cephmonparsergrp.add_argument('--monstat', action='store_true', help='Show Ceph mon stat')

    cephosdparser = subparsers.add_parser('osd', help='Ceph osd options')
    cephosdparsergrp = cephosdparser.add_mutually_exclusive_group()
    cephosdparsergrp.add_argument('--stat', action='store_true', help='Show ceph osd status')
    cephosdparsergrp.add_argument('--tree', action='store_true', help='Show Ceph osd tree')

    cephmdsparser = subparsers.add_parser('mds', help='Ceph mds options')
    cephmdsparsergrp = cephmdsparser.add_mutually_exclusive_group()
    cephmdsparsergrp.add_argument('--mdsstat', action='store_true', help='Show ceph mds status')

    return parser


def compose_nagios_output(output, cliargs):
    """
    Compose nagios message from ceph command output
    :param output: Ceph command result
    :param cliargs: Command line args
    :return: Nagios code
    """
    monid = getattr(cliargs, 'monid', None)
    if monid is not None:
        try:
            jsondata = json.loads(output)
        except ValueError:
            if output.find('ObjectNotFound') != -1:
                nagiosmessage = '{0} is not a valid ceph mon'.format(monid)
                return nagiosmessage, STATUS_ERROR
            else:
                nagiosmessage = 'Unknown error'
                return nagiosmessage, STATUS_UNKNOWN
        healthstatus = jsondata['health']['status']
        if healthstatus:
            _, health = healthstatus.split('_')
            nagiosmessage = healthstatus
            nagioscode = STATUS_OK
            if health == 'WARNING':
                nagioscode = STATUS_WARNING
            elif health == 'ERROR':
                nagioscode = STATUS_ERROR
            elif health == 'UNKNOWN':
                nagioscode = STATUS_UNKNOWN
        else:
            nagiosmessage = 'No mons found'
            nagioscode = STATUS_ERROR
    else:
        if output.find('HEALTH_OK') != -1:
            nagiosmessage = output
            nagioscode = STATUS_OK
        elif output.find('HEALTH_WARN') != -1:
            nagiosmessage = output
            nagioscode = STATUS_WARNING
        elif output.find('HEALTH_ERR') != -1:
            nagiosmessage = output
            nagioscode = STATUS_ERROR
        else:
            nagiosmessage = 'OK: {0}'.format(output)
            nagioscode = STATUS_OK
    return nagiosmessage, nagioscode


def main():
    """
    Main function
    :return: Nagios status code
    """
    parser = _parse_arguments()
    nargs = len(sys.argv[1:])
    if not nargs:
        parser.print_help()
        return STATUS_ERROR
    arguments = parser.parse_args()
    if hasattr(arguments, 'status'):
        # Common command
        ccmd = CommonCephCommand(arguments)
        cephcmd = ccmd.build_common_command()
    elif hasattr(arguments, 'monstatus'):
        # Mon command
        ccmd = MonCephCommand(arguments)
        cephcmd = ccmd.build_mon_command()
    elif hasattr(arguments, 'stat'):
        # Osd command
        ccmd = OsdCephCommand(arguments)
        cephcmd = ccmd.build_osd_command()
    elif hasattr(arguments, 'mdsstat'):
        # Mds command
        ccmd = MdsCephCommand(arguments)
        cephcmd = ccmd.build_mds_command()
    else:
        print('No valid command found')
        return STATUS_ERROR
    if not cephcmd:
        print(ccmd.nagiosmessage, file=sys.stderr)
        return STATUS_ERROR
    result = ccmd.run_ceph_command(cephcmd)
    if result:
        nagiosmsg, nagioscode = compose_nagios_output(result, arguments)
        print(nagiosmsg)
    return nagioscode


if __name__ == "__main__":
    sys.exit(main())
