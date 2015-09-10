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
import os
import subprocess
import argparse
import sys

# nagios exit code
STATUS_OK = 0
STATUS_WARNING = 1
STATUS_ERROR = 2
STATUS_UNKNOWN = 3

# default ceph values
CEPH_COMMAND = '/usr/bin/ceph'
CEPH_CONFIG = '/etc/ceph/ceph.conf'

__version__ = '0.2'


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
        self._nagiosmessage = ''

    @property
    def cephexec(self):
        """
        Get ceph executable
        :return: ceph executable
        """
        return self._cephexec

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
        return self._cephconf

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
        except OSError:
            self.nagiosmessage = 'ERROR: Ceph executable not found - {0}'.format(self.cephexec)
            return STATUS_ERROR
        output = output.strip()
        if output:
            if output.find('HEALTH_OK') != -1:
                self.nagiosmessage = output
                nagioscode = STATUS_OK
            elif output.find('HEALTH_WARN') != -1:
                self.nagiosmessage = output
                nagioscode = STATUS_WARNING
            elif output.find('HEALTH_ERR') != -1:
                self.nagiosmessage = output
                nagioscode = STATUS_ERROR
            else:
                if not os.path.exists(self.cephconf):
                    self.nagiosmessage = 'ERROR: No such file - {0}'.format(self.cephconf)
                    nagioscode = STATUS_ERROR
                else:
                    self.nagiosmessage = 'OK: {0}'.format(output)
                    nagioscode = STATUS_OK
        elif err:
            self.nagiosmessage = 'ERROR: {0}'.format(err.strip())
            nagioscode = STATUS_ERROR
        else:
            nagioscode = STATUS_ERROR

        return nagioscode

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
        self._monstatus = getattr(cliargs, 'monstatus')
        self._monstat = getattr(cliargs, 'monstat')
        super(MonCephCommand, self).__init__(cliargs)

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
        if self.monstatus:
            cmd.append('mon_status')
        elif self.monstat:
            cmd.append('mon')
            cmd.append('stat')
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
        cmd.append('mds')
        cmd.append('stat')
        return cmd


def _parse_arguments():
    """
    Parse command line arguments
    :return: Command line arguments
    """
    parser = argparse.ArgumentParser(description='ceph nagios plugin', version=__version__)
    parser.add_argument('-e', '--exe', default=CEPH_COMMAND, help='ceph executable [{0}]'.format(CEPH_COMMAND))
    parser.add_argument('-c', '--conf', default=CEPH_CONFIG, help='alternative ceph conf file [{0}]'.format(CEPH_CONFIG))
    parser.add_argument('-m', '--monaddress', help='ceph monitor address[:port]')
    parser.add_argument('-i', '--monid', help='ceph client id')
    parser.add_argument('-n', '--name', help='ceph client name')
    parser.add_argument('-k', '--keyring', help='ceph client keyring file')

    subparsers = parser.add_subparsers(help='Ceph commands options help')

    cephcommonparser = subparsers.add_parser('common', help='Ceph common options')
    cephcommonparsergrp = cephcommonparser.add_mutually_exclusive_group()
    cephcommonparsergrp.add_argument('--status', action='store_true', help='Show ceph status')
    cephcommonparsergrp.add_argument('--health', action='store_true', help='Show ceph health')
    cephcommonparsergrp.add_argument('--quorum', action='store_true', help='Show ceph quorum')
    cephcommonparsergrp.add_argument('--df', action='store_true', help='Show ceph pools status')

    cephmonparser = subparsers.add_parser('mon', help='Ceph monitor options')
    cephmonparsergrp = cephmonparser.add_mutually_exclusive_group()
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
        result = ccmd.run_ceph_command(cephcmd)
    elif hasattr(arguments, 'monstatus'):
        # Mon command
        ccmd = MonCephCommand(arguments)
        moncmd = ccmd.build_mon_command()
        result = ccmd.run_ceph_command(moncmd)
    elif hasattr(arguments, 'stat'):
        # Osd command
        ccmd = OsdCephCommand(arguments)
        osdcmd = ccmd.build_osd_command()
        result = ccmd.run_ceph_command(osdcmd)
    elif hasattr(arguments, 'mdsstat'):
        # Mds command
        ccmd = MdsCephCommand(arguments)
        mdscmd = ccmd.build_mds_command()
        result = ccmd.run_ceph_command(mdscmd)
    else:
        ccmd = 'No valid command found'
        result = STATUS_ERROR
    print(ccmd)
    return result


if __name__ == "__main__":
    sys.exit(main())
