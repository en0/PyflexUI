from abc import ABC, abstractmethod
from typing import TypeVar

from .models import *


T = TypeVar('T')


class CommandDispatcher[T](ABC):

    @abstractmethod
    def execute(self) -> T:
        """Executes a command and returns the result"""
        ...


class FlashROMAdapter(ABC):

    @abstractmethod
    def run(self, opts: FlashROMOpts) -> FlashROMExecResult:
        """Runs the flashrom utility with the given options."""
        ...

