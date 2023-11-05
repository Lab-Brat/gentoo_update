"""Unit tests for gentoo_update.py (main) file."""

import unittest
from unittest.mock import Mock, patch

from gentoo_update import create_cli


class TestGentooUpdate(unittest.TestCase):
    """Unit tests for functions in the gentoo_update module."""

    @patch("argparse.ArgumentParser.parse_args")
    def test_create_cli(self, mock_parse_args):
        """Test if the create_cli function returns the mocked arguments."""
        mock_args = Mock()
        mock_parse_args.return_value = mock_args
        args = create_cli()
        self.assertEqual(args, mock_args)


if __name__ == "__main__":
    unittest.main()
