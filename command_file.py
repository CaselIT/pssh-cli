import yaml
from typing import List


class Command:
    def __init__(self, commandDict: dict, index: int):
        if 'command' not in commandDict:
            raise ValueError(f'"command" key is missing in command {index + 1}')
        self.name = commandDict.get('name', f'Command {index + 1}')
        self.commad = commandDict['command']
        self.sudo = commandDict.get('sudo', False)
        self.abortOnError = commandDict.get('abortOnError', False)

    def __repr__(self):
        return f'{type(self).__name__}: {vars(self)}'


def getCommands(fileToParse) -> List[Command]:
    commands: dict = yaml.load(fileToParse)
    if not commands.get('commands'):
        raise ValueError('"commands" key if missing of empty')

    return [Command(cmd, i) for i, cmd in enumerate(commands['commands'])]


_example = {
    'commands': [{
        'name':
        'optional name for the command (str)',
        'command':
        'the command. Required (str)',
        'sudo':
        'if sudo is required. default false (bool)',
        'abortOnError': ('if an error happens abort the execution of the '
                         'next commands. default false (bool)')
    }, {
        'name': 'cmd 2',
        'command': 'date'
    }]
}


def saveExample(fileName: str):
    if not any(fileName.casefold().endswith(ext) for ext in ('yaml', 'yml')):
        fileName += '.yaml'
    with open(fileName, 'w') as f:
        yaml.dump(_example, f, default_flow_style=False)
    print(f'Saved example configuration to {fileName}')
