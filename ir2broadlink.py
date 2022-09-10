# sonylirc2broadlink
"""
Creates broadlink b64 ir codes from a Sony lirc.conf file.
"""

import pprint
from typing import Dict
from base64 import b64encode
import struct
import requests

def pulse_to_broadlink_hex(pulse: int) -> bytearray:
    """
    Converts raw pulse length to a cycle count at about 33kHz (why not 38kHz?)
    """
    broadlink_pulse: int = int(pulse*269/8192) # Found online and tested to work
    # If the pulse fits into 1 byte, treat as is.
    # Otherwise, insert a leading 0 and split over 2 bytes big endian.
    broadlink_hex: bytearray = bytearray()
    if broadlink_pulse < 256:
        broadlink_hex.append(broadlink_pulse)
    else:
        broadlink_hex.append(0)
        # Format for struct.pack, '>H', is a big endian short (2 byte) int
        broadlink_hex += struct.pack('>H', broadlink_pulse)
    return broadlink_hex

def flatten(pulses: list[tuple[int, int]]) -> list[int]:
    """
    Flattens a list of tuples into a single list of ints
    """
    flat_list = [value for pulse in pulses for value in pulse]
    return flat_list

def pulses_to_broadlink_hex(
        pulses: list[tuple[int, int]],
        repeats: int = 0) -> bytes:
    """
    Convert a series of pules to a broadlink hex representation of the data
    """
    # [0x26] to indicate an IR code is being sent
    broadlink_hex: bytearray = bytearray([0x26])
    #This is followed by the number of repeats
    if repeats > 255:
        raise ValueError(
                'Repeats has to be less than 256 to fit in a single byte'
                )
    broadlink_hex += bytearray([repeats])
    #This will be followed by the packet length, but we don't know that yet

    #Calculate packet data
    packet: bytearray = bytearray()
    pulses = flatten(pulses)
    for pulse in pulses:
        packet += pulse_to_broadlink_hex(pulse)

    # Now calculate the packet length and add it to broadlink_hex as a 2 byte,
    # little endian number
    packet_length: int = len(packet)
    broadlink_hex += bytearray(struct.pack('<H', packet_length))
    # Finally add the packet
    broadlink_hex += packet
    return broadlink_hex

def lirc_hex_to_binary(code_hex: str, bits: int) -> list[int]:
    """
    Converts a hex code into a binary, padded to the correct number of bits
    """
    # Convert hex string to a decimal integer
    decimal_representation: int = int(code_hex, base=0)
    # Convert decimal to binary string
    binary_representation: str = f'{decimal_representation:b}'
    # pad binary string with 0s to match the number of bits
    padding_length: int = bits - len(binary_representation)
    return '0' * padding_length + binary_representation

def lirc_to_pulses(lirc_config: Dict) -> Dict:
    """
    Given an lirc config as a dictionary, convert the hex codes for
    each button into a set of timed pulses
    """
    header: dict = lirc_config['header']
    one: dict = lirc_config['one']
    zero: dict = lirc_config['zero']
    codes: dict = lirc_config['codes']
    gap: str | None = lirc_config.pop('gap', None)
    ptrail: str | None = lirc_config.pop('ptrail', None)
    flags: str | None = lirc_config.pop('flags', None)
    post_data: str | None = lirc_config.pop('post_data', None)

    button_pulses: dict = {}
    for code in codes:
        # Get the binary representation of the codes
        number_of_bits: int = int(lirc_config['bits'])
        binary_code: str = lirc_hex_to_binary(codes[code], number_of_bits)
        # Add post data bits if they exist
        if post_data:
            number_of_bits = int(lirc_config['post_data_bits'])
            binary_code += lirc_hex_to_binary(post_data, number_of_bits)
        # Start with a set of pulses for the header
        pulses: list[tuple[int, int]] = []
        pulse: tuple[int, int] = (int(header['on']), int(header['off']))
        pulses.append(pulse)

        # Now go through the binary string and add pulses
        for bit in binary_code:
            if bit == '1':
                pulse = (int(one['on']), int(one['off']))
            elif bit == '0':
                pulse = (int(zero['on']), int(zero['off']))

            pulses.append(pulse)

        # Finish with final pulse of the trail and gap
        pulse_gap: int = 0
        trail: int = 0
        if flags and 'CONST_LENGTH' in flags:
            pulse_gap = int(gap) - sum([sum(pulse_pair) for pulse_pair in pulses])
        elif gap:
            pulse_gap = int(gap)
        if ptrail:
            trail = int(ptrail)
            pulse_gap = pulse_gap - trail
            pulse = (trail, pulse_gap)
            pulses.append(pulse)
        # If there is no ptrail, add the gap to the last value in the last tuple
        else:
            final_pulse: tuple[int, int] = pulses[-1]
            pulse_gap += final_pulse[-1]
            pulses[-1] = (final_pulse[0], pulse_gap)

        button_pulses[code] = pulses

    return button_pulses

def get_conf_file(path: str) -> str:
    """
    Pulls an lirc.conf file from the given path and returns the page text
    Parameters:
    path:
        Url to the lirc.conf file
    """
    lirc_request: requests.request = requests.get(path)
    return lirc_request

def parse_lirc(text: str) -> Dict[str, str]:
    """
    Parses a string and creates a dict with the parameters of the remote
    """
    # Create an empty dict to store the configuration
    remote_config: Dict = {}

    # Read through text line by line until "begin remote" is found.
    read_line_flag: bool = False # determines whether to skip the line
    read_code_flag: bool = False # determines whether line is part of code block

    line: str
    for line in text.split('\n'):
        if line == 'begin remote':
            read_line_flag = True
            section_config: Dict = {}
            continue # Don't read in the "begin remote" line

        if line == 'end remote':
            read_line_flag = False
            remote_config[section_config.pop('name')] = section_config
            continue

        # Skip the line if read_line_flag is false
        if not read_line_flag:
            continue

        # Set code block flag
        if 'begin codes' in line:
            read_code_flag = True
            codes: Dict[str, str] = {} # setting up separate dict for the codes
            continue
        elif 'end codes' in line:
            read_code_flag = False
            section_config['codes'] = codes
            continue

        # Convert line into set of key_value pairs
        # Split by whitespace
        line_elements: list[str] = line.split()
        # If the length of the list is 0, the line is empty, so skip
        if len(line_elements) == 0:
            continue
        # If the line is part of the code block of the remote, parse seperately
        elif read_code_flag:
            codes[line_elements[0]] = line_elements[1]
        # If there are only 2 elements left, create key and value from them
        elif len(line_elements) == 2:
            section_config[line_elements[0]] = line_elements[1]
        # For 3 elements create a subdict for on and off timings
        elif len(line_elements) == 3:
            sub_dict: Dict[str, str] = {}
            sub_dict['on'] = line_elements[1]
            sub_dict['off'] = line_elements[2]
            section_config[line_elements[0]] = sub_dict
        # Else I can't parse the line. Print a warning and continue
        else:
            print(f"Couldn't parse line: {line}. Continuing to next line.")

    return remote_config

def code_to_broadlink(config: Dict) -> Dict:
    """
    Converts a parsed lirc dictionary to a dictionary mapping keys to
    base 64 broadlink codes
    """
    broadlink_map: Dict = {}
    for section in config:
        section_config: Dict = config[section]
        repeats: int = int(section_config.pop('min_repeat', 0))
        section_pulses: Dict = lirc_to_pulses(section_config)
        for button, pulses in section_pulses.items():
            broadlink_map[button] = b64encode(pulses_to_broadlink_hex(
                    pulses, repeats
                    ))
    return broadlink_map

def main(lirc_url: str) -> None:
    """
    Takes a url to an lirc config page and returns a base 64, Home Assistant
    compatible list of broadlink codes.
    """
    lirc_text: str = get_conf_file(lirc_url).text
    codes: Dict = parse_lirc(lirc_text)
    pprint.pprint(code_to_broadlink(codes))

if __name__=='__main__':
    base_url: str = 'https://sourceforge.net/p/lirc-remotes/code/ci/master/tree/remotes/'
    remote_path: str = 'sony/RM-U306A.lircd.conf'
    main(base_url + remote_path)
