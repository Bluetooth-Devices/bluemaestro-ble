"""App-derived golden vectors and advertisement robustness regressions."""

import json
from pathlib import Path
from typing import TypedDict

import pytest
from bleak.backends.device import BLEDevice
from habluetooth import BluetoothServiceInfoBleak
from sensor_state_data import DeviceKey

from bluemaestro_ble.parser import BlueMaestroBluetoothDeviceData, _dew_point


class AppVector(TypedDict):
    """Native readings produced by the official app for one payload."""

    version: int
    payload: str
    expected: dict[str, float | int | None]


VECTORS = json.loads(
    (Path(__file__).parent / "fixtures/bmlogger-13.8.4.json").read_text()
)
LIVE_VECTORS = json.loads(
    (Path(__file__).parent / "fixtures/live-proxy.json").read_text()
)
LEGACY_22 = bytes.fromhex("16640e10000200f201f200830100")
PACKETS = [bytes.fromhex(row["payload"]) for row in VECTORS[::5]] + [LEGACY_22]


def advert(
    payload: bytes, source: str = "local", extra: bytes | None = None
) -> BluetoothServiceInfoBleak:
    data = {307: payload}
    if extra is not None:
        data[1234] = extra
    return BluetoothServiceInfoBleak(
        name="Sensor",
        address="aa:bb:cc:dd:ee:ff",
        rssi=-60,
        manufacturer_data=data,
        service_data={},
        service_uuids=[],
        source=source,
        device=BLEDevice("aa:bb:cc:dd:ee:ff", "Sensor", {}),
        advertisement=None,
        connectable=False,
        time=0,
        tx_power=None,
    )


def readings(
    parser: BlueMaestroBluetoothDeviceData, payload: bytes
) -> dict[str, float | int | None]:
    update = parser.update(advert(payload))
    return {
        key.key: value.native_value
        for key, value in update.entity_values.items()
        if key.key != "signal_strength"
    }


@pytest.mark.parametrize("vector", VECTORS + LIVE_VECTORS)
def test_matches_app(vector: AppVector) -> None:
    """Compare against execution of the official app's parser methods."""
    parser = BlueMaestroBluetoothDeviceData()
    assert readings(parser, bytes.fromhex(vector["payload"])) == vector["expected"]


@pytest.mark.parametrize("payload", PACKETS)
def test_truncated_and_recovery(payload: bytes) -> None:
    """Every truncated prefix is ignored, then a complete packet recovers."""
    for length in range(len(payload)):
        parser = BlueMaestroBluetoothDeviceData()
        assert not parser.supported(advert(payload[:length]))
        assert parser.update(advert(payload[:length])).entity_values == {}
        assert parser.supported(advert(payload))
        assert "temperature" in readings(parser, payload)


@pytest.mark.parametrize("payload", PACKETS)
def test_trailing_bytes(payload: bytes) -> None:
    """Optional statistics and scan-response bytes do not change readings."""
    assert readings(
        BlueMaestroBluetoothDeviceData(), payload + bytes(range(32))
    ) == readings(BlueMaestroBluetoothDeviceData(), payload)


@pytest.mark.parametrize(
    "payload",
    [
        b"",
        b"\x0a" + bytes(30),
        b"\x64" + bytes(30),
        b"\x65" + bytes(30),
        b"\xff" + bytes(30),
    ],
)
def test_unsupported(payload: bytes) -> None:
    assert not BlueMaestroBluetoothDeviceData().supported(advert(payload))


def test_legacy_22_preserved() -> None:
    assert readings(BlueMaestroBluetoothDeviceData(), LEGACY_22) == {
        "temperature": 24.2,
        "humidity": 49.8,
        "dew_point": 13.1,
        "battery": 100,
    }


@pytest.mark.parametrize("version", [23, 27, 42, 43])
def test_zero_humidity_clears_dew_point(version: int) -> None:
    vectors = [row for row in VECTORS if row["version"] == version]
    parser = BlueMaestroBluetoothDeviceData()
    assert (
        readings(parser, bytes.fromhex(vectors[0]["payload"]))["dew_point"] is not None
    )
    assert readings(parser, bytes.fromhex(vectors[3]["payload"]))["dew_point"] is None


def test_changed_other_manufacturer_and_adapter_switch() -> None:
    parser = BlueMaestroBluetoothDeviceData()
    payload = PACKETS[0]
    assert not parser.supported(advert(payload, extra=b"one"))
    # Only the unrelated manufacturer's data changes.
    assert not parser.supported(advert(payload, extra=b"two"))
    changed = bytearray(payload)
    changed[-1] += 1
    assert parser.supported(advert(bytes(changed), extra=b"two"))
    before = (
        parser.update(advert(bytes(changed), extra=b"two"))
        .entity_values[DeviceKey("temperature")]
        .native_value
    )
    update = parser.update(advert(payload, source="proxy", extra=b"three"))
    assert update.entity_values[DeviceKey("temperature")].native_value == before


def test_unrelated_manufacturer() -> None:
    info = advert(PACKETS[0])
    info.manufacturer_data.clear()
    assert not BlueMaestroBluetoothDeviceData().supported(info)


def test_pressure_unsigned_legacy() -> None:
    payload = bytearray(PACKETS[3])
    payload[10:12] = bytes.fromhex("9c40")
    assert (
        readings(BlueMaestroBluetoothDeviceData(), bytes(payload))["pressure"] == 4000
    )


@pytest.mark.parametrize("version", [23, 27, 42, 43])
def test_dew_point_singular_temperature(version: int) -> None:
    payload = bytearray.fromhex(
        next(row["payload"] for row in VECTORS if row["version"] == version)
    )
    modern = version >= 41
    offset = 15 if modern else 6
    payload[offset : offset + 2] = int(-243.5 * (100 if modern else 10)).to_bytes(
        2, "little" if modern else "big", signed=True
    )
    assert (
        readings(BlueMaestroBluetoothDeviceData(), bytes(payload))["dew_point"] is None
    )


@pytest.mark.parametrize("scale", [10, 100])
def test_dew_point_zero_denominator(scale: int) -> None:
    """Return unknown when floating-point rounding makes the denominator zero."""
    # Outside the advertisement range, this finite temperature makes alpha round
    # to exactly 17.67 at saturation. Exercise the helper's defensive guard.
    assert _dew_point(1e20, 100, scale) is None
