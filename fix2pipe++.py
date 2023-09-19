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


def print_fix_msg(msg_map, tags_map, direction):
    for key, value in sorted(msg_map.items()):
        description = None
        if not tags_map is None and key in tags_map.keys():            
            description = tags_map[key]
        if description is None:
            description = ""
        if direction == 'incoming':
            color_str = colors.GREEN
        else:
            color_str = colors.BLUE
        output = "{0:6} {1:28} {2}".format(key, description, value)
        print(color_str + output + colors.ENDCOLOR)


def parse_fix_msg(msg, tags_map, direction):
    msg_map = {}
    fields = msg.split('\x01')
    for field in fields:
        if len(field) > 0:
            tag_value = field.split('=')
            tag = tag_value[0]
            value = tag_value[1]
            msg_map[int(tag)] = value

    print_fix_msg(msg_map, tags_map, direction)
    

def parse_line(line, tags_map, only_fix):
    result = re.search('.+<.+->.+,.+> (incoming|outgoing): (.*)', line)
    if not only_fix:            
        print(line, end="")
    
    if result:
        msg = result.groups()[1]        
        parse_fix_msg(msg, tags_map, result.groups()[0])
        if only_fix:        
            print('------------------------------------------------------')


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="fix2pipe++ fix parser",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-t", "--tags", help="path to Tag.hpp")
    parser.add_argument("-o", "--only-fix", action="store_true", help="only outputs formatted fix")

    args = parser.parse_args()
    config = vars(args)

    tags_map = None
    if config['tags']:
        tags_map = parse_tags_file(config['tags'])
    
    only_fix = config['only_fix']

    for line in sys.stdin:
        parse_line(line, tags_map, only_fix)
