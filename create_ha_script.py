"""
create_ha_scripts.py

Creates a yaml file with Home Assistant valid scripts for every remote button
provided in the dictionary input.
"""

import yaml

from sys import argv
from lirc2broadlinkha import create_mapping

def create_script(button: str, code:str, entity_name: str) -> dict:
    """
    Creates a Home Assistant script that maps a button to it's corresponding
    base 64 code
    """

    # First sanitize the button name. Must be lower case without any dashes
    button_name: str = button.lower().replace('-', '_')
    
    # Build the Home Assistant script
    script: dict = {
        button_name: {
            'alias': button,
            'sequence': [
                {
                    'service': 'remote.send_command',
                    'target': {
                        'entity_id': entity_name
                        },
                    'data': {
                        'command': f'b64:{code}'
                        }
                    }
                ]
            }
        }
    return script
    

def main(lirc_url: str, entity_name: str, outfile: str | None = None) -> None:

    mapping = create_mapping(argv[1])
    script_file_string: str = ''
    for button, code in mapping.items():
        script: dict = create_script(button, code, entity_name)
        script_file_string += yaml.dump(script)
        script_file_string += '\n'


    if outfile:
        if outfile.split('.')[-1] not in ['yaml', 'yml']:
            raise ValueError('File must be a .yaml file')
        with open(outfile, 'w') as yaml_file:
            yaml_file.write(script_file_string)
    else:
        print(script_file_string)

if __name__ == '__main__':
    lirc_url: str = argv[1]
    entity_name: str = argv[2]
    outfile: str | None = None

    # Allow for entity name to either include remote. prefix or not
    if entity_name.split('.')[0] != 'remote':
        entity_name = f'remote.{entity_name}'

    # Check for existence of outfile argument
    if len(argv) > 2:
        outfile = argv[3]

    main(lirc_url, entity_name, outfile)
