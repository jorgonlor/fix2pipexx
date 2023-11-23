class colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    RED = '\033[31m'
    YELLOW = '\033[33m'
    ENDCOLOR = '\033[0m'


def print_color(color, txt):
    print(color + txt + colors.ENDCOLOR)


def print_error(txt):
    print_color(colors.RED, "ERROR: " + txt)


def print_warning(txt):
    print_color(colors.RED, "WARNING: " + txt)


def print_info(txt):
    print_color(colors.YELLOW, "INFO: " + txt)