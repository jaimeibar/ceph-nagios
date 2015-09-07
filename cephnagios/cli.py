

import argparse
import sys

from cephnagios.check_ceph_health import CommonCephCommand

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
        result = ccmd.run_ceph_command(cephcmd)
    elif hasattr(arguments, 'mon'):
        pass
    elif hasattr(arguments, 'osdstat'):
        pass
    elif hasattr(arguments, 'mdsstat'):
        pass
    else:
        pass
    print(ccmd)
    return result


if __name__ == "__main__":
    sys.exit(main())
