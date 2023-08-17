import unittest
from unittest.mock import patch, Mock
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


if __name__ == "__main__":
    unittest.main()
