#!/usr/bin/env python
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

from __future__ import print_function
import argparse
import os
import subprocess
import sys

__version__ = '0.2'

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
    Parse command line arguments
    :return: Command line arguments
    """
    parser = argparse.ArgumentParser(description="'ceph health' nagios plugin.")
    parser.add_argument('-e', '--exe', help='ceph executable [{0}]'.format(CEPH_COMMAND))
    parser.add_argument('-c', '--conf', help='alternative ceph conf file [{0}]'.format(CEPH_CONFIG))
    parser.add_argument('-m', '--monaddress', help='ceph monitor address[:port]')
    parser.add_argument('-i', '--monid', help='ceph client id')
    parser.add_argument('-n', '--name', help='ceph client name')
    parser.add_argument('-k', '--keyring', help='ceph client keyring file')
    parser.add_argument('-v', '--version', action='version', version=__version__, help='show version and exit')

    subparsers = parser.add_subparsers(help='Ceph commands options help')

    cephcommonparser = subparsers.add_parser('common', help='Ceph common options')
    cephcommonparsergrp = cephcommonparser.add_mutually_exclusive_group()
    cephcommonparsergrp.add_argument('--status', action='store_true', help='Show ceph status')
    cephcommonparsergrp.add_argument('--health', action='store_true', help='Show ceph health')
    cephcommonparsergrp.add_argument('--quorum', action='store_true', help='Show ceph quorum')
    cephcommonparsergrp.add_argument('--df', action='store_true', help='Show ceph pools status')

    cephmonparser = subparsers.add_parser('mon', help='Ceph monitor options')
    cephmonparsergrp = cephmonparser.add_mutually_exclusive_group()
    cephmonparsergrp.add_argument('--mon', action='store_true', help='Show ceph mon status')
    cephmonparsergrp.add_argument('--monstat', action='store_true', help='Show Ceph mon stat')

    cephosdparser = subparsers.add_parser('osd', help='Ceph osd options')
    cephosdparsergrp = cephosdparser.add_mutually_exclusive_group()
    cephosdparsergrp.add_argument('--osdstat', action='store_true', help='Show ceph osd status')
    cephosdparsergrp.add_argument('--osdtree', action='store_true', help='Show Ceph osd tree')

    cephmdsparser = subparsers.add_parser('mds', help='Ceph mds options')
    cephmdsparsergrp = cephmdsparser.add_mutually_exclusive_group()
    cephmdsparsergrp.add_argument('--mdsstat', action='store_true', help='Show ceph mds status')

    return parser


class CephCommandBase(object):
    """
    Base class
    """
    def __init__(self, cliargs):
        self._cephexec = getattr(cliargs, 'exe')
        self._cephconf = getattr(cliargs, 'conf')
        self._monaddress = getattr(cliargs, 'monaddress')
        self._monid = getattr(cliargs, 'monid')
        self._name = getattr(cliargs, 'name')
        self._keyring = getattr(cliargs, 'keyring')

    @property
    def cephexec(self):
        """
        Get ceph executable
        :return: ceph executable
        """
        return self._cephexec or CEPH_COMMAND

    @cephexec.setter
    def cephexec(self, newcephexec):
        """
        Set new ceph executable
        :param newcephexec: New ceph executable
        """
        self._cephexec = newcephexec

    @property
    def cephconf(self):
        """
        Get ceph config file
        :return: ceph config file
        """
        return self._cephconf or CEPH_CONFIG

    @cephconf.setter
    def cephconf(self, newcephconf):
        """
        Set new ceph config file
        :param newcephconf: New ceph config file
        """
        self._cephconf = newcephconf

    @property
    def monaddress(self):
        """
        Get mon address
        :return: mon address
        """
        return self._monaddress

    @monaddress.setter
    def monaddress(self, newmonaddress):
        """
        Set new mon address
        :param newmonaddress: New mon address
        """
        self._monaddress = newmonaddress

    @property
    def monid(self):
        """
        Get mon id
        :return: Mon id
        """
        return self._monid

    @monid.setter
    def monid(self, newmonid):
        """
        Set new mon id
        :param newmonid: New mon id
        """
        self._monid = newmonid

    @property
    def name(self):
        """
        Get client name for authentication
        :return: Client name
        """
        # TODO-jim: Improve this doc
        return self._name

    @name.setter
    def name(self, newname):
        """
        Set new client name for authentication
        :param newname: New client name
        """
        self._name = newname

    @property
    def keyring(self):
        """
        Get keyring
        :return: Keyring
        """
        return self._keyring

    @keyring.setter
    def keyring(self, newkeyring):
        """
        Set new keyring
        :param newkeyring: New keyring
        """
        self._keyring = newkeyring

    def build_base_command(self):
        """
        Build base ceph command from common command line arguments
        :return: Ceph command
        """
        basecmd = list()
        basecmd.append(self.cephexec)
        if self.cephconf is not None:
            basecmd.append('-c')
            basecmd.append(self.cephconf)
        if self.monaddress is not None:
            basecmd.append('-m')
            basecmd.append(self.monaddress)
        if self.monid is not None:
            basecmd.append('--id')
            basecmd.append(self.monid)
        if self.name is not None:
            basecmd.append('--name')
            basecmd.append(self.name)
        if self.keyring is not None:
            basecmd.append('--keyring')
            basecmd.append(self.keyring)
        return basecmd

    def run_ceph_command(self, command):
        """
        Run ceph command
        :param command: Ceph command
        :return: Nagios status code
        """
        try:
            runcmd = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
            output, err = runcmd.communicate()
        except OSError as error:
            print('ERROR: {0} - {1}'.format(error.strerror, self.cephexec), file=sys.stderr)
            nagioscode = STATUS_ERROR
        if output:
            if output.find('HEALTH_OK') != -1:
                print('HEALTH_OK: {0}'.format(output.strip()))
                nagioscode = STATUS_OK
            elif output.find('HEALTH_WARN') != -1:
                print('HEALTH_WARN: {0}'.format(output.strip()), file=sys.stderr)
                nagioscode = STATUS_WARNING
            elif output.find('HEALTH_ERR') != -1:
                print('HEALTH_ERROR: {0}'.format(output.strip()), file=sys.stderr)
                nagioscode = STATUS_ERROR
            else:
                if not os.path.exists(self.cephconf):
                    print('ERROR: No such file - {0}'.format(self.cephconf), file=sys.stderr)
                    nagioscode = STATUS_ERROR
                else:
                    print('UNKNOWN: {0}'.format(output.strip()), file=sys.stderr)
                    nagioscode = STATUS_UNKNOWN
        elif err:
            print('ERROR: {0}'.format(err.strip()), file=sys.stderr)
            nagioscode = STATUS_ERROR

        return nagioscode


class CommonCephCommand(CephCommandBase):

    def __init__(self, cliargs):
        self._status = getattr(cliargs, 'status')
        self._health = getattr(cliargs, 'health')
        self._quorum = getattr(cliargs, 'quorum')
        self._df = getattr(cliargs, 'df')
        super(CommonCephCommand, self).__init__(cliargs)

    @property
    def status(self):
        return self._status

    @property
    def health(self):
        return self._health

    @property
    def quorum(self):
        return self._quorum

    @property
    def dfcmd(self):
        return self._df

    def build_common_command(self):
        cmd = self.build_base_command()
        if self.status:
            cmd.append('status')
        elif self.health:
            cmd.append('health')
        elif self.quorum:
            cmd.append('quorum_status')
        else:
            cmd.append('df')
        return cmd

    def __str__(self):
        return '{0}'.format(self.build_common_command())


class MonCephCommand(CephCommandBase):

    def __init__(self, cmd, **kwargs):
        self._cmd = cmd
        self._mon = kwargs.get('mon')
        self._monstat = kwargs.get('monstat')
        super(MonCephCommand, self).__init__(**kwargs)


class OsdCephCommand(CephCommandBase):

    def __init__(self, cmd, **kwargs):
        self._cmd = cmd
        self._osdstat = kwargs.get('osdstat')
        self._osdtree = kwargs.get('osdtree')
        super(OsdCephCommand, self).__init__(**kwargs)


class MdsCephCommand(CephCommandBase):

    def __init__(self, cmd, **kwargs):
        self._cmd = cmd
        self._mdsstat = kwargs.get('mdsstat')
        super(MdsCephCommand, self).__init__(**kwargs)


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
    if hasattr(arguments, 'status'):
        # Common command
        ccmd = CommonCephCommand(arguments)
        cephcmd = ccmd.build_common_command()
        ccmd.run_ceph_command(cephcmd)
    elif hasattr(arguments, 'mon'):
        pass
    elif hasattr(arguments, 'osdstat'):
        pass
    elif hasattr(arguments, 'mdsstat'):
        pass
    else:
        pass
    # command = compose_command(arguments)
    # if not command:
        # parser.error('Missing mandatory argument --status or --health')
    # result = do_ceph_command(command)
    # return result


if __name__ == "__main__":
    sys.exit(main())
