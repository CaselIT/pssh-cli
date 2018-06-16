from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser, FileType


def getCli():
    parser = ArgumentParser(
        formatter_class=ArgumentDefaultsHelpFormatter, description='Run ssh commands in parallel')

    hostGroup = parser.add_mutually_exclusive_group(required=True)
    hostGroup.add_argument('-f', '--hostFile', help='The host file to use', type=FileType())
    hostGroup.add_argument('-n', '--hostNames', help='The host names to use', nargs='+')

    commandGroup = parser.add_mutually_exclusive_group(required=True)
    commandGroup.add_argument('command', help='The command to use', nargs='?')
    commandGroup.add_argument(
        '-c', '--commandFile', help='A file with the commands to execute', type=FileType())
    parser.add_argument('-q', '--quiet', help='Do not log the output', action='store_true')
    parser.add_argument(
        '-s',
        '--sudo',
        help='Execute command as sudo. Ignore when a commandFile is used',
        action='store_true')
    parser.add_argument('-t', '--timeout', help='Timeout for the commands', type=float, default=10)
    parser.add_argument('--noColour', help='Disable colour output', action='store_true')
    return parser
