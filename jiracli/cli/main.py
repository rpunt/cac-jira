#!/usr/bin/env python
# pylint: disable=line-too-long

"""
Main entry point for the Jira CLI tool.

This script provides a command-line interface for interacting with Jira. It supports
various subcommands, such as 'issue', and dynamically loads the appropriate modules
and actions based on user input. The tool is designed to be extensible, allowing
additional subcommands and actions to be added as needed.
"""

import argparse
import importlib
import sys
import logging
import cac_core as cac


def main():
    """
    Entry point for the Jira CLI tool.

    This function sets up the argument parser, handles subcommands, and dynamically
    loads and executes the appropriate module and action based on user input.

    It supports subcommands like 'issue' and allows each subcommand to define its
    own arguments and actions. Errors during module loading or execution are logged.
    """
    log = cac.logger.new(__name__)
    parser = argparse.ArgumentParser(prog="jira", description="Jira CLI tool")
    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    # Define the 'issue' subcommand
    issue_parser = subparsers.add_parser("issue", help="Issue-related commands")
    issue_parser.add_argument("action", help="Action to perform (e.g., list, create)")
    issue_parser.add_argument("--verbose", help="Verbose output", action="store_true", default=False)

    args, remaining_args = parser.parse_known_args()

    if not args.subcommand:
        parser.print_help()
        sys.exit(1)
    if args.verbose:
        log.setLevel(logging.DEBUG)

    # Dynamically load the subcommand module and call the corresponding action

    try:
        module_path = f"jiracli.commands.{args.subcommand}.{args.action}"
        log.debug("Attempting to import module: %s", module_path)
        module = importlib.import_module(module_path)
        log.debug("Successfully imported module: %s", module_path)

        # Convert action to PascalCase for class name (e.g., "list" -> "IssueList")
        class_name = f"{args.subcommand.capitalize()}{args.action.capitalize()}"
        log.debug("Determined class name: %s", class_name)

        # Load the subcommand class
        log.debug("Loading subcommand class from module: %s", module_path)
        subcommand_class = getattr(module, class_name, None)
        if subcommand_class is None:
            raise AttributeError(
                f"Class '{class_name}' not found in module '{module_path}'"
            )

        # Instantiate the subcommand class
        log.debug("Instantiating subcommand class: %s", class_name)
        subcommand_instance = subcommand_class()

        # Let the subcommand class define its own arguments
        log.debug("Initializing argument parser for: %s %s", args.subcommand, args.action)
        subcommand_parser = argparse.ArgumentParser(
            prog=f"jira {args.subcommand} {args.action}"
        )
        log.debug("Calling 'define_arguments' for: %s %s", args.subcommand, args.action)
        subcommand_instance.define_arguments(subcommand_parser)
        log.debug("Parsing arguments for: %s %s", args.subcommand, args.action)
        subcommand_args = subcommand_parser.parse_args(remaining_args)
        if not isinstance(subcommand_args, argparse.Namespace):
            raise TypeError("Parsed arguments must be an instance of argparse.Namespace")

        # Call the execute method of the subcommand class with parsed arguments
        log.debug("Executing action method: %s.execute", class_name)
        subcommand_instance.execute(subcommand_args)
    except ModuleNotFoundError:
        log.error("Error: Command module '%s' not found.", module_path)
    except AttributeError as e:
        log.error("Error: %s", e)
    except Exception as e: # pylint: disable=broad-except
        log.error("Unexpected error: %s", e)
        # import traceback
        # traceback.print_exc()


if __name__ == "__main__":
    main()
