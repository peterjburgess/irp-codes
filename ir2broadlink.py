# sonylirc2broadlink
"""
Creates broadlink b64 ir codes from a Sony lirc.conf file.
"""

from typing import Dict
import requests
from bs4 import BeautifulSoup


def get_conf_file(path: str) -> str:
    """
    Pulls an lirc.conf file from the given path and returns the page text
    Parameters:
    path:
        Url to the lirc.conf file
    """
    r = requests.get(path)
    return r.text
#TODO separate out each remote section into it's own sub-dict
def parse_lirc(text: str) -> Dict[str, str]:
    """
    Parses a string and creates a dict with the parameters of the remote
    """
    # Create an empty dict to store the configuration
    remote_config: Dict = {}

    # DEBUG
    config_text: list[str] = []

    # Read through text line by line until "begin remote" is found.
    read_line_flag: bool = False # determines whether to skip the line
    read_code_flag: bool = False # determines whether line is part of code block

    line: str
    for line in text.split('\n'):
        if line == 'begin remote':
            read_line_flag = True
            continue # Don't read in the "begin remote" line

        if line == 'end remote':
            read_line_flag = False
            break

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
            remote_config['codes'] = codes
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
            remote_config[line_elements[0]] = line_elements[1]
        # For 3 elements create a subdict for on and off timings
        elif len(line_elements) == 3:
            sub_dict: Dict[str, str] = {}
            sub_dict['on'] = line_elements[1]
            sub_dict['off'] = line_elements[2]
            remote_config[line_elements[0]] = sub_dict
        # Else I can't parse the line. Print a warning and continue
        else:
            print(f"Couldn't parse line: {line}. Continuing to next line.")

        config_text.append(line_elements)

    return remote_config

def main(*args, **kwargs):
    lirc_text: str = get_conf_file(args[0])
    print(parse_lirc(lirc_text))

if __name__=='__main__':
    main('https://sourceforge.net/p/lirc-remotes/code/ci/master/tree/remotes/sony/RM-U306A.lircd.conf')