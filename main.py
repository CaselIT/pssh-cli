from cli import getCli
from command_file import getCommands
from runner import Runner


def main(args):
    runner = Runner(
        args.timeout, hostNames=args.hostNames, hostFile=args.hostFile, quiet=args.quiet)

    if args.command:
        runner.runCommand(args.command, args.sudo)
    elif args.commandFile:
        commands = getCommands(args.commandFile)
        runner.runCommandList(commands)


if __name__ == '__main__':
    parser = getCli()
    args = parser.parse_args()
    main(args)
