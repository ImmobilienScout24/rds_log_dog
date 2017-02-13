from __future__ import print_function, absolute_import, unicode_literals, division

import unittest2 as unittest
import boto3
import moto
from pprint import pprint
from rds_log_dog.cfn_utils import cfn_get_output

try:
  import _fix_moto as fix
  fix.unset_http_proxy()
except:
  pass


class Test(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.s3 = boto3.client('s3')

    @moto.mock_cloudformation
    def test_cfn_get_output(self):
        client = boto3.client('cloudformation')
        response = client.create_stack(
            StackName='foo',
            TemplateBody="""
{
  "AWSTemplateFormatVersion": "2010-09-09",
  "Description": "An s3 bucket",
  "Resources": {
    "bucket": {
      "Type": "AWS::S3::Bucket",
      "Properties" : {
        "BucketName": "MyBucketName"
    }}
  },
  "Outputs": {
    "name": {
      "Description": "name of destination log bucket",
      "Value": {"Ref": "bucket"}
    }
  }
} """)
        self.assertTrue('StackId' in response)
        self.assertEqual('MyBucketName', cfn_get_output(
            response['StackId'], 'name'))


if __name__ == '__main__':
    unittest.main()
