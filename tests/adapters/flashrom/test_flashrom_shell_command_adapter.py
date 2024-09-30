import pytest
from unittest.mock import patch, ANY
from subprocess import CompletedProcess
from contextlib import contextmanager

from pyflex.models import FlashROMOpts, FlashROMActionEnum, FlashROMExecResult
from pyflex.exceptions import PyFlexExecutionError
from adapters.flashrom import FlashROMShellCommandAdapter


def make_flashrom_opts(action: FlashROMActionEnum, **kwargs):
    kwargs.setdefault("force", False)
    kwargs.setdefault("verbosity", 0)
    kwargs.setdefault("programmer", "dummy:emulate=M25P10.RES")
    return FlashROMOpts(action=action, **kwargs)


def make_flashrom_result(**kwargs):
    kwargs.setdefault("args", ["flashrom", "-R"])
    kwargs.setdefault("returncode", 0)
    kwargs.setdefault("stdout", b'')
    kwargs.setdefault("stderr", b'')
    return CompletedProcess(**kwargs)


@contextmanager
def patch_exec(unit, result=None):
    result = result or make_flashrom_result()
    with patch.object(unit, "_execute_subprocess", return_value=result) as _patch:
        yield _patch


@pytest.fixture()
def testing_dir(tmp_path_factory):
    return tmp_path_factory.mktemp("flashrom_shell_command_adapter")


@pytest.fixture()
def output_path(testing_dir):
    return  testing_dir / "foo.bin"


@pytest.fixture()
def unit(output_path):
    return FlashROMShellCommandAdapter(output_path)


def test_flashrom_command_for_basic_write(
    unit: FlashROMShellCommandAdapter,
    testing_dir
):
    opts = make_flashrom_opts(
        FlashROMActionEnum.WRITE,
        input_path=testing_dir / "testfile.bin"
    )
    with patch_exec(unit) as _exec:
        unit.run(opts)
        _exec.assert_called_with([
            "flashrom",
            "-p", "dummy:emulate=M25P10.RES",
            "-w", opts.input_path,
        ])


def test_flashrom_command_for_write_with_verbosity_and_force(
    unit: FlashROMShellCommandAdapter,
    testing_dir
):
    opts = make_flashrom_opts(
        FlashROMActionEnum.WRITE,
        force=True,
        verbosity=3,
        input_path=testing_dir / "testfile.bin"
    )
    with patch_exec(unit) as _exec:
        unit.run(opts)
        _exec.assert_called_with([
            "flashrom",
            "-p", "dummy:emulate=M25P10.RES",
            "-w", opts.input_path,
            "-f", "-VVV",
        ])


def test_flashrom_command_for_erase(unit: FlashROMShellCommandAdapter):
    opts = make_flashrom_opts(FlashROMActionEnum.ERASE)
    with patch_exec(unit) as _exec:
        unit.run(opts)
        _exec.assert_called_with([
            "flashrom",
            "-p", "dummy:emulate=M25P10.RES",
            "-E",
        ])


def test_flashrom_command_for_verify(unit: FlashROMShellCommandAdapter, output_path):
    opts = make_flashrom_opts(
        FlashROMActionEnum.VERIFY,
        input_path=output_path / "testfile.bin",
    )
    with patch_exec(unit) as _exec:
        unit.run(opts)
        _exec.assert_called_with([
            "flashrom",
            "-p", "dummy:emulate=M25P10.RES",
            "-v", output_path / "testfile.bin"
        ])


def test_flashrom_command_for_probe(unit: FlashROMShellCommandAdapter):
    opts = make_flashrom_opts(FlashROMActionEnum.PROBE)
    with patch_exec(unit) as _exec:
        unit.run(opts)
        _exec.assert_called_with([
            "flashrom",
            "-p", "dummy:emulate=M25P10.RES",
        ])


def test_flashrom_command_for_read(unit: FlashROMShellCommandAdapter):
    opts = make_flashrom_opts(FlashROMActionEnum.READ)
    with patch_exec(unit) as _exec:
        unit.run(opts)
        _exec.assert_called_with([
            "flashrom",
            "-p", "dummy:emulate=M25P10.RES",
            "-r", ANY
        ])


def test_flashrom_should_raise_with_non_zero_exit(unit: FlashROMShellCommandAdapter):
    opts = make_flashrom_opts(FlashROMActionEnum.READ)
    result = make_flashrom_result(returncode=1)
    with patch_exec(unit, result):
        with pytest.raises(PyFlexExecutionError):
            unit.run(opts)


def test_flashrom_response_with_message_from_stdin(unit: FlashROMShellCommandAdapter):
    opts = make_flashrom_opts(FlashROMActionEnum.WRITE)
    result = make_flashrom_result(stdout=b"Hello, World!")
    expected = FlashROMExecResult("Hello, World!", path=None)
    with patch_exec(unit, result):
        assert(unit.run(opts) == expected)


def test_flashrom_response_with_message_from_stderr(unit: FlashROMShellCommandAdapter):
    opts = make_flashrom_opts(FlashROMActionEnum.WRITE)
    result = make_flashrom_result(stderr=b"Good-bye, World!")
    expected = FlashROMExecResult("Good-bye, World!", path=None)
    with patch_exec(unit, result):
        assert(unit.run(opts) == expected)


def test_flashrom_response_with_message_from_stdout_and_err(unit: FlashROMShellCommandAdapter):
    opts = make_flashrom_opts(FlashROMActionEnum.WRITE)
    result = make_flashrom_result(stdout=b"Hello, World!", stderr=b"Good-bye, World!")
    expected = FlashROMExecResult("STDOUT:\nHello, World!\n\nSTDERR:\nGood-bye, World!", path=None)
    with patch_exec(unit, result):
        assert(unit.run(opts) == expected)


def test_flashrom_response_with_file(unit: FlashROMShellCommandAdapter):
    opts = make_flashrom_opts(FlashROMActionEnum.READ)
    with patch_exec(unit):
        assert(unit.run(opts).path)
