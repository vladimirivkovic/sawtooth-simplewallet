# Copyright 2018 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ------------------------------------------------------------------------------
'''     
Command line interface for the marbles transaction family.

Parses command line arguments and passes it to the SimpleWalletClient class
to process.
''' 

import argparse
import getpass
import logging
import os
import sys
import traceback
import pkg_resources

from colorlog import ColoredFormatter

from marbles.marbles_client import MarblesClient

DISTRIBUTION_NAME = 'marbles'

DEFAULT_URL = 'http://rest-api:8008'

USER_NAME = 'jack'

def create_console_handler(verbose_level):
    clog = logging.StreamHandler()
    formatter = ColoredFormatter(
        "%(log_color)s[%(asctime)s %(levelname)-8s%(module)s]%(reset)s "
        "%(white)s%(message)s",
        datefmt="%H:%M:%S",
        reset=True,
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red',
        })

    clog.setFormatter(formatter)
    clog.setLevel(logging.DEBUG)
    return clog

def setup_loggers(verbose_level):
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(create_console_handler(verbose_level))

def add_init_parser(subparsers, parent_parser):
    '''Define the "init" command line parsing.'''
    parser = subparsers.add_parser(
        'init',
        help='init marble',
        parents=[parent_parser])

    parser.add_argument(
        'name',
        type=str,
        help='name of marble')

    parser.add_argument(
        'color',
        type=str,
        help='marble color')

    parser.add_argument(
        'size',
        type=int,
        help='marble size')

    parser.add_argument(
        'owner',
        type=str,
        help='owner of marble')

def add_delete_parser(subparsers, parent_parser):
    '''Define the "delete" command line parsing.'''
    parser = subparsers.add_parser(
        'delete',
        help='deletes a marble',
        parents=[parent_parser])

    parser.add_argument(
        'name',
        type=str,
        help='the name of marble')

def add_read_parser(subparsers, parent_parser):
    '''Define the "read" command line parsing.'''
    parser = subparsers.add_parser(
        'read',
        help='shows marble',
        parents=[parent_parser])

    parser.add_argument(
        'name',
        type=str,
        help='the name of marble')

def add_transfer_parser(subparsers, parent_parser):
    '''Define the "transfer" command line parsing.'''
    parser = subparsers.add_parser(
        'transfer',
        help='transfers marble from one owner to the other',
        parents=[parent_parser])

    parser.add_argument(
        'name',
        type=str,
        help='the name to marble')

    parser.add_argument(
        'owner',
        type=str,
        help='the name of new owner')

def create_parent_parser(prog_name):
    '''Define the -V/--version command line options.'''
    parent_parser = argparse.ArgumentParser(prog=prog_name, add_help=False)

    try:
        version = pkg_resources.get_distribution(DISTRIBUTION_NAME).version
    except pkg_resources.DistributionNotFound:
        version = 'UNKNOWN'

    parent_parser.add_argument(
        '-V', '--version',
        action='version',
        version=(DISTRIBUTION_NAME + ' (Hyperledger Sawtooth) version {}')
        .format(version),
        help='display version information')

    return parent_parser


def create_parser(prog_name):
    '''Define the command line parsing for all the options and subcommands.'''
    parent_parser = create_parent_parser(prog_name)

    parser = argparse.ArgumentParser(
        description='Provides subcommands to manage your marbles',
        parents=[parent_parser])

    subparsers = parser.add_subparsers(title='subcommands', dest='command')

    subparsers.required = True

    add_init_parser(subparsers, parent_parser)
    add_delete_parser(subparsers, parent_parser)
    add_read_parser(subparsers, parent_parser)
    add_transfer_parser(subparsers, parent_parser)

    return parser

def _get_keyfile(customerName):
    '''Get the private key for a customer.'''
    home = os.path.expanduser("~")
    key_dir = os.path.join(home, ".sawtooth", "keys")

    return '{}/{}.priv'.format(key_dir, customerName)

def _get_pubkeyfile(customerName):
    '''Get the public key for a customer.'''
    home = os.path.expanduser("~")
    key_dir = os.path.join(home, ".sawtooth", "keys")

    return '{}/{}.pub'.format(key_dir, customerName)

def do_init(args):
    '''Implements the "init" subcommand by calling the client class.'''
    keyfile = _get_keyfile(USER_NAME)

    client = MarblesClient(baseUrl=DEFAULT_URL, keyFile=keyfile)

    response = client.init(args)

    print("Response: {}".format(response))

def do_delete(args):
    '''Implements the "delete" subcommand by calling the client class.'''
    keyfile = _get_keyfile(USER_NAME)

    client = MarblesClient(baseUrl=DEFAULT_URL, keyFile=keyfile)

    response = client.delete(args.name)

    print("Response: {}".format(response))

def do_read(args):
    '''Implements the "read" subcommand by calling the client class.'''
    keyfile = _get_keyfile(USER_NAME)

    client = MarblesClient(baseUrl=DEFAULT_URL, keyFile=keyfile)

    data = client.read(args.name)

    if data is not None:
        print("\n{} Marble = {}\n".format(args.name,
                                                        data.decode()))
    else:
        raise Exception("Data not found: {}".format(args.name))

def do_transfer(args):
    '''Implements the "transfer" subcommand by calling the client class.'''
    keyfileFrom = _get_keyfile(USER_NAME)

    clientFrom = MarblesClient(baseUrl=DEFAULT_URL, keyFile=keyfileFrom)

    response = clientFrom.transfer(args)
    print("Response: {}".format(response))

def main(prog_name=os.path.basename(sys.argv[0]), args=None):
    '''Entry point function for the client CLI.'''
    if args is None:
        args = sys.argv[1:]
    parser = create_parser(prog_name)
    args = parser.parse_args(args)

    verbose_level = 0

    setup_loggers(verbose_level=verbose_level)

    # Get the commands from cli args and call corresponding handlers
    if args.command == 'init':
        do_init(args)
    elif args.command == 'delete':
        do_delete(args)
    elif args.command == 'read':
        do_read(args)
    elif args.command == 'transfer':
        do_transfer(args)
    else:
        raise Exception("Invalid command: {}".format(args.command))


def main_wrapper():
    try:
        main()
    except KeyboardInterrupt:
        pass
    except SystemExit as err:
        raise err
    except BaseException as err:
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

