from uuid import UUID

from bleak.backends.device import BLEDevice
from bluetooth_data_tools import monotonic_time_coarse
from bluetooth_sensor_state_data import SensorUpdate
from habluetooth import BluetoothServiceInfoBleak
from sensor_state_data import (
    DeviceKey,
    SensorDescription,
    SensorDeviceClass,
    SensorDeviceInfo,
    SensorValue,
    Units,
)

from bluemaestro_ble.parser import BlueMaestroBluetoothDeviceData


def make_bluetooth_service_info(  # noqa: PLR0913
    name: str,
    manufacturer_data: dict[int, bytes],
    service_uuids: list[str],
    address: str,
    rssi: int,
    service_data: dict[UUID, bytes],
    source: str,
    tx_power: int = 0,
    raw: bytes | None = None,
) -> BluetoothServiceInfoBleak:
    return BluetoothServiceInfoBleak(
        name=name,
        manufacturer_data=manufacturer_data,
        service_uuids=service_uuids,
        address=address,
        rssi=rssi,
        service_data=service_data,
        source=source,
        device=BLEDevice(
            name=name,
            address=address,
            details={},
            rssi=rssi,
        ),
        time=monotonic_time_coarse(),
        advertisement=None,
        connectable=True,
        tx_power=tx_power,
        raw=raw,
    )


def test_can_create():
    BlueMaestroBluetoothDeviceData()


TEMPO_DISC_THD = make_bluetooth_service_info(
    name="FA17B62C",
    manufacturer_data={
        307: b"\x17d\x0e\x10\x00\x02\x00\xf2\x01\xf2\x00\x83\x01\x00\x01\r\x02\xab\x00\xf2\x01\xf2\x01\r\x02\xab\x00\xf2\x01\xf2\x00\xff\x02N\x00\x00\x00\x00\x00"
    },
    address="aa:bb:cc:dd:ee:ff",
    rssi=-60,
    service_data={},
    service_uuids=[],
    source="local",
)


def test_temp_disc_thd():
    parser = BlueMaestroBluetoothDeviceData()
    update = parser.update(TEMPO_DISC_THD)
    assert update == SensorUpdate(
        title="Tempo Disc THD EEFF",
        devices={
            None: SensorDeviceInfo(
                name="Tempo Disc THD EEFF",
                model="Tempo Disc THD",
                manufacturer="BlueMaestro",
                sw_version=None,
                hw_version=None,
            )
        },
        entity_descriptions={
            DeviceKey(key="temperature", device_id=None): SensorDescription(
                device_key=DeviceKey(key="temperature", device_id=None),
                device_class=SensorDeviceClass.TEMPERATURE,
                native_unit_of_measurement=Units.TEMP_CELSIUS,
            ),
            DeviceKey(key="humidity", device_id=None): SensorDescription(
                device_key=DeviceKey(key="humidity", device_id=None),
                device_class=SensorDeviceClass.HUMIDITY,
                native_unit_of_measurement=Units.PERCENTAGE,
            ),
            DeviceKey(key="battery", device_id=None): SensorDescription(
                device_key=DeviceKey(key="battery", device_id=None),
                device_class=SensorDeviceClass.BATTERY,
                native_unit_of_measurement=Units.PERCENTAGE,
            ),
            DeviceKey(key="dew_point", device_id=None): SensorDescription(
                device_key=DeviceKey(key="dew_point", device_id=None),
                device_class=SensorDeviceClass.DEW_POINT,
                native_unit_of_measurement=Units.TEMP_CELSIUS,
            ),
            DeviceKey(key="signal_strength", device_id=None): SensorDescription(
                device_key=DeviceKey(key="signal_strength", device_id=None),
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
        },
        entity_values={
            DeviceKey(key="temperature", device_id=None): SensorValue(
                device_key=DeviceKey(key="temperature", device_id=None),
                name="Temperature",
                native_value=24.2,
            ),
            DeviceKey(key="humidity", device_id=None): SensorValue(
                device_key=DeviceKey(key="humidity", device_id=None),
                name="Humidity",
                native_value=49.8,
            ),
            DeviceKey(key="battery", device_id=None): SensorValue(
                device_key=DeviceKey(key="battery", device_id=None),
                name="Battery",
                native_value=100,
            ),
            DeviceKey(key="dew_point", device_id=None): SensorValue(
                device_key=DeviceKey(key="dew_point", device_id=None),
                name="Dew " "Point",
                native_value=13.1,
            ),
            DeviceKey(key="signal_strength", device_id=None): SensorValue(
                device_key=DeviceKey(key="signal_strength", device_id=None),
                name="Signal " "Strength",
                native_value=-60,
            ),
        },
    )


def test_temp_disc_thd_raw():
    parser = BlueMaestroBluetoothDeviceData()
    update = parser.update(
        make_bluetooth_service_info(
            name="FA17B62C",
            manufacturer_data={307: b""},  # any will do
            address="aa:bb:cc:dd:ee:ff",
            rssi=-60,
            service_data={},
            service_uuids=[],
            source="local",
            raw=b"\x2a\xff\x33\x01\x17\x64\x0e\x10\x00\x02\x00\xf2"
            b"\x01\xf2\x00\x83\x01\x00\x01\x0d\x02\xab\x00\xf2"
            b"\x01\xf2\x01\x0d\x02\xab\x00\xf2\x01\xf2\x00\xff"
            b"\x02\x4e\x00\x00\x00\x00\x00",
        )
    )
    assert update == SensorUpdate(
        title="Tempo Disc THD EEFF",
        devices={
            None: SensorDeviceInfo(
                name="Tempo Disc THD EEFF",
                model="Tempo Disc THD",
                manufacturer="BlueMaestro",
                sw_version=None,
                hw_version=None,
            )
        },
        entity_descriptions={
            DeviceKey(key="temperature", device_id=None): SensorDescription(
                device_key=DeviceKey(key="temperature", device_id=None),
                device_class=SensorDeviceClass.TEMPERATURE,
                native_unit_of_measurement=Units.TEMP_CELSIUS,
            ),
            DeviceKey(key="humidity", device_id=None): SensorDescription(
                device_key=DeviceKey(key="humidity", device_id=None),
                device_class=SensorDeviceClass.HUMIDITY,
                native_unit_of_measurement=Units.PERCENTAGE,
            ),
            DeviceKey(key="battery", device_id=None): SensorDescription(
                device_key=DeviceKey(key="battery", device_id=None),
                device_class=SensorDeviceClass.BATTERY,
                native_unit_of_measurement=Units.PERCENTAGE,
            ),
            DeviceKey(key="dew_point", device_id=None): SensorDescription(
                device_key=DeviceKey(key="dew_point", device_id=None),
                device_class=SensorDeviceClass.DEW_POINT,
                native_unit_of_measurement=Units.TEMP_CELSIUS,
            ),
            DeviceKey(key="signal_strength", device_id=None): SensorDescription(
                device_key=DeviceKey(key="signal_strength", device_id=None),
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
        },
        entity_values={
            DeviceKey(key="temperature", device_id=None): SensorValue(
                device_key=DeviceKey(key="temperature", device_id=None),
                name="Temperature",
                native_value=24.2,
            ),
            DeviceKey(key="humidity", device_id=None): SensorValue(
                device_key=DeviceKey(key="humidity", device_id=None),
                name="Humidity",
                native_value=49.8,
            ),
            DeviceKey(key="battery", device_id=None): SensorValue(
                device_key=DeviceKey(key="battery", device_id=None),
                name="Battery",
                native_value=100,
            ),
            DeviceKey(key="dew_point", device_id=None): SensorValue(
                device_key=DeviceKey(key="dew_point", device_id=None),
                name="Dew " "Point",
                native_value=13.1,
            ),
            DeviceKey(key="signal_strength", device_id=None): SensorValue(
                device_key=DeviceKey(key="signal_strength", device_id=None),
                name="Signal " "Strength",
                native_value=-60,
            ),
        },
    )


def test_temp_disc_thd_raw_missing_data():
    """Test 307 in the manufacturer data by raw is missing it."""
    parser = BlueMaestroBluetoothDeviceData()
    update = parser.update(
        make_bluetooth_service_info(
            name="FA17B62C",
            manufacturer_data={307: b""},  # any will do
            address="aa:bb:cc:dd:ee:ff",
            rssi=-60,
            service_data={},
            service_uuids=[],
            source="local",
            raw=b"\x2a\xff",
        )
    )
    assert update == SensorUpdate(
        title=None,
        devices={},
        entity_descriptions={},
        entity_values={},
        binary_entity_descriptions={},
        binary_entity_values={},
        events={},
    )
