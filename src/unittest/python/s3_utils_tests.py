from __future__ import print_function, absolute_import, unicode_literals, division

import unittest2 as unittest
import boto3
import os
from moto import mock_s3
from tempfile import NamedTemporaryFile

from rds_log_dog.s3_utils import (
    list_folders, get_top_level_folder_under_prefix, write_data_to_object, get_size, get_files)


class TestS3Utils(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.s3 = boto3.client('s3')

    @mock_s3
    def test_get_files(self):
        self.s3.create_bucket(Bucket='mybucket')
        self.s3.put_object(Bucket='mybucket', Key='foo/file')
        self.s3.put_object(Bucket='mybucket', Key='foo/file1')
        self.assertEqual([('foo/file', 0), ('foo/file1', 0)], get_files('mybucket', 'foo'))

    @mock_s3
    def test_list_s3_folders_on_non_existing_folder(self):
        self.s3.create_bucket(Bucket='mybucket')
        self.assertEqual(set(), list_folders(
            Bucket='mybucket', Prefix='folder1'))

    @mock_s3
    def test_list_s3_folders_on_empty_folder(self):
        self.s3.create_bucket(Bucket='mybucket')
        self.s3.put_object(Bucket='mybucket', Key='folder1/')
        self.assertEqual(set(), list_folders(
            Bucket='mybucket', Prefix='folder1'))

    @mock_s3
    def test_list_s3_folders_on_only_files(self):
        self.s3.create_bucket(Bucket='mybucket')
        self.s3.put_object(Bucket='mybucket', Key='folder1/file1')
        self.assertEqual(set(), list_folders(
            Bucket='mybucket', Prefix='folder1'))

    @mock_s3
    def test_list_s3_folders_flat(self):
        self.s3.create_bucket(Bucket='mybucket')
        self.s3.put_object(Bucket='mybucket', Key='rds_logs/folder1/file1')
        self.s3.put_object(Bucket='mybucket', Key='rds_logs/folder1/file2')
        self.s3.put_object(Bucket='mybucket', Key='rds_logs/folder2/file1')
        self.s3.put_object(Bucket='mybucket', Key='rds_logs/file1')
        self.assertEqual({'folder1', 'folder2'}, list_folders(
            Bucket='mybucket', Prefix='rds_logs'))

    @mock_s3
    def test_list_s3_folders_nested(self):
        self.s3.create_bucket(Bucket='mybucket')
        self.s3.put_object(Bucket='mybucket',
                           Key='rds_logs/folder1/subfolder1/file1')
        self.s3.put_object(Bucket='mybucket', Key='rds_logs/folder1/file2')
        self.s3.put_object(Bucket='mybucket', Key='rds_logs/folder2/file1')
        self.assertEqual({'folder1', 'folder2'}, list_folders(
            Bucket='mybucket', Prefix='rds_logs'))

    def test_get_top_level_folder_under_prefix_top_level_folder(self):
        self.assertEqual('folder1', get_top_level_folder_under_prefix(
            'rds_log/folder1/', 'rds_log'))

    def test_get_top_level_folder_under_prefix_2nd_level_folder(self):
        self.assertEqual('folder1', get_top_level_folder_under_prefix(
            'rds_log/folder1/subfolder/', 'rds_log'))

    def test_get_top_level_folder_under_prefix_2nd_level_file(self):
        self.assertEqual('folder1', get_top_level_folder_under_prefix(
            'rds_log/folder1/file', 'rds_log'))

    def test_get_top_level_folder_under_prefix_top_level_file(self):
        self.assertEqual(None, get_top_level_folder_under_prefix(
            'rds_log/folder1', 'rds_log'))

    def test_get_top_level_folder_under_prefix_with_tricky_foldername(self):
        self.assertEqual('id', get_top_level_folder_under_prefix(
            'rds_log/id/', 'rds_log'))
        self.assertEqual('rds_id', get_top_level_folder_under_prefix(
            'rds_log/rds_id/', 'rds_log'))

    # TODO/FIXME: unimplemented or wrong usage
    def test_get_top_level_folder_under_prefix_with_parent_end_w_slash(self):
        # wrong
        self.assertEqual('older1', get_top_level_folder_under_prefix(
            'rds/folder1/', 'rds/'))
        # right
        self.assertEqual(None, get_top_level_folder_under_prefix(
            'rds/folder1', 'rds/'))

    # TODO/FIXME: unimplemented or wrong usage
    def test_get_top_level_folder_under_prefix_with_no_parent(self):
        with self.assertRaises(Exception):
            self.assertEqual(None, get_top_level_folder_under_prefix(
                'rds/folder1/', None))

    @mock_s3
    def test_write_data_to_object(self):
        self.s3.create_bucket(Bucket='bucket')

        write_data_to_object('bucket', 'foo', 'mydata')

        # must not throw an exception
        self.s3.head_object(Bucket='bucket', Key='foo')

    @mock_s3
    def test_get_size(self):
        with NamedTemporaryFile() as f:
            f.write('Some Datafoo')
            file_size = os.path.getsize(f.name)
            self.s3.create_bucket(Bucket='foo')
            self.s3.put_object(
                Body=f,
                Bucket='foo',
                Key='bar'
            )
            self.assertEquals(file_size, get_size('foo', 'bar'))

if __name__ == '__main__':
    unittest.main()
