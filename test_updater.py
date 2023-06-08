import unittest
from unittest import mock
from gentoo_update import create_logger, add_prefixes, run_shell_script


class TestGentooUpdate(unittest.TestCase):

    @mock.patch('gentoo_update.os.path.exists', return_value=False)
    @mock.patch('gentoo_update.os.mkdir')
    def test_create_logger(self, mock_mkdir, mock_exists):
        logger, log_file = create_logger()
        self.assertTrue(mock_mkdir.called)
        self.assertEqual(logger.level, 20)

if __name__ == '__main__':
    unittest.main()

