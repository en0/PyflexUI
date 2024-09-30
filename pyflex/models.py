from typing import Optional
from enum import Enum, auto as enum_auto
from dataclasses import dataclass


class FlashROMActionEnum(Enum):
    PROBE = enum_auto()
    ERASE = enum_auto()
    READ = enum_auto()
    VERIFY = enum_auto()
    WRITE = enum_auto()


@dataclass
class FlashROMOpts:
    action: FlashROMActionEnum
    force: bool
    verbosity: int
    programmer: str
    input_path: Optional[str] = None


@dataclass
class FlashROMExecResult:
    message: str
    path: Optional[str] = None


