from pathlib import Path
from logging import getLogger
from uuid import uuid4 as uuid
from . import exceptions
from .typing import CommandDispatcher, FlashROMAdapter
from .models import (
    FlashROMActionEnum,
    FlashROMOpts,
    FlashROMExecResult,
)


_log = getLogger(__name__)


class FlashROMService(CommandDispatcher[FlashROMExecResult]):
    """Manage execution of the FlashROM utility.

    This service provides a safe method to execute a FlashROMAdapter. The service
    is intended to verify all parameters are safe and complient with the constraints
    of the PyFlex hat.

    Arguments:
        adapter:
            The FlashROMAdapter used to execute the FlashROM utiity.

        input_directory:
            The path used to store input files that are passed the the FlashROM utiity.

    Methods:
        set_action:
            Set the action for this execution.

        set_programmer:
            Set the programmer to use for this execution.

        set_file:
            Set the data to use as the input file.

        set_verbosity:
            Set the verbosity level for this execution.

        set_force:
            Enable the Force option when executing the FlashROM utility.

        unset_force:
            Disable the Force option when executing the FlashROM utility.

        execute:
            Execute the FlashROM utililty with the configured options.
    """

    def __init__(self, adapter: FlashROMAdapter, input_directory: str) -> None:
        self._adapter = adapter
        self._input_directory = Path(input_directory)

        self._action = None
        self._programmer = None
        self._verbosity = 0
        self._force = False
        self._file_name = None

    def set_action(self, action: str) -> None:
        """Set the action for this execution.

        Arguments:
            action:
                A string containing one of "probe", "erase", "write", "read", or
                "verify". Any other option will result in an error.

        Raises:
            PyFlexInvalidParameter:
                Raised if an invalid action is given.
        """

        try:
            self._action = {
                "probe": FlashROMActionEnum.PROBE,
                "erase": FlashROMActionEnum.ERASE,
                "write": FlashROMActionEnum.WRITE,
                "read": FlashROMActionEnum.READ,
                "verify": FlashROMActionEnum.VERIFY,
            }[action]
            _log.debug("Action: %s", self._action)

        except KeyError as ex:
            _log.error("Invalid value for ACTION: %s", action)
            raise exceptions.PyFlexInvalidParameter("Invalid value for ACTION.")

    def set_programmer(self, programmer: str) -> None:
        """Set the programmer to use for this execution.

        Arguments:
            programmer:
                A string representing the programmer device to use.

        Raises:
            Nothing
        """
        self._programmer = programmer
        _log.debug("Programmer: %s", programmer)

    def set_file(self, data: bytes) -> None:
        """Set the data to use as the input file.

        Arguments:
            data:
                Bytes to use as the input file.

        Raises:
            Nothing
        """
        try:
            file_path = self._file_path(f"{uuid()}.bin")
            with open(file_path, 'wb') as fd:
                fd.write(data)
            _log.debug("File uploaded to %s", file_path)
        except Exception:
            # Trapping this because it could fail and it will bubble all the way
            # out to the UI. Logs should capture this event if it happens.
            _log.error("Unexpected error while writing input file.")
            raise

    def set_verbosity(self, value: int) -> None:
        """Set the verbosity level for this execution.

        Arguments:
            value:
                An int between 0 and 3 that specify the verbosity level.

        Raises:
            PyFlexInvalidParameter:
                Raised if the given value is outside of the valid range.
        """
        if 0 <= value <= 3:
            self._verbosity = value
            _log.debug("Verbosity level: %s", value)
        else:
            _log.error("Invalid value for VERBOSITY: %s", value)
            raise PyFlexInvalidParameter("Invalid value for VERBOSITY")

    def set_force(self) -> None:
        """Enable the Force option when executing the FlashROM utility.

        Arguments:
            Nothing

        Raises:
            Nothing
        """
        self._force = True
        _log.debug("Force flag: True")

    def unset_force(self) -> None:
        """Disable the Force option when executing the FlashROM utility.

        Arguments:
            Nothing

        Raises:
            Nothing
        """
        self._force = False
        _log.debug("Force flag: False")

    def execute(self) -> FlashROMExecResult:
        """Execute the FlashROM utililty with the configured options.

        This function will validate all parameters for consistancy then pass them
        off to the FashROMAdapter. All errors are trapped and re-emitted with
        cient-safe information.

        Arguments:
            Nothing

        Raises:
            PyFlexException:
                Raised when any unexpected failure occures. This might be an issue
                with the adapter or a bug in how it is called. Consult logs for
                more information.

            PyFlexInvalidParameter:
                Raised when the service detects a missing or inconsistant parameters.
        """
        try:
            opts = self._build_opts()
            return self._adapter.run(opts)

        except exceptions.PyFlexException:
            _log.error("PyFlex Execution Failure")
            raise

        except Exception as ex:
            _log.error("General Execution Failure")
            raise exceptions.PyFlexExecutionError("Unable to execute FlashROM utility.") from ex

    def _build_opts(self) -> FlashROMOpts:

        file_path = self._file_path()

        if not self._action:
            raise exceptions.PyFlexInvalidParameter("Invalid value for ACTION.")

        elif self._action in [FlashROMActionEnum.ERASE, FlashROMActionEnum.PROBE] and self._file_name:
            raise exceptions.PyFlexInvalidParameter(
                f"Invalid Parameter. Action={self._action} cannot use an input file."
            )

        elif self._action in [FlashROMActionEnum.WRITE, FlashROMActionEnum.VERIFY] and not self._file_name:
            raise exceptions.PyFlexInvalidParameter(
                f"Invalid Parameter. Action={self._action} requires an input file."
            )

        elif self._action in {FlashROMActionEnum.WRITE, FlashROMActionEnum.VERIFY} and not file_path.exists():
            _log.error("Input file missing. Aborting execution. This is a bug!")
            raise exceptions.PyFlexExecutionError(
                f"File expected but does not exist. Cannot continue."
            )

        opts = FlashROMOpts(
            action=self._action,
            force=self._force,
            verbosity=self._verbosity,
            programmer=self._programmer,
            input_path=file_path,
        )

        _log.debug("PyFlex FlashROM execution options: %s", opts)
        return opts

    def _file_path(self, file_name: str = None) -> Path:
        if file_name is not None:
            self._file_name = file_name

        if self._file_name is None:
            return None

        return self._input_directory / self._file_name

