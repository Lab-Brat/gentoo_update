import unittest
from unittest.mock import patch, Mock, MagicMock
import gentoo_update
from gentoo_update import create_cli, add_prefixes


class TestGentooUpdate(unittest.TestCase):
    def test_add_prefixes(self):
        input_args = "a bc"
        expected_output = "-a --bc"
        self.assertEqual(add_prefixes(input_args), expected_output)

    @patch("argparse.ArgumentParser.parse_args")
    def test_create_cli(self, mock_parse_args):
        mock_args = Mock()
        mock_parse_args.return_value = mock_args
        args = create_cli()
        self.assertEqual(args, mock_args)

    @patch("gentoo_update.gentoo_update.ShellRunner")
    @patch("argparse.ArgumentParser.parse_args")
    @patch("gentoo_update.gentoo_update.add_prefixes")
    def test_main(self, mock_add_prefixes, mock_parse_args, mock_shell_runner):
        mock_args = Mock()
        mock_args.quiet = "y"
        mock_args.update_mode = "security"
        mock_args.args = None
        mock_args.config_update_mode = "ignore"
        mock_args.daemon_restart = "n"
        mock_args.clean = "n"
        mock_args.read_logs = "n"
        mock_args.read_news = "n"
        mock_parse_args.return_value = mock_args

        mock_add_prefixes.return_value = []

        mock_shell_runner_instance = mock_shell_runner.return_value
        mock_shell_runner_instance.run_shell_script = MagicMock()

        gentoo_update.gentoo_update.main()
        mock_shell_runner_instance.run_shell_script.assert_called_once()


if __name__ == "__main__":
    unittest.main()
