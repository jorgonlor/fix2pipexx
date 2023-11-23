#!/usr/bin/env python

import re, sys, argparse
from util import *

# from validate_rfq import *


def parse_tags_file(tags_filename):
    tags_map = {}
    tags_file = open(tags_filename, "r")
    tags_file_content = tags_file.read()
    result = re.search("enum class Tag : int \{([\s\S]*?)\};", tags_file_content)
    if result:
        for line in result.groups()[0].splitlines():
            line = line.strip()
            if line[:2] == "//":
                continue
            tag_name_and_value = line.split("=")
            if len(tag_name_and_value) == 2:
                tag_name = tag_name_and_value[0]
                value = tag_name_and_value[1]
                tags_map[int(value.strip(" ,"))] = tag_name.strip()
    else:
        print("Error parsing tags file " + tags_filename)

    return tags_map


def tag_key(t):
    return t[0]


def name_key(t):
    return t[1]


tag_value_descriptions = {
    35: {
        "0": "Heartbeat",
        "1": "Test Request",
        "3": "Reject",
        "4": "Sequence Reset",
        "5": "Logout",
        "8": "Execution Report",
        "9": "Order Cancel Reject",
        "A": "Logon",
        "D": "New Order Single",
        "F": "Order Cancel Request",
        "G": "Order Cancel/Repalce Request",
        "Q": "Dont Know Trade",
        "R": "Quote Request",
        "S": "Quote",
        "W": "Market Data Snapshot",
        "X": "Market Data Incremental",
        "Y": "Market Data Request Reject",
        "Z": "Quote Cancel",
        "a": "Quote Status Request",
        "b": "Quote Ack",
        "d": "Security Definition",
        "g": "Trading Session Status Request",
        "h": "Trading Session Status",
        "i": "Mass Quote",
        "j": "Business Message Reject",
    }
}


def describe_field(key, val):
    if key in tag_value_descriptions:
        key_desc = tag_value_descriptions[key]
        if val in key_desc:
            return "(" + key_desc[val] + ")"

    return ""


def print_fix_msg(msg_map, tags_map, direction, sort_by):
    msg_fields = []
    for key, value in msg_map.items():
        name = ""
        if not tags_map is None and key in tags_map.keys():
            name = tags_map[key]
        msg_fields.append((key, name, value))

    # validate_msg(msg_map, tags_map, direction)

    if sort_by == "name" and not tags_map is None:
        msg_fields.sort(key=name_key)
    else:
        msg_fields.sort(key=tag_key)

    for key, name, value in msg_fields:
        if direction == "incoming":
            color_str = colors.GREEN
        else:
            color_str = colors.BLUE
        output = "{0:6} {1:28} {2} {3}".format(
            key, name, value, describe_field(key, value)
        )
        print(color_str + output + colors.ENDCOLOR)

    # TESTS
    # for key, name, value in msg_fields:
    #     if name in ["MsgType", "CheckSum", "BeginString", "BodyLength", "MsgSeqNum", "SendingTime", "SenderCompId", "TargetCompId", "TransactTime", "SenderSubId"]:
    #         continue
    #     print("BOOST_CHECK_EQUAL(lex.find(Tag::{0}).first, \"{1}\");".format(name, value))


def parse_fix_msg(msg, tags_map, direction, sort_by):
    msg_map = {}
    fields = msg.split("|")
    for field in fields:
        if len(field) > 0:
            tag_value = field.split("=")
            tag = int(tag_value[0])
            value = tag_value[1].strip(" ,\x01")
            if direction == "outgoing " and tag in msg_map:
                tag_name = ""
                if tag in tags_map:
                    tag_name = tags_map[tag]
                print_warning("Duplicated tag {0}<{1}>".format(tag_name, tag))
            msg_map[tag] = value

    print_fix_msg(msg_map, tags_map, direction, sort_by)


def parse_line(line, tags_map, only_fix, sort_by):
    line = line.replace("\x01", "|")
    result = re.search(".+<.+->.+,.+> (incoming|outgoing): (.*)", line)

    if not only_fix:
        print(line, end="")

    if result:
        direction = result.groups()[0]
        msg = result.groups()[1]
        parse_fix_msg(msg, tags_map, direction, sort_by)
        if only_fix:
            print("------------------------------------------------------")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="fix2pipe++ fix parser",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("-t", "--tags", help="path to Tag.hpp")
    parser.add_argument(
        "-o", "--only-fix", action="store_true", help="only outputs formatted fix"
    )
    parser.add_argument(
        "-s",
        "--sort-by",
        choices=["tag", "name"],
        default="tag",
        help="sorts fields by tag number or name",
    )

    args = parser.parse_args()
    config = vars(args)

    tags_map = None
    if config["tags"]:
        tags_map = parse_tags_file(config["tags"])

    only_fix = config["only_fix"]
    sort_by = config["sort_by"]

    for line in sys.stdin:
        parse_line(line, tags_map, only_fix, sort_by)
