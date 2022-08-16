import unittest
import ir2broadlink

class TestLircRetrieval(unittest.TestCase):
    
    # Set up with a get request to a lirc conf file
    def setUp(self):
        self.r = ir2broadlink.get_conf_file('https://sourceforge.net/p/lirc-remotes/code/ci/master/tree/remotes/sony/RM-U306A.lircd.conf')

    # Ensure that requests is working and can access the lirc database
    def test_200_response(self):
        self.assertEqual(self.r.status_code, 200)

if __name__ == '__main__':
    unittest.main()
