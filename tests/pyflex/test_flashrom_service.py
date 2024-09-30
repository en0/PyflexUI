import pytest
from pathlib import Path
from unittest.mock import Mock, ANY

from pyflex import FlashROMService
from pyflex.models import FlashROMActionEnum, FlashROMExecResult, FlashROMOpts
from pyflex.typing import FlashROMAdapter
from pyflex.exceptions import PyFlexExecutionError, PyFlexInvalidParameter


def make_flashrom_opts(action: FlashROMActionEnum, **kwargs):
    ## TODO: Duplilcate of flashrom tests. Move to test helpers
    kwargs.setdefault("force", False)
    kwargs.setdefault("verbosity", 0)
    kwargs.setdefault("programmer", "dummy:emulate=M25P10.RES")
    return FlashROMOpts(action=action, **kwargs)


@pytest.fixture()
def input_directory(tmp_path_factory):
    return tmp_path_factory.mktemp("flashrom_service")


@pytest.fixture()
def adapter():
    return Mock(
        spec=FlashROMAdapter,
        return_value=FlashROMExecResult("Okay", None)
    )


@pytest.fixture()
def unit(adapter, input_directory):
    return FlashROMService(adapter, input_directory)


def test_can_probe(unit, adapter):
    expected = make_flashrom_opts(FlashROMActionEnum.PROBE)
    unit.set_action("probe")
    unit.set_programmer("dummy:emulate=M25P10.RES")
    unit.execute()
    adapter.run.assert_called_with(expected)


def test_can_erase(unit, adapter):
    expected = make_flashrom_opts(FlashROMActionEnum.ERASE)
    unit.set_action("erase")
    unit.set_programmer("dummy:emulate=M25P10.RES")
    unit.execute()
    adapter.run.assert_called_with(expected)


def test_can_read(unit, adapter):
    expected = make_flashrom_opts(FlashROMActionEnum.READ)
    unit.set_action("read")
    unit.set_programmer("dummy:emulate=M25P10.RES")
    unit.execute()
    adapter.run.assert_called_with(expected)


def test_can_write(unit, adapter):
    expected = make_flashrom_opts(
        FlashROMActionEnum.WRITE,
        input_path=ANY
    )
    unit.set_action("write")
    unit.set_programmer("dummy:emulate=M25P10.RES")
    unit.set_file(b"0100100001101001")
    unit.execute()
    adapter.run.assert_called_with(expected)


def test_can_verify(unit, adapter):
    expected = make_flashrom_opts(
        FlashROMActionEnum.VERIFY,
        input_path=ANY
    )
    unit.set_action("verify")
    unit.set_programmer("dummy:emulate=M25P10.RES")
    unit.set_file(b"0100100001101001")
    unit.execute()
    adapter.run.assert_called_with(expected)


def test_file_is_created_in_input_directory_when_write(unit, input_directory):
    expected = b"0100100001101001"
    unit.set_action("write")
    unit.set_programmer("dummy:emulate=M25P10.RES")
    unit.set_file(expected)
    unit.execute()
    try:
        in_file = next(input_directory.rglob("*.bin"))
        with open(in_file, 'rb') as fd:
            actual = fd.read()
        assert(actual == expected)
    finally:
        Path(in_file).unlink()


def test_file_is_created_in_input_directory_when_verify(unit, input_directory):
    expected = b"0100100001101001"
    unit.set_action("verify")
    unit.set_programmer("dummy:emulate=M25P10.RES")
    unit.set_file(expected)
    unit.execute()
    try:
        in_file = next(input_directory.rglob("*.bin"))
        with open(in_file, 'rb') as fd:
            actual = fd.read()
        assert(actual == expected)
    finally:
        Path(in_file).unlink()


def test_force_flag(unit, adapter, input_directory):
    expected = make_flashrom_opts(FlashROMActionEnum.READ, force=True)
    unit.set_action("read")
    unit.set_programmer("dummy:emulate=M25P10.RES")
    unit.set_force()
    unit.execute()
    adapter.run.assert_called_with(expected)


def test_verbosity_flag(unit, adapter, input_directory):
    expected = make_flashrom_opts(FlashROMActionEnum.READ, verbosity=3)
    unit.set_action("read")
    unit.set_programmer("dummy:emulate=M25P10.RES")
    unit.set_verbosity(3)
    unit.execute()
    adapter.run.assert_called_with(expected)


def test_pyflex_execution_errors_are_forwarded(unit, adapter, input_directory):
    expected = PyFlexExecutionError("Hello from unittest")
    adapter.run = Mock(side_effect=expected)
    unit.set_action("read")
    unit.set_programmer("dummy:emulate=M25P10.RES")
    with pytest.raises(PyFlexExecutionError) as err:
        unit.execute()
    assert err.value == expected


def test_pyflex_raises_parameter_error_if_handed_a_file_with_an_erase_action(
    unit, adapter, input_directory
):
    unit.set_action("erase")
    unit.set_file(b"0100100001101001")
    unit.set_programmer("dummy:emulate=M25P10.RES")
    with pytest.raises(PyFlexInvalidParameter) as err:
        unit.execute()


def test_pyflex_raises_parameter_error_if_handed_a_file_with_a_probe_action(
    unit, adapter, input_directory
):
    unit.set_action("probe")
    unit.set_file(b"0100100001101001")
    unit.set_programmer("dummy:emulate=M25P10.RES")
    with pytest.raises(PyFlexInvalidParameter) as err:
        unit.execute()


def test_pyflex_raises_parameter_error_if_not_handed_a_file_with_a_write_action(
    unit, adapter, input_directory
):
    unit.set_action("write")
    unit.set_programmer("dummy:emulate=M25P10.RES")
    with pytest.raises(PyFlexInvalidParameter) as err:
        unit.execute()


def test_pyflex_raises_parameter_error_if_not_handed_a_file_with_a_verify_action(
    unit, adapter, input_directory
):
    unit.set_action("verify")
    unit.set_programmer("dummy:emulate=M25P10.RES")
    with pytest.raises(PyFlexInvalidParameter) as err:
        unit.execute()
