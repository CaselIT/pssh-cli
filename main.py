from sys import exit

from cli import getCli
from command_file import getCommands
from runner import Runner
from utils import Log


def main(args):
    log = Log(not args.noColour)
    runner = Runner(
        args.timeout,
        log,
        hostNames=args.hostNames,
        hostFile=args.hostFile,
        quiet=args.quiet,
        only=args.only)

    if args.command:
        runner.runCommand(args.command, args.sudo)
    elif args.commandFile:
        commands = getCommands(args.commandFile)
        runner.runCommandList(commands)
    runner.close()
    exit()


if __name__ == '__main__':
    parser = getCli()
    args = parser.parse_args()
    main(args)
