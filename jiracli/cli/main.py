#!/usr/bin/env python
# pylint: disable=line-too-long

"""
Main entry point for the Jira CLI tool.

This script provides a command-line interface for interacting with Jira. It supports
nested commands, such as 'jira issue list' or 'jira project create', and dynamically
loads the appropriate modules and actions based on user input. The tool is designed to be
extensible, allowing additional commands to be added as needed.
"""

import argparse
import importlib
import sys
import logging
import cac_core as cac


def main():
    """
    Entry point for the Jira CLI tool.

    This function sets up the argument parser with nested commands, and dynamically
    loads and executes the appropriate module and action based on user input.

    It supports command patterns like 'jira issue list' or 'jira project create' and allows
    each command to define its own arguments and actions. Errors during module loading
    or execution are logged.
    """
    log = cac.logger.new(__name__)

    # Create parent parser for global arguments
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument("--verbose", help="Verbose output", action="store_true", default=False)

    # Main parser that inherits from parent
    parser = argparse.ArgumentParser(prog="jira", description="Jira CLI tool", parents=[parent_parser])
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Define top-level commands - pass parent_parser to inherit global arguments
    issue_parser = subparsers.add_parser("issue", help="Issue-related commands", parents=[parent_parser])
    issue_subparsers = issue_parser.add_subparsers(dest="action", required=True)

    # Define issue actions with empty parsers - the actual arguments will be added by the command classes
    issue_list_parser = issue_subparsers.add_parser("list", help="List issues", parents=[parent_parser])
    issue_create_parser = issue_subparsers.add_parser("create", help="Create an issue", parents=[parent_parser])

    # Example of another top-level command - pass parent_parser to inherit global arguments
    project_parser = subparsers.add_parser("project", help="Project-related commands", parents=[parent_parser])
    project_subparsers = project_parser.add_subparsers(dest="action", required=True)

    # Define project actions with empty parsers - the actual arguments will be added by the command classes
    project_list_parser = project_subparsers.add_parser("list", help="List projects", parents=[parent_parser])
    project_create_parser = project_subparsers.add_parser("create", help="Create a project", parents=[parent_parser])

    # First parse just the command and action to determine which action class to load
    args, unknown = parser.parse_known_args()
    if args.verbose:
        log.setLevel(logging.DEBUG)

    command = args.command
    action = getattr(args, 'action', None)

    if not action:
        log.error("No action specified for '%s'", command)
        sys.exit(1)

    # Dynamically load the command module and call the corresponding action
    try:
        module_path = f"jiracli.commands.{command}.{action}"
        log.debug("Attempting to import module: %s", module_path)
        module = importlib.import_module(module_path)
        log.debug("Successfully imported module: %s", module_path)

        # Convert command and action to PascalCase for class name (e.g., "issue" "list" -> "IssueList")
        class_name = f"{command.capitalize()}{action.capitalize()}"
        log.debug("Determined class name: %s", class_name)

        # Load the action class
        log.debug("Loading action class from module: %s", module_path)
        action_class = getattr(module, class_name, None)
        if action_class is None:
            raise AttributeError(
                f"Class '{class_name}' not found in module '{module_path}'"
            )

        # Instantiate the action class
        log.debug("Instantiating action class: %s", class_name)
        action_instance = action_class()

        # Now add the command-specific arguments to the appropriate parser
        if command == "issue" and action == "list":
            action_instance.define_arguments(issue_list_parser)
        elif command == "issue" and action == "create":
            action_instance.define_arguments(issue_create_parser)
        elif command == "project" and action == "list":
            action_instance.define_arguments(project_list_parser)
        elif command == "project" and action == "create":
            action_instance.define_arguments(project_create_parser)

        # Now parse all arguments with the updated parser
        args = parser.parse_args()
        if args.verbose:
            log.setLevel(logging.DEBUG)

        # Execute the action with the fully parsed arguments
        log.debug("Executing action method: %s.execute", class_name)
        action_instance.execute(args)
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
