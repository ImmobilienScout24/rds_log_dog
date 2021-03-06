from __future__ import print_function, absolute_import, division

import unittest2 as unittest
from moto import mock_rds
from rds_log_dog.discoverer import Discoverer


class Test(unittest.TestCase):

    @mock_rds
    def test_discoverer_with_no_rds_instances(self):
        disco = Discoverer()
        disco_result = disco.discover()
        self.assertEqual(
            [], disco_result,
            "count rds-instances should be 0 in moto-mock env and from type list")

if __name__ == '__main__':
    unittest.main()
