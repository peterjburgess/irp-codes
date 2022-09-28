"""Test suite for the lirc to broadlink ir codes conversion module"""
import unittest
import ir2broadlink

class TestLircRetrieval(unittest.TestCase):
    """Tests that the LIRC configuration file is retrieved correctly"""
    # Set up with a get request to a lirc conf file
    def setUp(self):
        self.response = ir2broadlink.get_conf_file(
            'https://sourceforge.net/p/lirc-remotes' \
            '/code/ci/master/tree/remotes/sony/RM-U306A.lircd.conf'
            )

    # Ensure that requests is working and can access the lirc database
    def test_200_response(self):
        """Test that url of a known configuration file gives a 200 response"""
        self.assertEqual(self.response.status_code, 200)

class TestLircToPulseConversion(unittest.TestCase):
    """Test that code correctly converts LIRC files to pulses"""

    def setUp(self):
        self.simple_code = {
            'bits': 15,
            'header': {
                'on': '2400',
                'off': '600'
            },
            'one': {
                'on': '1200',
                'off': '600',
            },
            'zero': {
                'on': '600',
                'off': '600'
            },
            'codes': {
                'TEST_CODE_1': '0x30C',
                'TEST_CODE_2': '0x540C'
            }
        }
        self.correct_simple_codes = {
            'TEST_CODE_1': '000001100001100',
            'TEST_CODE_2': '101010000001100'
        }
        self.correct_simple_pulses = {
            'TEST_CODE_1': [(2400, 600), (600, 600), (600, 600), (600, 600),
            (600, 600), (600, 600), (1200, 600), (1200, 600), (600, 600), (600,
            600), (600, 600), (600, 600), (1200, 600), (1200, 600), (600, 600),
            (600, 600)
            ],
            'TEST_CODE_2': [(2400, 600), (1200, 600), (600, 600), (1200, 600),
            (600, 600), (1200, 600), (600, 600), (600, 600), (600, 600),
            (600, 600), (600, 600), (600, 600), (1200, 600), (1200, 600),
            (600, 600), (600, 600)
            ]
        }

        self.code_with_trail = {
            'bits': 14,
            'flags': 'CONST_LENGTH',
            'header': {
                'on': '2400',
                'off': '600'
            },
            'one': {
                'on': '1200',
                'off': '600',
            },
            'zero': {
                'on': '600',
                'off': '600'
            },
            'ptrail': '600',
            'gap': '45000',
            'codes': {
                'TEST_CODE_1': '0x186',
                'TEST_CODE_2': '0x2A06'
            }
        }
        self.correct_trail_codes = {
            'TEST_CODE_1': '00000110000110',
            'TEST_CODE_2': '10101000000110'
        }
        self.correct_trail_pulses = {
            'TEST_CODE_1': [(2400, 600), (600, 600), (600, 600), (600, 600),
            (600, 600), (600, 600), (1200, 600), (1200, 600), (600, 600), (600,
            600), (600, 600), (600, 600), (1200, 600), (1200, 600), (600, 600),
            (600, 22200)
            ],
            'TEST_CODE_2': [(2400, 600), (1200, 600), (600, 600), (1200, 600),
            (600, 600), (1200, 600), (600, 600), (600, 600), (600, 600),
            (600, 600), (600, 600), (600, 600), (1200, 600), (1200, 600),
            (600, 600), (600, 21600)
            ]
        }

        self.code_without_trail = {
            'bits': 15,
            'flags' : 'CONST_LENGTH',
            'header': {
                'on': '2400',
                'off': '600'
            },
            'one': {
                'on': '1200',
                'off': '600',
            },
            'zero': {
                'on': '600',
                'off': '600'
            },
            'gap': '45000',
            'codes': {
                'TEST_CODE_1': '0x410D',
                'TEST_CODE_2': '0x3B0D'
            }

        }
        self.correct_no_trail_codes = {
            'TEST_CODE_1': '100000100001101',
            'TEST_CODE_2': '011101100001101'
        }
        self.correct_no_trail_pulses = {
            'TEST_CODE_1': [(2400, 600), (1200, 600), (600, 600), (600, 600),
            (600, 600), (600, 600), (600, 600), (1200, 600), (600, 600), (600,
            600), (600, 600), (600, 600), (1200, 600), (1200, 600), (600, 600),
            (1200, 21600)
            ],
            'TEST_CODE_2': [(2400, 600), (600, 600), (1200, 600), (1200, 600),
            (1200, 600), (600, 600), (1200, 600), (1200, 600), (600, 600),
            (600, 600), (600, 600), (600, 600), (1200, 600), (1200, 600),
            (600, 600), (1200, 19800)
            ]
        }

        self.code_with_post_data = {
            'bits': 6,
            'flags' : 'CONST_LENGTH',
            'header': {
                'on': '2400',
                'off': '600'
            },
            'one': {
                'on': '1200',
                'off': '600',
            },
            'zero': {
                'on': '600',
                'off': '600'
            },
            'gap': '45000',
            'ptrail': '1200',
            'post_data_bits': '8',
            'post_data': '0x86',
            'codes': {
                'TEST_CODE_1': '0x13',
                'TEST_CODE_2': '0x33'
            }

        }
        self.correct_post_data_codes = {
            'TEST_CODE_1': '010011',
            'TEST_CODE_2': '110011'
        }
        self.correct_post_data_pulses = {
            'TEST_CODE_1': [(2400, 600), (600, 600), (1200, 600), (600, 600),
            (600, 600), (1200, 600), (1200, 600), (1200, 600), (600, 600), (600,
            600), (600, 600), (600, 600), (1200, 600), (1200, 600), (600, 600),
            (1200, 20400)
            ],
            'TEST_CODE_2': [(2400, 600), (1200, 600), (1200, 600), (600, 600),
            (600, 600), (1200, 600), (1200, 600), (1200, 600), (600, 600), (600,
            600), (600, 600), (600, 600), (1200, 600), (1200, 600), (600, 600),
            (1200, 19800)
            ]
        }
    # Ensure that the simple code correctly converts to binary
    def test_simple_binary_conversion(self):
        """Test that simple lirc config correctly converts to binary"""
        for code in self.simple_code['codes']:
            parsed_binary_code = ir2broadlink.lirc_hex_to_binary(
                code_hex=self.simple_code['codes'][code],
                bits=self.simple_code['bits'])
            correct_binary_code = self.correct_simple_codes[code]
            self.assertEqual(parsed_binary_code, correct_binary_code)

    def test_simple_pulse_conversion(self):
        """Test that simple lirc config correctly converts to pulses"""
        pulses = ir2broadlink.lirc_to_pulses(self.simple_code)
        self.assertEqual(pulses, self.correct_simple_pulses)

    def test_code_trail_binary_conversion(self):
        """Test that lirc config with a ptrail correctly converts to binary"""
        for code in self.code_with_trail['codes']:
            parsed_binary_code = ir2broadlink.lirc_hex_to_binary(
                code_hex=self.code_with_trail['codes'][code],
                bits=self.code_with_trail['bits'])
            correct_binary_code = self.correct_trail_codes[code]
            self.assertEqual(parsed_binary_code, correct_binary_code)

    def test_trail_pulse_conversion(self):
        """Test that lirc config with a ptrail correctly converts to pulses"""
        pulses = ir2broadlink.lirc_to_pulses(self.code_with_trail)
        self.assertEqual(pulses, self.correct_trail_pulses)

    def test_no_trail_binary_conversion(self):
        """Test that lirc config without ptrail correctly converts to binary"""
        for code in self.code_without_trail['codes']:
            parsed_binary_code = ir2broadlink.lirc_hex_to_binary(
                code_hex=self.code_without_trail['codes'][code],
                bits=self.code_without_trail['bits']
            )
            correct_binary_code = self.correct_no_trail_codes[code]
            self.assertEqual(parsed_binary_code, correct_binary_code)

    def test_no_trail_pulse_conversion(self):
        """Test that lirc config without ptrail correctly converts to pulses"""
        pulses = ir2broadlink.lirc_to_pulses(self.code_without_trail)
        self.assertEqual(pulses, self.correct_no_trail_pulses)

    def test_post_data_binary_conversion(self):
        """Test that lirc config with post data correctly converts to binary"""
        for code in self.code_with_post_data['codes']:
            parsed_binary_code = ir2broadlink.lirc_hex_to_binary(
                code_hex=self.code_with_post_data['codes'][code],
                bits=self.code_with_post_data['bits']
            )
            correct_binary_code = self.correct_post_data_codes[code]
            self.assertEqual(parsed_binary_code, correct_binary_code)

    def test_post_data_pulse_conversion(self):
        """Test that lirc config with post data correctly converts to pulses"""
        pulses = ir2broadlink.lirc_to_pulses(self.code_with_post_data)
        self.assertEqual(pulses, self.correct_post_data_pulses)

class TestPulseToBroadlinkHexConversion(unittest.TestCase):
    """Tests for converting pulses to Broadlink valid hex"""

    def test_list_flatten(self):
        """Tests that list of tuples correctly flattens to list of ints"""
        pulses = [(40, 40), (80, 40), (40, 40), (40, 3600)]
        flat_list = [40, 40, 80, 40, 40, 40, 40, 3600]
        self.assertEqual(ir2broadlink.flatten(pulses), flat_list)

    def test_pulse_to_broadlink_hex_single_byte(self):
        """
        Tests that pulse that fits into single byte correctly converts to
        Broadlink hex
        """
        # Broadlink hex value for 1000 microseconds
        single_byte_test = bytearray([0x20])
        self.assertEqual(
                single_byte_test,
                ir2broadlink.pulse_to_broadlink_hex(1000)
                )

    def test_pulse_to_broadlink_hex_multi_byte(self):
        """
        Tests that pulse that doesn't fit into single bye correctly converts
        to Broadlink hex
        """
        # Broadlink hex value for 50,000 microseconds
        multi_byte_test = bytearray([0x00, 0x06, 0x69])
        self.assertEqual(
                multi_byte_test,
                ir2broadlink.pulse_to_broadlink_hex(50000)
                )

    def test_pulse_to_broadlink_hex(self):
        """Tests that pulse array correctly converts to Broadlink hex"""
        pulses = [(2400, 600), (1200, 600), (600, 600), (600, 21600)]
        correct_broadlink_hex = bytearray(
                [ 0x26, 0x00, 0x0a, 0x00, 0x4E, 0x13, 0x27, 0x13, 0x13, 0x13,
                    0x13, 0x00, 0x02, 0xC5 ]
                )
        self.assertEqual(
                ir2broadlink.pulses_to_broadlink_hex(pulses),
                correct_broadlink_hex
                )


if __name__ == '__main__':
    unittest.main()
