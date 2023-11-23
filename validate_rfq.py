from util import *

valid_tenors = ('SP', 'IMM1', 'IMM2', 'IMM3', 'IMM4', 'TOD', 'TOM', 'SN', '1W', '2W', '3W', '1M', '2M', '3M', '4M', '5M', '6M', '7M', '8M', '9M', '10M', '11M', '1Y')

def skip_validation(a, b):
    pass


def check_expected_fields(expected_fields, msg, tags_map):
    error = False
    for key in expected_fields:
        if not key in msg.keys():
            print_error("{0}<{1}> not found".format(tags_map[key], str(key)))
            error = True
    if error:
        return True
    for key in expected_fields:
        if msg[key] == '':
            print_error("{0}<{1}> is empty".format(tags_map[key], str(key)))
            error = True
    return error


def check_unexpected_fields(unexpected_fields, msg, tags_map):
    error = False
    for key in unexpected_fields:
        if key in msg.keys():
            print_error("Unexpected {0}<{1}> found".format(tags_map[key], str(key)))
            error = True
    return error


def check_fields_not_zero(keys, msg, tags_map):
    for key in keys:        
        if key in msg.keys() and (msg[key] == '0' or msg[key] == '0.0'):
            print_error("{0}<{1}> is zero".format(tags_map[key], str(key)))

    
def check_fields_zero(keys, msg, tags_map):
    for key in keys:        
        if key in msg.keys() and (msg[key] != '0' and msg[key] != '0.0'):
            print_error("{0}<{1}> is NOT zero".format(tags_map[key], str(key)))


# REJECTED EXECUTION REPORT
def validate_to_crossfire_exec_report_swap_rejected(msg, tags_map):
    print_info("Validating outgoing Swap ExecutionReport(F)")
    error = check_expected_fields((195, 64, 20005, 192, 640, 20011, 20012, 20015, 641, 193), msg, tags_map)
    error = error or check_fields_not_zero((64, 192, 640, 20012, 20015, 20014, 20013, 641, 193), msg, tags_map)
    if 20011 in msg.keys() and msg[20011] != '0':
        print_error("LeavesQty2<20011> is not zero")

# FILLED EXECUTION REPORT

def validate_to_crossfire_exec_report_spot_filled(msg, tags_map):
    print_info("Validating outgoing Spot ExecutionReport(F)")
    check_unexpected_fields((20005, 20001, 192, 640, 20011, 20012, 20015, 20014, 20013, 641, 193, 195), msg, tags_map)
    if 20000 in msg.keys() and msg[20000] != 'SP':
        print_error("SpotFwd Tenor<20000> must be SP")


def validate_to_crossfire_exec_report_forward_filled(msg, tags_map):
    print_info("Validating outgoing Forward ExecutionReport(F)")
    error = check_expected_fields((20000, 195, 64), msg, tags_map)
    error = error or check_unexpected_fields((20005, 20001, 192, 640, 20011, 20012, 20015, 20014, 20013, 641, 193), msg, tags_map)
    if 20000 in msg.keys() and msg[20000] == 'SP':
        print_error("Forward Tenor<20000> must not be SP")
    if error:
        return    
    check_fields_not_zero((195, 64), msg, tags_map)


def validate_to_crossfire_exec_report_swap_filled(msg, tags_map):
    print_info("Validating outgoing Swap ExecutionReport(F)")
    error = check_expected_fields((195, 64, 20005, 192, 640, 20011, 20012, 20015, 20014, 20013, 641, 193), msg, tags_map)
    error = error or check_fields_not_zero((64, 192, 640, 20012, 20015, 20014, 20013, 641, 193), msg, tags_map)
    if 20011 in msg.keys() and msg[20011] != '0':
        print_error("LeavesQty2<20011> is not zero")


def validate_to_crossfire_exec_report_ndf_filled(msg, tags_map):
    print_info("Validating outgoing NDF ExecutionReport(F)")
    error = check_expected_fields((20000, 195, 64, 20001), msg, tags_map)
    error = error or check_unexpected_fields((20005, 192, 640, 20011, 20012, 20015, 20014, 20013, 641, 193), msg, tags_map)
    error = error or check_fields_not_zero((195, 64, 20001), msg, tags_map)


def validate_to_crossfire_exec_report_ndf_swap_filled(msg, tags_map):
    print_info("Validating outgoing NDFSwap ExecutionReport(F)")
    error = check_expected_fields((195, 64, 20005, 192, 640, 20011, 20012, 20015, 20014, 20013, 641, 193, 20001, 20006), msg, tags_map)
    error = error or check_fields_not_zero((64, 192, 640, 20012, 20015, 20014, 20013, 641, 193, 20001, 20006), msg, tags_map)
    if 20011 in msg.keys() and msg[20011] != '0':
        print_error("LeavesQty2<20011> is not zero")


def validate_to_crossfire_exec_report_filled(msg, tags_map, instr_type):
    print_info("Validating outgoing ExecutionReport(Filled, 150=F)")
    error = check_expected_fields((1, 55, 17, 37, 11, 54, 40, 44, 59, 150, 39, 38, 31, 32, 151, 14, 6), msg, tags_map)
    if error:
        return
    if not msg[59] in ('3', '4'):
        print_error("TimeInForce<59> must be IOC(3) or FOK(4)")
    if 20000 in msg.keys():
        if msg[20000] not in valid_tenors:
            print_error("Invalid Tenor<20000> " + msg[20000])
    if error:
        return    
    check_fields_not_zero((14, 31, 32, 38, 44), msg, tags_map)
    if msg[151] != '0' and msg[151] != '0.0':
        print_error("LeavesQty<151> is not zero: " + msg[151])
    validate_funcs = {'SPOTFWD': validate_to_crossfire_exec_report_spot_filled,
                      'FWD': validate_to_crossfire_exec_report_forward_filled,
                      'SWAP': validate_to_crossfire_exec_report_swap_filled,
                      'NDF': validate_to_crossfire_exec_report_ndf_filled,
                      'NDFSWAP': validate_to_crossfire_exec_report_ndf_swap_filled}
    if not instr_type in validate_funcs.keys():
        print_error("Invalid SecurityType=" + instr_type)
    if error:
        return    
    validate_func = validate_funcs[instr_type]
    validate_func(msg, tags_map)


def validate_to_crossfire_exec_report_rejected(msg, tags_map, instr_type):
    print_info("Validating outgoing ExecutionReport(Rejected, 150=8)")
    error = check_expected_fields((1, 55, 17, 37, 11, 54, 40, 44, 59, 150, 39, 38, 151, 14, 6), msg, tags_map)
    if error:
        return
    if not msg[59] in ('3', '4'):
        print_error("TimeInForce<59> must be IOC(3) or FOK(4)")
    if 20000 in msg.keys():
        if msg[20000] not in valid_tenors:
            print_error("Invalid Tenor<20000> " + msg[20000])
    if error:
        return    
    
    check_fields_not_zero((38, 44), msg, tags_map)    
    check_unexpected_fields( (31, 32), msg, tags_map)
    check_fields_zero((6, 14, 151), msg, tags_map)

    if instr_type in ['SWAP', 'NDFSWAP']:
        check_fields_not_zero([640], msg, tags_map)
        check_unexpected_fields((20013, 20014), msg, tags_map)
        check_fields_zero((20015, 20012, 20011), msg, tags_map)

    validate_funcs = {'SPOTFWD': validate_to_crossfire_exec_report_spot_filled,
                      'FWD': validate_to_crossfire_exec_report_forward_filled,
                      'SWAP': validate_to_crossfire_exec_report_swap_rejected,
                      'NDF': validate_to_crossfire_exec_report_ndf_filled,
                      'NDFSWAP': validate_to_crossfire_exec_report_ndf_swap_filled}
    if not instr_type in validate_funcs.keys():
        print_error("Invalid SecurityType=" + instr_type)
    if error:
        return    
    validate_func = validate_funcs[instr_type]
    validate_func(msg, tags_map)


def validate_to_crossfire_exec_report(msg, tags_map):
    if not 167 in msg.keys():
        instr_type = 'SPOTFWD'
    else:
        instr_type = msg[167]
    print_info("Validating outgoing ExecutionReport")
    if not 150 in msg.keys():
        print_error("ExecType<150> not found")
        return    
    exec_type = msg[150]
    if exec_type == 'F':
        validate_to_crossfire_exec_report_filled(msg, tags_map, instr_type)
    elif exec_type == '8':
        validate_to_crossfire_exec_report_rejected(msg, tags_map, instr_type)

# QUOTES

def validate_to_crossfire_quote_spot(msg, tags_map):
    print_info("validating outgoing Spot Quote")


def validate_to_crossfire_quote_forward(msg, tags_map):
    print_color(colors.YELLOW, "Validating outgoing Forward Quote")
    error = check_expected_fields((20000, 189, 191, 64), msg, tags_map)
    if error:
        return
    check_fields_not_zero((189, 191, 64), msg, tags_map)


def validate_to_crossfire_quote_swap(msg, tags_map):
    print_color(colors.YELLOW, "Validating outgoing Swap Quote")
    error = check_expected_fields((20000, 20005, 192, 20009, 20007, 20010, 20008, 642, 643, 189, 191, 64, 193), msg, tags_map)


def validate_to_crossfire_quote_ndf(msg, tags_map):
    print_color(colors.YELLOW, "Validating outgoing NDF Quote")
    error = check_expected_fields((20000, 189, 191, 20001, 64), msg, tags_map)


def validate_to_crossfire_quote_ndf_swap(msg, tags_map):
    print_color(colors.YELLOW, "Validating outgoing NDFSwap Quote")
    error = check_expected_fields((20000, 20005, 192, 20009, 20007, 20010, 20008, 642, 643, 189, 191, 20001, 20006, 64, 193), msg, tags_map)


def validate_to_crossfire_quote(msg, tags_map):
    if not 167 in msg.keys():
        print_error("SecurityType(167) not found")
        return
    instr_type = msg[167]
    print_color(colors.YELLOW, "Validating outgoing Quote")
    error = check_expected_fields((1, 131, 55, 117, 38, 134, 132, 135, 133, 20003), msg, tags_map)
    validate_funcs = {'SPOTFWD': validate_to_crossfire_quote_spot,
                      'FWD': validate_to_crossfire_quote_forward,
                      'SWAP': validate_to_crossfire_quote_swap,
                      'NDF': validate_to_crossfire_quote_ndf,
                      'NDFSWAP': validate_to_crossfire_quote_ndf_swap}
    if not instr_type in validate_funcs.keys():
        print_error("Invalid SecurityType=" + instr_type)
    if error:
        return    
    check_fields_not_zero((38, 134, 132, 135, 133), msg, tags_map)    
    validate_func = validate_funcs[instr_type]
    validate_func(msg, tags_map)


def validate_msg(msg, tags_map, direction):    
    if direction == "outgoing" and msg[35] == 'S':
        validate_to_crossfire_quote(msg, tags_map)
    if direction == "outgoing" and msg[35] == '8':
        validate_to_crossfire_exec_report(msg, tags_map)
