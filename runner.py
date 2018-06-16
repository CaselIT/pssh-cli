from concurrent.futures import ThreadPoolExecutor
from pssh.clients import ParallelSSHClient
from pssh.output import HostOutput
from typing import List, Dict

from command_file import Command
from host_file import getHostConfig


class Runner:
    def __init__(self, timeout, hostNames=None, hostFile=None, quiet=False):
        self.quiet = quiet
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
            self._log(output)
        self.client.join(output)
        if logExit:
            for host, hostOutput in output.items():
                print(f'{self._prefix(host)}\texit code: {hostOutput.exit_code}')
        return output

    def runCommandList(self, commandList: List[Command], verbose=None):
        verbose = not self.quiet if verbose is None else verbose
        for command in commandList:
            if verbose:
                print(f'Running command {command.name}')
            output = self.runCommand(command.commad, command.sudo, verbose, False)
            if command.abortOnError:
                for host, hostOutput in output.items():
                    if hostOutput.exit_code:
                        print(f'[{self._hostName(host)}] command {command.name} exited with',
                              f'error {hostOutput.exit_code}.',
                              'No further commands will be executed.')
                        self.client.hosts.remove(host)

    def _hostName(self, host):
        if not self.hostConfig:
            return host
        return self.hostConfig[host].get('name', host)

    def _prefix(self, host):
        return f'[{self._hostName(host)}]'.ljust(self.justification + 2)

    def _log(self, output: Dict[str, HostOutput]):
        for hostOutput in output.values():
            self.pool.submit(self._logSingleOutput, hostOutput)

    def _logSingleOutput(self, hostOutput: HostOutput):
        for line in hostOutput.stdout:
            print(f'{self._prefix(hostOutput.host)}\t{line}')
