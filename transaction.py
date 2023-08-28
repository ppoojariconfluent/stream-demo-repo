#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2020 Confluent Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


# A simple example demonstrating use of AvroSerializer.

import argparse
import os
from uuid import uuid4
import uuid
import random

from six.moves import input

from confluent_kafka import Producer
from confluent_kafka.serialization import StringSerializer, SerializationContext, MessageField
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer


class Transaction(object):
    """
    User record

    Args:
        name (str): User's name

        favorite_number (int): User's favorite number

        favorite_color (str): User's favorite color

        address(str): User's address; confidential
    """

    def __init__(self, transaction_id, account_number, amount, transaction_type):
        self.transaction_id = transaction_id
        self.account_number = account_number
        self.amount = amount
        # address should not be serialized, see user_to_dict()
        self.transaction_type = transaction_type


def transaction_to_dict(transaction, ctx):
    """
    Returns a dict representation of a User instance for serialization.

    Args:
        user (User): User instance.

        ctx (SerializationContext): Metadata pertaining to the serialization
            operation.

    Returns:
        dict: Dict populated with user attributes to be serialized.
    """

    # User._address must not be serialized; omit from dict
    return dict(transaction_id=transaction.transaction_id,
                account_number=transaction.account_number,
                amount=transaction.amount,
                transaction_type=transaction.transaction_type
                )


def delivery_report(err, msg):
    """
    Reports the failure or success of a message delivery.

    Args:
        err (KafkaError): The error that occurred on None on success.

        msg (Message): The message that was produced or failed.

    Note:
        In the delivery report callback the Message.key() and Message.value()
        will be the binary format as encoded by any configured Serializers and
        not the same object that was passed to produce().
        If you wish to pass the original object(s) for key and value to delivery
        report callback we recommend a bound callback or lambda where you pass
        the objects along.
    """

    if err is not None:
        print("Delivery failed for User record {}: {}".format(msg.key(), err))
        return
    print('User record {} successfully produced to {} [{}] at offset {}'.format(
        msg.key(), msg.topic(), msg.partition(), msg.offset()))


def main(args):
    topic = 'bank-transactions'
    schema = "transaction.avsc"


    path = os.path.realpath(os.path.dirname(__file__))
    with open(f"{path}/avro/{schema}") as f:
        schema_str = f.read()

    schema_registry_conf = {
        'url': 'enter your schema registry url',
        'basic.auth.user.info': 'schema_registry_key:schema_registry_secret'
        }
    schema_registry_client = SchemaRegistryClient(schema_registry_conf)

    avro_serializer = AvroSerializer(schema_registry_client,
                                     schema_str,
                                     transaction_to_dict)

    string_serializer = StringSerializer('utf_8')

    producer_conf = {'bootstrap.servers': 'bootstrap url',
    'sasl.mechanisms': 'PLAIN',
    'security.protocol': 'SASL_SSL',
    'sasl.username': 'cluster api key',
    'sasl.password': 'cluster api secret',
    }

    producer = Producer(producer_conf)

    print("Producing transactional records to topic {}. ^C to exit.".format(topic))
    for _ in range(30):
        # Serve on_delivery callbacks from previous calls to produce()
        producer.poll(0.0)
        try:
            # transaction_transaction_id = input("Enter transaction_id: ")
            # transaction_account_number = input("Enter account number: ")
            # transaction_amount = input("Enter amount: ")
            # transaction_transaction_type = input("Enter transaction type: ")
            transaction_transaction_id = str(uuid.uuid4())
            transaction_account_number = f"account_{random.randint(1, 5)}"
            transaction_amount = round(random.uniform(10, 500), 2)
            transaction_transaction_type = random.choice(["debit", "credit"])
            transaction = Transaction(transaction_id=transaction_transaction_id,
                        account_number=transaction_account_number,
                        amount=transaction_amount,
                        transaction_type=transaction_transaction_type)
            producer.produce(topic=topic,
                             key=string_serializer(str(uuid4())),
                             value=avro_serializer(transaction, SerializationContext(topic, MessageField.VALUE)),
                             on_delivery=delivery_report)
        except KeyboardInterrupt:
            break
        except ValueError:
            print("Invalid input, discarding record...")
            continue

    print("\nFlushing records...")
    producer.flush()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="AvroSerializer example")
    parser.add_argument('-b', dest="bootstrap_servers", required=True,
                        help="Bootstrap broker(s) (host[:port])")
    parser.add_argument('-s', dest="schema_registry", required=True,
                        help="Schema Registry (http(s)://host[:port]")
    parser.add_argument('-t', dest="topic", default="example_serde_avro",
                        help="Topic name")
    parser.add_argument('-p', dest="specific", default="true",
                        help="Avro specific record")

    main(parser.parse_args())

