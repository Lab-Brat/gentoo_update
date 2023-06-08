import unittest
from unittest import mock
from gentoo_update import create_logger, add_prefixes, run_shell_script


class TestGentooUpdate(unittest.TestCase):
    @mock.patch("gentoo_update.gentoo_update.os.path.exists", return_value=False)
    @mock.patch("gentoo_update.gentoo_update.os.mkdir")
    def test_create_logger(self, mock_mkdir, _):
        logger, _ = create_logger()
        self.assertTrue(mock_mkdir.called)
        self.assertEqual(logger.level, 20)

    def test_add_prefixes(self):
        input_args = ["a", "bc"]
        expected_output = ["-a", "--bc"]
        self.assertEqual(add_prefixes(input_args), expected_output)

    @mock.patch("gentoo_update.gentoo_update.subprocess.Popen")
    @mock.patch(
        "gentoo_update.gentoo_update.create_logger", return_value=(mock.Mock(), "log_file")
    )
    @mock.patch("gentoo_update.gentoo_update.shlex.split")
    def test_run_shell_script(self, mock_split, _, mock_popen):
        # mocking the split, logger and popen calls
        mock_process = mock.Mock()
        mock_process.returncode = 0
        mock_process.stdout = [b"test output\n"]
        mock_process.stderr = [b"test error\n"]
        mock_popen.return_value.__enter__.return_value = mock_process
        run_shell_script("arg1", "arg2")
        self.assertTrue(mock_split.called)
        self.assertTrue(mock_popen.called)


if __name__ == "__main__":
    unittest.main()
