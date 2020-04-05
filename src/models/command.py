# -*- coding: utf-8 -*-
"""
.. module:: command
   :platform: Windows
   :synopsis: Creates a runnable command

.. moduleauthor:: Ryan Long <ryanlong1004@gmail.com>

"""
import asyncio
import datetime
import logging
import sys
from asyncio.subprocess import Process
from typing import Union, Coroutine

LOG_FORMAT = "%(asctime)s-%(levelname)-5s:%(message)s"
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format=LOG_FORMAT)

LOG = logging.getLogger(__name__)


class CommandError(Exception):
    """Represents a CommandError"""


class Command:
    """
    Represents a runnable command
    """

    def __init__(self, cmd: str, stderr_target=None, stdout_target=None):
        """

        Args:
            cmd (str): command to run
            stderr_target (StreamReader): destination for stderr
            stdout_target (StreamReader): destination for stdout
        """
        self._stdout_target = stdout_target
        self._stderr_target = stderr_target
        self._process = None

        self.cmd = cmd
        self.stdout = None
        self.stderr = None
        self.start_time = None
        self.end_time = None

    @property
    def return_code(self) -> Union[int, None]:
        """

        Returns:
            return code if exists or ``none``

        """
        if hasattr(self._process, "returncode"):
            return self._process.returncode
        return None

    @property
    def pid(self) -> Union[int, None]:
        """

        Returns:
            pid if exists else ``none``

        """
        if hasattr(self._process, "pid"):
            return self._process.pid
        return None

    @property
    def time_delta(self):
        seconds = (self.end_time - self.start_time).total_seconds()
        minutes = divmod(seconds, 60)[0]
        return minutes, seconds

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self.cmd}>"

    def __str__(self) -> str:
        if self.pid is None:
            return f"{self.cmd:60} [None] [None]"
        return (
            f"{self.cmd:60} [{self.pid:6}] [{self.return_code:3}] "
            f"Start:{self.start_time} "
            f"End:{self.end_time} "
            f"Elapsed:{self.time_delta[0]:6}m {self.time_delta[1]:8}s"
        )

    def __call__(self) -> Coroutine:
        """Builds the command and returns a coroutine

        Returns:
            coroutine

        """

        async def func():
            """

            Returns:
                ``none``

            """
            self.start_time = get_date_time_string()
            process = await asyncio.create_subprocess_shell(
                self.cmd,
                stdout=self._stdout_target
                if self._stdout_target is not None
                else asyncio.subprocess.PIPE,
                stderr=self._stderr_target
                if self._stderr_target is not None
                else asyncio.subprocess.PIPE,
            )
            self._process = process
            self.stdout, self.stderr = await parse_streams_on_complete(process)
            self.end_time = get_date_time_string()
            write_log(self)
            return None

        return func()


def bytes_to_string(_bytes) -> str:
    """Decodes bytes to utf-8 string

    Args:
        _bytes (bytes): bytes value

    Returns:
        str

    .. todo:: We're not decoding the string here, because it
        fails for certain windows commands
    """
    value = str(_bytes.replace(b"\x00", b""))[2:-1].replace("\r", "")
    value = value.replace("\\r", "").replace("\\n", " ")
    return value


async def parse_streams_on_complete(process: Process) -> tuple:
    """Awaits process to finish and the converts streams from bytes to strings

    Args:
        process (Process):

    Returns:
        tuple(str|str)

    """
    stdout, stderr = await process.communicate()
    return bytes_to_string(stdout), bytes_to_string(stderr)


def write_log(command: Command):
    """Writes command to info or error log

    Args:
        command (Command): command

    Returns:
        ``none``
    """
    if command.return_code == 0:
        LOG.info(f"{command}")
    else:
        LOG.error(f"{command}{command.stderr}{command.stdout}")


def get_date_time_string():
    """Returns current date/time string

    Returns:
        string (2017-01-09 03:47:21,595)

    """
    return datetime.datetime.now()
