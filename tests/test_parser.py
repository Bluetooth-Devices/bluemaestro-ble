from bluetooth_sensor_state_data import SensorUpdate
from sensor_state_data import (
    DeviceKey,
    SensorDescription,
    SensorDeviceClass,
    SensorDeviceInfo,
    SensorValue,
    Units,
)

from bluemaestro_ble.parser import BlueMaestroBluetoothDeviceData
from tests.helpers import make_bluetooth_service_info


def test_can_create() -> None:
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


def test_temp_disc_thd() -> None:
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
                name="Dew Point",
                native_value=13.1,
            ),
            DeviceKey(key="signal_strength", device_id=None): SensorValue(
                device_key=DeviceKey(key="signal_strength", device_id=None),
                name="Signal Strength",
                native_value=-60,
            ),
        },
    )


def test_temp_disc_thd_raw() -> None:
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
                name="Dew Point",
                native_value=13.1,
            ),
            DeviceKey(key="signal_strength", device_id=None): SensorValue(
                device_key=DeviceKey(key="signal_strength", device_id=None),
                name="Signal Strength",
                native_value=-60,
            ),
        },
    )


TEMPO_DISC_T = make_bluetooth_service_info(
    name="FABF5A2E",
    manufacturer_data={307: b"\rd\x02X\n\xd1\x00\xfc\x01\x00"},
    address="aa:bb:cc:dd:ee:ff",
    rssi=-65,
    service_data={},
    service_uuids=[],
    source="local",
)


def test_tempo_disc_t() -> None:
    parser = BlueMaestroBluetoothDeviceData()
    update = parser.update(TEMPO_DISC_T)
    assert update == SensorUpdate(
        title="Tempo Disc T EEFF",
        devices={
            None: SensorDeviceInfo(
                name="Tempo Disc T EEFF",
                model="Tempo Disc T",
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
            DeviceKey(key="battery", device_id=None): SensorDescription(
                device_key=DeviceKey(key="battery", device_id=None),
                device_class=SensorDeviceClass.BATTERY,
                native_unit_of_measurement=Units.PERCENTAGE,
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
                native_value=25.2,
            ),
            DeviceKey(key="battery", device_id=None): SensorValue(
                device_key=DeviceKey(key="battery", device_id=None),
                name="Battery",
                native_value=100,
            ),
            DeviceKey(key="signal_strength", device_id=None): SensorValue(
                device_key=DeviceKey(key="signal_strength", device_id=None),
                name="Signal Strength",
                native_value=-65,
            ),
        },
    )


TEMPO_DISC_THPD = make_bluetooth_service_info(
    name="FA17B62C",
    manufacturer_data={
        307: b"\x1bd\x0e\x10\x00\x02\x00\xf2\x01\xf2\x00\x83\x01\x00\x01\r\x02\xab\x00\xf2\x01\xf2\x01\r\x02\xab\x00\xf2\x01\xf2\x00\xff\x02N\x00\x00\x00\x00\x00"
    },
    address="aa:bb:cc:dd:ee:ff",
    rssi=-60,
    service_data={},
    service_uuids=[],
    source="local",
)


def test_temp_disc_thpd() -> None:
    parser = BlueMaestroBluetoothDeviceData()
    update = parser.update(TEMPO_DISC_THPD)
    assert update == SensorUpdate(
        title="Tempo Disc THPD EEFF",
        devices={
            None: SensorDeviceInfo(
                name="Tempo Disc THPD EEFF",
                model="Tempo Disc THPD",
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
            DeviceKey(key="pressure", device_id=None): SensorDescription(
                device_key=DeviceKey(key="pressure", device_id=None),
                device_class=SensorDeviceClass.PRESSURE,
                native_unit_of_measurement=Units.PRESSURE_MBAR,
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
            DeviceKey(key="pressure", device_id=None): SensorValue(
                device_key=DeviceKey(key="pressure", device_id=None),
                name="Pressure",
                native_value=13.1,
            ),
            DeviceKey(key="signal_strength", device_id=None): SensorValue(
                device_key=DeviceKey(key="signal_strength", device_id=None),
                name="Signal Strength",
                native_value=-60,
            ),
        },
    )


def test_temp_disc_thd_raw_missing_data() -> None:
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


EMPTY_SENSOR_UPDATE = SensorUpdate(
    title=None,
    devices={},
    entity_descriptions={},
    entity_values={},
    binary_entity_descriptions={},
    binary_entity_values={},
    events={},
)


def test_empty_manufacturer_data() -> None:
    """Test an empty manufacturer data payload is ignored."""
    parser = BlueMaestroBluetoothDeviceData()
    update = parser.update(
        make_bluetooth_service_info(
            name="FABF5A2E",
            manufacturer_data={307: b""},
            address="aa:bb:cc:dd:ee:ff",
            rssi=-65,
            service_data={},
            service_uuids=[],
            source="local",
        )
    )
    assert update == EMPTY_SENSOR_UPDATE


def test_unknown_device_id() -> None:
    """Test an unknown device id is ignored."""
    parser = BlueMaestroBluetoothDeviceData()
    update = parser.update(
        make_bluetooth_service_info(
            name="FABF5A2E",
            manufacturer_data={307: b"\x99d\x02X\n\xd1\x00\xfc\x01\x00"},
            address="aa:bb:cc:dd:ee:ff",
            rssi=-65,
            service_data={},
            service_uuids=[],
            source="local",
        )
    )
    assert update == EMPTY_SENSOR_UPDATE


def test_truncated_payload() -> None:
    """Test a payload shorter than the device struct is ignored."""
    parser = BlueMaestroBluetoothDeviceData()
    update = parser.update(
        make_bluetooth_service_info(
            name="FABF5A2E",
            manufacturer_data={307: b"\rd\x02X"},
            address="aa:bb:cc:dd:ee:ff",
            rssi=-65,
            service_data={},
            service_uuids=[],
            source="local",
        )
    )
    assert update == EMPTY_SENSOR_UPDATE
