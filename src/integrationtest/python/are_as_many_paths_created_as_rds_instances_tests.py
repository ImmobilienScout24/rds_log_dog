from __future__ import print_function, absolute_import, unicode_literals, division

import unittest2 as unittest
import os, re
from util import execute_command
from cfn_utils import get_output

class Test(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        with open('target/FUNCTION_STACK_NAME','r') as f:
                self.function_stack_name = f.read().strip()

        with open('target/DST_BUCKET_STACK_NAME','r') as f:
                self.bucket_stack_name = f.read().strip()

        self.lambda_function_name = get_output(self.function_stack_name, 'name')
        self.bucket_name = get_output(self.bucket_stack_name , 'name')
       
    def test_no_s3_rds_logs_equals_rds_instances(self):
        return_code, std_out, std_err = execute_command('aws s3 ls {}/rds_logs/'.format(self.bucket_name))
        out = std_out.splitlines()
        result = [ line for line in out if re.match("^\s*PRE\s+", line) ]

        # discover # of rds instances
        import boto3
        client = boto3.client('rds')
        response = client.describe_db_instances()

        self.assertEqual(len(response['DBInstances']), len(result), "number of rds instances doesn't match number of folders in rds_logs/")

if __name__ == '__main__':
    unittest.main()
