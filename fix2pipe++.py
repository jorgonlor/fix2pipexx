#!/usr/bin/env python

import re, sys, argparse


class colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    ENDCOLOR = '\033[0m'


def parse_tags_file(tags_filename):
    tags_map = {}
    tags_file = open(tags_filename, "r")
    tags_file_content = tags_file.read()
    result = re.search('enum class Tag : int \{([\s\S]*?)\};', tags_file_content)
    if result:
        for line in result.groups()[0].splitlines():
            tag_name_and_value = line.split('=')
            if len(tag_name_and_value) == 2:
                tag_name = tag_name_and_value[0]
                value = tag_name_and_value[1]
                tags_map[int(value.strip(' ,'))] = tag_name.strip()
    else:
        print('Error parsing tags file ' + tags_filename)
    
    return tags_map


def tag_key(t):
    return t[0]


def name_key(t):
    return t[1]


def print_fix_msg(msg_map, tags_map, direction, sort_by):
    msg_fields = []
    for key, value in msg_map.items():
        name = ""
        if not tags_map is None and key in tags_map.keys():            
            name = tags_map[key]
        msg_fields.append((key, name, value))

    if sort_by == 'name' and not tags_map is None:
        msg_fields.sort(key=name_key)
    else:
        msg_fields.sort(key=tag_key)

    for key, name, value in msg_fields:
        if direction == 'incoming':
            color_str = colors.GREEN
        else:
            color_str = colors.BLUE
        output = "{0:6} {1:28} {2}".format(key, name, value)
        print(color_str + output + colors.ENDCOLOR)


def parse_fix_msg(msg, tags_map, direction, sort_by):
    msg_map = {}
    fields = msg.split('|')
    for field in fields:
        if len(field) > 0:
            tag_value = field.split('=')
            tag = tag_value[0]
            value = tag_value[1]
            msg_map[int(tag)] = value

    print_fix_msg(msg_map, tags_map, direction, sort_by)
    

def parse_line(line, tags_map, only_fix, sort_by):
    line = line.replace('\x01', '|')
    result = re.search('.+<.+->.+,.+> (incoming|outgoing): (.*)', line)

    if not only_fix:
        print(line, end="")
    
    if result:
        direction = result.groups()[0]
        msg = result.groups()[1]
        parse_fix_msg(msg, tags_map, direction, sort_by)
        if only_fix:        
            print('------------------------------------------------------')


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="fix2pipe++ fix parser",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-t", "--tags", help="path to Tag.hpp")
    parser.add_argument("-o", "--only-fix", action="store_true", help="only outputs formatted fix")
    parser.add_argument("-s", "--sort-by", choices=['tag', 'name'], default='tag', help="sorts fields by tag number or name")

    args = parser.parse_args()
    config = vars(args)

    tags_map = None
    if config['tags']:
        tags_map = parse_tags_file(config['tags'])
    
    only_fix = config['only_fix']
    sort_by = config['sort_by']

    for line in sys.stdin:
        parse_line(line, tags_map, only_fix, sort_by)
