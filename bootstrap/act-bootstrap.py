#!/usr/bin/env python3

import argparse
import json
import os
import sys
from logging import critical, warning

import act


def parseargs():
    """ Parse arguments """
    parser = argparse.ArgumentParser(description="ACT Bootstrap data model")
    parser.add_argument(
        "--userid",
        type=int,
        dest="user_id",
        required=True,
        help="User ID")
    parser.add_argument(
        "--object-types",
        dest="object_types_filename",
        required=True,
        help="Object type defintions (json)")
    parser.add_argument(
        "--fact-types",
        dest="fact_types_filename",
        required=True,
        help="Fact type defintions (json)")
    parser.add_argument(
        "--meta-fact-types",
        dest="meta_fact_types_filename",
        required=True,
        help="Meta Fact type defintions (json)")
    parser.add_argument(
        "--logfile",
        dest="log_file",
        help="Log to file (default = stdout)")
    parser.add_argument(
        "--loglevel",
        dest="log_level",
        default="info",
        help="Loglevel (default = info)")
    parser.add_argument(
        "--act-baseurl",
        dest="act_baseurl",
        required=True,
        help="API URI")

    return parser.parse_args()


def create_object_types(client, object_types_filename):
    if not os.path.isfile(object_types_filename):
        critical("Object defintion file not found: %s" % object_types_filename)
        sys.exit(1)

    try:
        object_types = json.loads(open(object_types_filename).read())
    except json.decoder.JSONDecodeError:
        critical("Unable to parse file as json: %s" % object_types_filename)
        sys.exit(1)

    existing_object_types = [object_type.name
                             for object_type in client.get_object_types()]

    # Create all objects
    for object_type in object_types:
        name = object_type["name"]
        validator = object_type.get("validator", act.DEFAULT_VALIDATOR)

        if name in existing_object_types:
            warning("Object type %s already exists" % name)
            continue

        client.object_type(name=name, validator_parameter=validator).add()


def create_fact_types(client, fact_types_filename):
    # Create fact type with allowed bindings to ALL objects
    # We want to change this later, but keep it like this to make it simpler
    # when evaluating the data model

    if not os.path.isfile(fact_types_filename):
        critical("Facts defintion file not found: %s" % fact_types_filename)

    try:
        fact_types = json.loads(open(fact_types_filename).read())
    except json.decoder.JSONDecodeError:
        critical("Unable to parse file as json: %s" % fact_types_filename)
        sys.exit(1)

    for fact_type in fact_types:
        name = fact_type["name"]
        validator = fact_type.get("validator", act.DEFAULT_VALIDATOR)
        object_bindings = fact_type.get("objectBindings", [])

        if not object_bindings:
            client.create_fact_type_all_bindings(
                name, validator_parameter=validator)

        else:
            client.create_fact_type(name, validator=validator, object_bindings=object_bindings)


def create_meta_fact_types(client, meta_fact_types_filename):
    # Create fact type with allowed bindings to ALL objects
    # We want to change this later, but keep it like this to make it simpler
    # when evaluating the data model

    if not os.path.isfile(meta_fact_types_filename):
        critical("Meta Fact defintions file not found: %s" % meta_fact_types_filename)

    try:
        meta_fact_types = json.loads(open(meta_fact_types_filename).read())
    except json.decoder.JSONDecodeError:
        critical("Unable to parse file as json: %s" % meta_fact_types_filename)
        sys.exit(1)

    for meta_fact_type in meta_fact_types:
        name = meta_fact_type["name"]
        validator = meta_fact_type.get("validator", act.DEFAULT_VALIDATOR)
        fact_bindings = meta_fact_type.get("factBindings", [])

        if not fact_bindings:
            client.create_meta_fact_type_all_bindings(name, validator_parameter=validator)

        else:
            client.create_meta_fact_type(name, fact_bindings=fact_bindings, validator=validator)


if __name__ == "__main__":
    args = parseargs()

    client = act.Act(
        args.act_baseurl,
        args.user_id,
        args.log_level,
        args.log_file,
        "act-types")
    create_object_types(
        client, object_types_filename=args.object_types_filename)
    create_fact_types(client, fact_types_filename=args.fact_types_filename)
    create_meta_fact_types(client, meta_fact_types_filename=args.meta_fact_types_filename)
