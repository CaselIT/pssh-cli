import yaml


class CustomString(str):
    '''Allow different configurations on the same host'''

    def __eq__(self, other):
        return self is other

    def __hash__(self):
        return id(self)


def getHostConfig(fileToParse) -> dict:
    config: dict = yaml.load(fileToParse)
    if not config.get('hosts'):
        raise ValueError('"hosts" key is missing or empty')

    default = config.get('default', {})
    if not isinstance(default, dict):
        raise TypeError('"default" key must be an object')
    hostConfig = {}
    for index, host in enumerate(config['hosts']):
        if not isinstance(host, dict):
            raise TypeError(f'host {index + 1} is not an object')
        name, config = makeConfigForHost(host, default)
        if name in hostConfig:
            raise ValueError(f'host {name} is duplicate')
        hostConfig[name] = config
    return hostConfig


def makeConfigForHost(currentHost: dict, default: dict):
    config: dict = default.copy()
    config.update(currentHost)
    return CustomString(config.get('host')), config


_example = {
    'default': {
        'user': 'username (str)',
        'password': 'password to use (str)',
        'port': 'port (int)',
        'sudoRequiresPassword': 'if sudo requires sending the password (bool)'
    },
    'hosts': [{
        'host': 'host name. Required',
        'user': 'username',
        'password': 'password to use'
    }]
}


def saveExample(fileName: str):
    if not any(fileName.casefold().endswith(ext) for ext in ('yaml', 'yml')):
        fileName += '.yaml'
    with open(fileName, 'w') as f:
        yaml.dump(_example, f, default_flow_style=False)
    print(f'Saved example configuration to {fileName}')
