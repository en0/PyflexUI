from unittest.mock import Mock
from pyflex import FlashROMService
from pyflex.typing import FlashROMAdapter, FlashROMExecResult
from adapters.flashrom import FlashROMShellCommandAdapter


def get_flashrom():
    adapter = FlashROMShellCommandAdapter("webui/outputs/")
    service = FlashROMService(adapter, "webui/inputs/")
    return service

