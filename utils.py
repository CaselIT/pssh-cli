from colorama import init, Fore
import sys
from threading import Lock


class Log:
    _SUDO_MSG = '[sudo] password for'

    def __init__(self, useColour, skipSudo=True):
        self.useColour = useColour
        self._colour = self._withColour if useColour else self._withoutColour
        if useColour:
            initColour()
        self.stdout = sys.stdout
        self.stderr = sys.stderr
        self.lock = Lock()

    def colour(self, colour, string):
        return self._colour(colour, string)

    def _withColour(self, colour, string):
        return f'{colour}{string}{Fore.RESET}'

    def _withoutColour(self, colour, string):
        return string

    def print(self, *args):
        self._syncPrint(*args, file=self.stdout)

    def __call__(self, *args):
        return self.print(*args)

    def error(self, *args):
        if any(self._SUDO_MSG in part for part in args):
            return
        self._syncPrint(*args, file=self.stderr)

    def _syncPrint(self, *args, **kwargs):
        with self.lock:
            print(*args, **kwargs)


_initCalled = False


def initColour():
    global _initCalled
    if not _initCalled:
        init()
        _initCalled = True
