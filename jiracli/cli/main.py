#!/usr/bin/env python

# from .. import __version__

# import sys
# import logging
import jiracli.core
import jiracli.commands.issue as issue

# log = logging.getLogger("jira")

def main():
    # logger = jiracli.logging.getLogger("jira")
    # logger.setLevel(logging.INFO)
    # log.info(f"JiraCLI v{__version__}")
    # args = sys.argv[1:]
    # print('count of args :: {}'.format(len(args)))
    # for arg in args:
    #     print('passed argument :: {}'.format(arg))

    issue.list(jiracli.JIRA_CLIENT)

    # my_function('hello world')

    # my_object = MyClass('Thomas')
    # my_object.say_name()

if __name__ == '__main__':
    main()
