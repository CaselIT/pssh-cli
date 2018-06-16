def main(args):
    import command_file as cf
    import host_file as hf
    if args.command not in ('hosts', 'commands'):
        raise TypeError(f'command {args.command} not supported')
    if args.checkFile:
        from pprint import pprint
        parse = hf.getHostConfig if args.command == 'hosts' else cf.getCommands
        with open(args.fileName) as f:
            pprint(parse(f))
    else:
        saveExample = hf.saveExample if args.command == 'hosts' else cf.saveExample
        saveExample(args.fileName)


def cli():
    from argparse import ArgumentParser
    parser = ArgumentParser(description='Save example configuration or check an existing one')

    sub = parser.add_subparsers(title='Command to use', dest='command')
    sub.add_parser('hosts', help='Save example configuration for the host file')
    sub.add_parser('commands', help='Save example configuration for the command file')

    parser.add_argument('fileName', help='Save to this file')
    parser.add_argument(
        '-c',
        '--checkFile',
        help='Check the fileName instead of saving an example',
        action='store_true')
    return parser


if __name__ == '__main__':
    parser = cli()
    args = parser.parse_args()
    main(args)
