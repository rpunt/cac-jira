# pylint: disable=missing-docstring

import abc
import glob
import os

# Dynamically find all Python files in the current directory (excluding __init__.py)
module_files = glob.glob(os.path.join(os.path.dirname(__file__), "*.py"))
module_names = [
    os.path.splitext(os.path.basename(f))[0]
    for f in module_files
    if os.path.basename(f) != "__init__.py"
]

# Import all modules dynamically
__all__ = module_names

class IssueCommand(abc.ABC):
    """
    A base class for all issue-related commands.

    This class provides shared functionality and structure for all commands
    in the 'issue' module, including default arguments.
    """

    @abc.abstractmethod
    def execute(self, args):
        """
        Abstract method that must be implemented by all subclasses.

        Args:
            args (argparse.Namespace): Parsed command-line arguments.

        Returns:
            None
        """
        pass # pylint: disable=unnecessary-pass

    @classmethod
    def define_arguments(cls, parser):
        """
        Defines default arguments for all issue-related commands.

        Args:
            parser (argparse.ArgumentParser): The argument parser to define arguments for.

        Returns:
            None
        """
        parser.add_argument(
            "-p", "--project", help="Filter issues by project key", default="CRDBOPS"
        )
