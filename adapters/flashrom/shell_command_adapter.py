import subprocess
from pathlib import Path
from uuid import uuid4 as uuid
from os import environ
from typing import Optional
from logging import getLogger
from pyflex.exceptions import PyFlexExecutionError
from pyflex.typing import (
    FlashROMActionEnum,
    FlashROMAdapter,
    FlashROMExecResult,
    FlashROMOpts,
)


_log = getLogger(__name__)


def _prepair_response(result):
    # TODO: Probably move this up to common library once it's needed.

    msg = result.stdout.decode('utf8').strip()
    err = result.stderr.decode('utf8').strip()

    if msg and err:
        return f"STDOUT:\n{msg}\n\nSTDERR:\n{err}"

    elif err:
        return err

    elif msg:
        return msg

    else:
        return f"Application exited without details - CODE: {result.returncode}"


class FlashROMShellCommandAdapter(FlashROMAdapter):
    """Execute the FlashROM utility.

    This class is implemented to provide a FlashROMAdapter that executes the
    FlashROM utility on the host running this code. This adapter expects that the
    arguments given to it are correct and well-formed. No checks are made for
    argument consistancy.

    Arguments:
        output_path:
            The directory to write output files, if applicable.

        env:
            An optional dictionary of environment variables to pass to the
            FlashROM utility.

    Methods:
        run: Runs the FlashROM utility.
    """

    def __init__(self, output_path: str, env: Optional[dict[str, str]] = None) -> None:

        _log.debug(
            "Initilized FlashROMShellCommandAdapter with "
            "options: output_path=%s, env=%s",
            output_path,
            env
        )

        self._output_path = Path(output_path)
        self._env = env

    def _execute_subprocess(self, command: list) -> subprocess.CompletedProcess:
        _log.info("Running subprocess: %s", command)
        return subprocess.run(
            args=command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

    def _make_command(self, opts: FlashROMOpts) -> list:

        # This command is passed to subprocess which is considered safe.
        # For more information regarding the subprocess, read the following document.
        # https://docs.python.org/3/library/subprocess.html#security-considerations

        ret = ["flashrom"]
        file_name = None

        if opts.action == FlashROMActionEnum.PROBE:
            ret.extend([
                "-p", opts.programmer,
            ]);

        elif opts.action == FlashROMActionEnum.WRITE:
            ret.extend([
                "-p", opts.programmer,
                "-w", opts.input_path,
            ]);

        elif opts.action == FlashROMActionEnum.ERASE:
            ret.extend([
                "-p", opts.programmer,
                "-E"
            ]);

        elif opts.action == FlashROMActionEnum.VERIFY:
            ret.extend([
                "-p", opts.programmer,
                "-v", opts.input_path,
            ]);

        elif opts.action == FlashROMActionEnum.READ:
            # The caller expects this file name, so save it so we can return the
            # value.
            file_name = f"{uuid()}.bin"
            ret.extend([
                "-p", opts.programmer,
                "-r", f'"{str(self._output_path / file_name)}"',
            ])

        # Global Flags
        if opts.force:
            ret.append("-f")
        if opts.verbosity > 0:
            ret.append("-" + ("V" * min(3, opts.verbosity)))

        return ret, file_name


    def run(self, opts: FlashROMOpts) -> FlashROMExecResult:
        """Runs the flashrom utility with the given options.

        Arguments:
            opts:
                A FlashROMOpts object that identifies the arguments
                to pass to the flashrom utility.

        Raises:
            PyFlexExecutionError:
                Raised when the exit code of FlashROM is non-zero.

        Returns:
            FlashROMExecResult:
                contains the result data from FlashROM including the
                message and binary file, if applicable.
        """

        command, file_name = self._make_command(opts)
        result = self._execute_subprocess(command)
        msg = _prepair_response(result)

        if result.returncode != 0:

            _log.warning(
                "Non-zero Exit Code: %s, STDOUT: %s, STDERR: %s",
                result.returncode,
                result.stdout,
                result.stderr
            )

            raise PyFlexExecutionError(msg)

        else:

            _log.debug("FlashROM execution succeeded")
            return FlashROMExecResult(msg, file_name)
