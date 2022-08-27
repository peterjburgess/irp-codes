from email.utils import parsedate
import unittest
import ir2broadlink

class TestLircRetrieval(unittest.TestCase):
    
    # Set up with a get request to a lirc conf file
    def setUp(self):
        self.r = ir2broadlink.get_conf_file(
            'https://sourceforge.net/p/lirc-remotes' \
            '/code/ci/master/tree/remotes/sony/RM-U306A.lircd.conf'
            )

    # Ensure that requests is working and can access the lirc database
    def test_200_response(self):
        self.assertEqual(self.r.status_code, 200)

class TestLircToPulseConversion(unittest.TestCase):

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
            (600, 600), (0, 0)
            ],
            'TEST_CODE_2': [(2400, 600), (1200, 600), (600, 600), (1200, 600),
            (600, 600), (1200, 600), (600, 600), (600, 600), (600, 600), 
            (600, 600), (600, 600), (600, 600), (1200, 600), (1200, 600),
            (600, 600), (600, 600), (0, 0)
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

    # Ensure that the simple code correctly converts to binary
    def test_simple_binary_conversion(self):
        for code in self.simple_code['codes']:
            parsed_binary_code = ir2broadlink.lirc_hex_to_binary(
                code_hex=self.simple_code['codes'][code], 
                bits=self.simple_code['bits'])
            correct_binary_code = self.correct_simple_codes[code]
            self.assertEqual(parsed_binary_code, correct_binary_code)

    def test_simple_pulse_conversion(self):
        pulses = ir2broadlink.lirc_to_pulses(self.simple_code)
        self.assertEqual(pulses, self.correct_simple_pulses)

    def test_code_trail_binary_converstion(self):
        for code in self.code_with_trail['codes']:
            parsed_binary_code = ir2broadlink.lirc_hex_to_binary(
                code_hex=self.code_with_trail['codes'][code], 
                bits=self.code_with_trail['bits'])
            correct_binary_code = self.correct_trail_codes[code]
            self.assertEqual(parsed_binary_code, correct_binary_code)

    def test_trail_pulse_conversion(self):
        pulses = ir2broadlink.lirc_to_pulses(self.code_with_trail)
        self.assertEqual(pulses, self.correct_trail_pulses)
        #self.assertEqual(pulses['TEST_CODE_1'], self.correct_trail_pulses['TEST_CODE_1'])



if __name__ == '__main__':
    unittest.main()
