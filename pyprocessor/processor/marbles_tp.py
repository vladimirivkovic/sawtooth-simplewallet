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
Transaction family class for marbles.
'''

import traceback
import sys
import hashlib
import logging

from sawtooth_sdk.processor.handler import TransactionHandler
from sawtooth_sdk.processor.exceptions import InvalidTransaction
from sawtooth_sdk.processor.exceptions import InternalError
from sawtooth_sdk.processor.core import TransactionProcessor

LOGGER = logging.getLogger(__name__)

FAMILY_NAME = "marbles"


def _hash(data):
    '''Compute the SHA-512 hash and return the result as hex characters.'''
    return hashlib.sha512(data).hexdigest()


# Prefix for marbles is the first six hex digits of SHA-512(TF name).
sw_namespace = _hash(FAMILY_NAME.encode('utf-8'))[0:6]


class Marble:
    def __init__(self, args):
        if len(args) != 4:
            raise InvalidTransaction("Invalid number of args")

        self.name = args[0]
        self.color = args[1]
        self.size = int(args[2])
        self.owner = args[3]

    def to_string(self):
        return ",".join([self.name, self.color, str(self.size), self.owner])


class MarblesTransactionHandler(TransactionHandler):
    '''                                                       
    Transaction Processor class for the marbles transaction family.       

    This with the validator using the accept/get/set functions.
    It implements functions to init, read, transfer and delete marble.
    '''

    def __init__(self, namespace_prefix):
        self._namespace_prefix = namespace_prefix

    @property
    def family_name(self):
        return FAMILY_NAME

    @property
    def family_versions(self):
        return ['1.0']

    @property
    def namespaces(self):
        return [self._namespace_prefix]

    def apply(self, transaction, context):
        '''This implements the apply function for this transaction handler.

           This function does most of the work for this class by processing
           a single transaction for the marbles transaction family.   
        '''

        # Get the payload and extract marbles-specific information.
        header = transaction.header
        payload_list = transaction.payload.decode().split(",")
        operation = payload_list[0]
        args = payload_list[1:]

        # Get the public key sent from the client.
        from_key = header.signer_public_key

        # Perform the operation.
        LOGGER.info("Operation = " + operation)

        if operation == "initMarble":
            self._init_marble(context, args)
        elif operation == "deleteMarble":
            self._delete_marble(context, args)
        elif operation == "transferMarble":
            if len(payload_list) == 3:
                to_key = payload_list[2]
            self._transfer_marble(context, args)
        else:
            LOGGER.info("Unhandled action. " +
                        "Operation should be deposit, withdraw or transfer")

    def _init_marble(self, context, args):
        key = args[0]
        marble_address = self._get_marble_address(key)
        LOGGER.info('Got the key {} and the marble address {} '.format(
            key, marble_address))
        current_entry = context.get_state([marble_address])

        if current_entry != []:
            raise InvalidTransaction("Marble already exists")

        state_data = str(','.join(args)).encode('utf-8')
        addresses = context.set_state({marble_address: state_data})

        if len(addresses) < 1:
            raise InternalError("State Error")

    def _delete_marble(self, context, args):
        if len(args) != 1:
            raise InvalidTransaction("Invalid number of args")

        key = args[0]
        marble_address = self._get_marble_address(key)
        LOGGER.info('Got the key {} and the wallet address {} '.format(
            key, marble_address))
        marble = context.get_state([marble_address])
        new_balance = 0

        if marble == []:
            LOGGER.info('No marble with the key {} '.format(key))
            return

        LOGGER.info('Deleting marble {} '.format(key))
        addresses = context.delete_state([marble_address])

        if len(addresses) < 1:
            raise InternalError("State Error")

    def _transfer_marble(self, context, args):
        if len(args) != 2:
            raise InvalidTransaction("Invalid number of args")

        key = args[0]
        to_person = args[1]

        marble_address = self._get_marble_address(key)
        LOGGER.info('Got the from key {} and the from wallet address {} '.format(
            key, marble_address))
        current_entry = context.get_state([marble_address])

        if current_entry == []:
            raise InvalidTransaction("Marble does not exist")

        marble = Marble(current_entry[0].data.decode().split(","))
        marble.owner = to_person

        context.set_state({marble_address: marble.to_string().encode('utf-8')})

    def _get_marble_address(self, from_key):
        return _hash(FAMILY_NAME.encode('utf-8'))[0:6] + _hash(from_key.encode('utf-8'))[0:64]


def setup_loggers():
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)


def main():
    '''Entry-point function for the marbles transaction processor.'''
    setup_loggers()
    try:
        # Register the transaction handler and start it.
        processor = TransactionProcessor(url='tcp://validator:4004')

        handler = MarblesTransactionHandler(sw_namespace)

        processor.add_handler(handler)

        processor.start()

    except KeyboardInterrupt:
        pass
    except SystemExit as err:
        raise err
    except BaseException as err:
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
