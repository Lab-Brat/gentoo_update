"""
This module provides functionality for updating a Gentoo Linux system.

It includes the following submodules:
- _version: contains the version number of the package
- gentoo_update: contains the main functionality for updating the system
- notifier: provides functionality for sending notifications
- parser: provides functionality for parsing command line arguments
- reporter: provides functionality for generating reports
- shell_runner: provides functionality for running shell commands
"""

from ._version import __version__
from .gentoo_update import add_prefixes, create_cli, main
from .notifier import Notifier
from .parser import Parser
from .reporter import Reporter
from .shell_runner import ShellRunner
