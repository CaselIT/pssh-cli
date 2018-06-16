from colorama import Fore
from concurrent.futures import ThreadPoolExecutor
from pssh.clients import ParallelSSHClient
from pssh.output import HostOutput
from typing import List, Dict

from command_file import Command
from host_file import getHostConfig
from utils import Log


class Runner:
    def __init__(self, timeout, log: Log, hostNames=None, hostFile=None, quiet=False):
        if hostFile and hostNames:
            raise ValueError('Cannot specify both "hostNames" and "hostFile"')
        elif hostNames:
            self.client = ParallelSSHClient(list(hostNames), timeout=timeout)
            self.hostConfig = None
        elif hostFile:
            self.hostConfig = getHostConfig(hostFile)
            self.client = ParallelSSHClient(
                list(self.hostConfig.keys()), host_config=self.hostConfig, timeout=timeout)
        else:
            raise ValueError('One of "hostNames" or "hostFile" is required')
        self.quiet = quiet
        self.log = log
        self.pool = ThreadPoolExecutor()
        self.justification = max(
            len(self._hostName(host)) for host in (hostNames or self.hostConfig.keys()))

    def runCommand(self, command, sudo, consumeOutput=None, logExit=True):
        consumeOutput = not self.quiet if consumeOutput is None else consumeOutput
        output = self.client.run_command(command, sudo=sudo)
        if sudo and self.hostConfig:
            for host in output:
                if (self.hostConfig[host].get('sudoRequiresPassword', False)
                        and self.hostConfig[host].get('password', False)):
                    stdin = output[host].stdin
                    pwd = self.hostConfig[host]['password']
                    stdin.write(f'{pwd}\n')
                    stdin.flush()
        if consumeOutput:
            self._logCommand(output)
        self.client.join(output, consume_output=True)
        if logExit:
            for host, hostOutput in output.items():
                self._print(host, f'exit code: {hostOutput.exit_code}')
        return output

    def runCommandList(self, commandList: List[Command], verbose=None):
        verbose = not self.quiet if verbose is None else verbose
        for command in commandList:
            if verbose:
                self.log(self.log.colour(Fore.GREEN, f'Running command {command.name}'))
            output = self.runCommand(command.commad, command.sudo, verbose, False)
            if command.abortOnError:
                for host, hostOutput in output.items():
                    if hostOutput.exit_code:
                        text = (f'command {command.name} exited with error {hostOutput.exit_code}.',
                                'No further commands will be executed.')
                        self._print(host, text, True)
                        self.client.hosts.remove(host)

    def close(self):
        self.pool.shutdown(False)

    def _hostName(self, host):
        if not self.hostConfig:
            return host
        return self.hostConfig[host].get('name', host)

    def _prefix(self, host):
        return self.log.colour(Fore.LIGHTBLUE_EX,
                               f'[{self._hostName(host)}]'.ljust(self.justification + 2))

    def _logCommand(self, output: Dict[str, HostOutput]):
        for hostOutput in output.values():
            self.pool.submit(self._logSingleOutput, hostOutput, error=False)
            self.pool.submit(self._logSingleOutput, hostOutput, error=True)

    def _print(self, host, line, isError=False):
        if isError:
            line = f'{self.log.colour(Fore.RED, "[err]")} {line}'
        text = f'{self._prefix(host)}\t{line}'
        fn = self.log.error if isError else self.log.print
        fn(text)

    def _logSingleOutput(self, hostOutput: HostOutput, error):
        lines = hostOutput.stderr if error else hostOutput.stdout
        for line in lines:
            self._print(hostOutput.host, line, error)
