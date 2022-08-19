# sonylirc2broadlink
"""
Creates broadlink b64 ir codes from a Sony lirc.conf file.
"""

from typing import Dict
import requests

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

    button_pulses: dict = {}
    for code in codes:
        # Get the binary representation of the codes
        number_of_bits = int(lirc_config['bits'])
        binary_code: str = lirc_hex_to_binary(codes[code], number_of_bits)
        # Start with a set of pulses for the header
        pulses: list[tuple[int, int]] = []
        pulse = (int(header['on']), int(header['off']))
        pulses.append(pulse)
            
        # Now go through the binary string and add pulses
        for bit in binary_code:
            if bit == '1':
                pulse = (int(one['on']), int(one['off']))
            elif bit == '0':
                pulse = (int(zero['on']), int(zero['off']))

            pulses.append(pulse)
        
        button_pulses[code] = pulses
                    
    return button_pulses

def get_conf_file(path: str) -> str:
    """
    Pulls an lirc.conf file from the given path and returns the page text
    Parameters:
    path:
        Url to the lirc.conf file
    """
    r = requests.get(path)
    return r

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

def main(*args, **kwargs):
    lirc_text: str = get_conf_file(args[0]).text
    print(parse_lirc(lirc_text))
    print(lirc_hex_to_binary('0x2A06', 14))

if __name__=='__main__':
    main('https://sourceforge.net/p/lirc-remotes/code/ci/master/tree/remotes/sony/RM-U306A.lircd.conf')