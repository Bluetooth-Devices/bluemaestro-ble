"""App-derived golden vectors and advertisement robustness regressions."""

import json
from pathlib import Path
from typing import TypedDict

import pytest
from bleak.backends.device import BLEDevice
from habluetooth import BluetoothServiceInfoBleak
from sensor_state_data import DeviceKey

from bluemaestro_ble.parser import BlueMaestroBluetoothDeviceData


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
LEGACY_23 = bytes.fromhex("17640e10000200f201f200830100")
PACKETS = [
    bytes.fromhex(row["payload"]) for row in VECTORS[::5] if row["version"] != 23
] + [LEGACY_22, LEGACY_23]


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


@pytest.mark.parametrize(
    "vector", [row for row in VECTORS + LIVE_VECTORS if row["version"] != 23]
)
def test_matches_app(vector: AppVector) -> None:
    """Compare against execution of the official app's parser methods."""
    parser = BlueMaestroBluetoothDeviceData()
    expected = dict(vector["expected"])
    if vector["version"] == 27:
        # Preserve the existing THPD sensor set; the app also calculates dew point.
        expected.pop("dew_point")
    assert readings(parser, bytes.fromhex(vector["payload"])) == expected


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


@pytest.mark.parametrize("version", [42, 43])
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
    payload = bytearray.fromhex(
        next(row["payload"] for row in VECTORS if row["version"] == 27)
    )
    payload[10:12] = bytes.fromhex("9c40")
    assert (
        readings(BlueMaestroBluetoothDeviceData(), bytes(payload))["pressure"] == 4000
    )


@pytest.mark.parametrize("version", [42, 43])
def test_dew_point_singular_temperature(version: int) -> None:
    payload = bytearray.fromhex(
        next(row["payload"] for row in VECTORS if row["version"] == version)
    )
    payload[15:17] = (-24350).to_bytes(2, "little", signed=True)
    assert (
        readings(BlueMaestroBluetoothDeviceData(), bytes(payload))["dew_point"] is None
    )


@pytest.mark.parametrize(
    ("vector", "dew_point"),
    list(
        zip([row for row in LIVE_VECTORS if row["version"] == 23], [4.7, 4.9, 5.0, 3.6])
    ),
)
def test_live_v23_transmitted_dew_point(vector: AppVector, dew_point: float) -> None:
    """Keep the transmitted reading even when the app calculates another value."""
    payload = bytes.fromhex(vector["payload"])
    expected = dict(vector["expected"])
    expected["dew_point"] = dew_point
    assert readings(BlueMaestroBluetoothDeviceData(), payload) == expected


@pytest.mark.parametrize("dew_point", [49, -123, 0])
def test_v23_transmitted_dew_point(dew_point: int) -> None:
    """Decode signed transmitted dew point independently of temperature/humidity."""
    payload = bytearray(LEGACY_23)
    payload[10:12] = dew_point.to_bytes(2, "big", signed=True)
    assert (
        readings(BlueMaestroBluetoothDeviceData(), bytes(payload))["dew_point"]
        == dew_point / 10
    )
