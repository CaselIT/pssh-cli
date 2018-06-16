from pssh.clients import ParallelSSHClient
from typing import List

from command_file import Command, getCommands
from host_file import getHostConfig


class Runner:
    def __init__(self, args):
        if args.hostName:
            self.client = ParallelSSHClient(list(args.hostName), timeout=args.timeout)
            self.hostConfig = None
        else:
            self.hostConfig = getHostConfig(args.hostFile)
            self.client = ParallelSSHClient(
                list(self.hostConfig.keys()), host_config=self.hostConfig, timeout=args.timeout)

    def runCommand(self, command, sudo, consumeOutput, logExit=True):
        output = self.client.run_command(command, sudo=sudo)
        if sudo and self.hostConfig:
            for host in output:
                if (host in self.hostConfig
                        and self.hostConfig[host].get('sudoRequiresPassword', False)
                        and self.hostConfig[host].get('password', False)):
                    stdin = output[host].stdin
                    pwd = self.hostConfig[host]['password']
                    stdin.write(f'{pwd}\n')
                    stdin.flush()
        self.client.join(output, consume_output=consumeOutput)
        if logExit:
            for host, hostOutput in output.items():
                print(f'[Host {host}] exit code: {hostOutput.exit_code}')
        return output

    def runCommandList(self, commandList: List[Command], verbose):
        for command in commandList:
            if verbose:
                print(f'Running command {command.name}')
            output = self.runCommand(command.commad, command.sudo, verbose, False)
            if command.abortOnError:
                for host, hostOutput in output.items():
                    if hostOutput.exit_code:
                        print(f'[{host}] command {command.name} exited with',
                              f'error {hostOutput.exit_code}.',
                              'No further commands will be executed.')
                        self.client.hosts.remove(host)


def setLogger(args):
    if args.quiet:
        return
    from logging import Filter, LogRecord
    from pssh.utils import enable_host_logger, host_logger

    class SudoFilter(Filter):
        _SUDO_MSG = '[sudo] password for'

        def filter(self, record: LogRecord):
            msg = record.getMessage()
            return self._SUDO_MSG not in msg

    enable_host_logger()
    host_logger.addFilter(SudoFilter())


def main(args):
    setLogger(args)
    runner = Runner(args)

    if args.command:
        runner.runCommand(args.command, args.sudo, not args.quiet)
    elif args.commandFile:
        commands = getCommands(args.commandFile)
        runner.runCommandList(commands, not args.quiet)


def cli():
    from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser, FileType
    parser = ArgumentParser(
        formatter_class=ArgumentDefaultsHelpFormatter, description='Run ssh commands in parallel')

    hostGroup = parser.add_mutually_exclusive_group(required=True)
    hostGroup.add_argument('-f', '--hostFile', help='The host file to use', type=FileType())
    hostGroup.add_argument('-n', '--hostName', help='The host names to use', nargs='+')

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

    return parser


if __name__ == '__main__':
    parser = cli()
    args = parser.parse_args()
    main(args)
