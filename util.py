'''
This file contains basic utility functions
'''
import binascii
import socket

MAX_NUM_CLIENTS = 10
TIME_OUT = 0.5 # 500ms
CHUNK_SIZE = 1400 # 1400 Bytes

def validate_checksum(message):
    '''
    Validates Checksum of a message and returns true/false
    '''
    try:
        msg, checksum = message.rsplit('|', 1)
        msg += '|'
        return generate_checksum(msg.encode()) == checksum
    except BaseException:
        return False


def generate_checksum(message):
    '''
    Returns Checksum of the given message
    '''
    return str(binascii.crc32(message) & 0xffffffff)


def make_packet(msg_type="data", seqno=0, msg=""):
    '''
    This will add the header to your message.
    The formats is `<message_type> <sequence_number> <body> <checksum>`
    msg_type can be data, ack, end, start
    seqno is a packet sequence number (integer)
    msg is the actual message string
    '''
    body = "%s|%d|%s|" % (msg_type, seqno, msg)
    checksum = generate_checksum(body.encode())
    packet = "%s%s" % (body, checksum)
    return packet


def parse_packet(message):
    '''
    This function will parse the packet in the same way it was made in the above function.
    '''
    pieces = message.split('|')
    msg_type, seqno = pieces[0:2]
    checksum = pieces[-1]
    data = '|'.join(pieces[2:-1])
    return msg_type, seqno, data, checksum


def make_message(msg_type, msg_format, message=None):
    '''
    This function can be used to format your message according
    to any one of the formats described in the documentation.
    msg_type defines type like join, disconnect etc.
    msg_format is either 1,2,3 or 4
    msg is remaining. 
    '''
    if msg_format == 2:
        msg_len = 0
        return "%s %d" % (msg_type, msg_len)
    if msg_format in [1, 3, 4]:
        msg_len = len(message)
        return "%s %d %s" % (msg_type, msg_len, message)
    return ""


def parse_message(data):
    '''
    This function will take data and split it into the separate components needed for make_message().
    data is the message to be parsed.
    '''
    message_contents = []
    last_space_index = -1
    max_spaces = 3
    spaces_found = 0
    # Loop until either a max of 3 spaces (4 components) or no more spaces are found.
    while spaces_found < max_spaces:
        # Search 1 ahead of the last space, up until the next space.
        next_space = data.find(" ", last_space_index + 1)
        # If no more spaces are found, break
        if next_space == -1:
            break
        else:
            component = data[last_space_index + 1:next_space]
            message_contents.append(component)
            spaces_found += 1
            last_space_index = next_space
    # Add the remaining component
    message_contents.append(data[last_space_index + 1:])
    return message_contents


def parse_input(user_input):
    '''
    This function will take user input and split it into separate components.
    input is the message to be parsed.
    '''

    input_contents = []
    # Strip input of trailing whitespace.
    user_input = user_input.strip()
    last_space_index = -1
    # If there is no spaces left, the input is just one argument
    next_space = user_input.find(" ", last_space_index + 1)
    if next_space == -1:
        input_contents.append(user_input)
    else:
        arg = user_input[last_space_index + 1:next_space]
        input_contents.append(arg)
        # If the argument isn't msg, return that erroneous input.
        if arg != "msg":
            return input_contents
        # Else, just grab the number of users to decide how many spaces to search for.
        last_space_index = next_space
        next_space = user_input.find(" ", last_space_index + 1)
        arg = user_input[last_space_index + 1:next_space]
        input_contents.append(arg)
        # Use the arg as max spaces to stop the loop at.
        max_spaces = int(arg)
        spaces_found = 0
        last_space_index = next_space
        # Loop until max spaces are found.
        while spaces_found < max_spaces:
            # Search 1 ahead of the last space, up until the next space. Add the arg to the to-be "list of usernames".
            next_space = user_input.find(" ", last_space_index + 1)
            arg = user_input[last_space_index + 1:next_space]
            input_contents[1] += "," + arg
            spaces_found += 1
            last_space_index = next_space
        # Add the remaining component
        input_contents.append(user_input[last_space_index + 1:])
    return input_contents
