"""
Parser for BlueMaestro BLE advertisements.

This file is shamelessly copied from the following repository:
https://github.com/Ernst79/bleparser/blob/c42ae922e1abed2720c7fac993777e1bd59c0c93/package/bleparser/bluemaestro.py

MIT License applies.
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass
from struct import Struct

from bluetooth_data_tools import short_address
from bluetooth_sensor_state_data import BluetoothData
from habluetooth import BluetoothServiceInfoBleak
from sensor_state_data import SensorLibrary
from sensor_state_data.description import BaseSensorDescription

_LOGGER = logging.getLogger(__name__)


@dataclass
class BlueMaestroDevice:
    model: str
    # Every struct ends at its last decoded field; trailing advertisement
    # bytes are statistics the parser does not read.
    struct: Struct
    # One (sensor description, divisor) pair per unpacked struct field, in order.
    fields: tuple[tuple[BaseSensorDescription, int], ...]
    calculated_dew_point: bool = False


TEMPERATURE_SENSOR_V8_ID = 0x08
TEMPO_DISC_T_ID = 0x0D
TEMPO_DISC_THD_LEGACY_ID = 0x16
TEMPO_DISC_THD_ID = 0x17
TEMPO_DISC_THPD_ID = 0x1B
TEMPO_DISC_MAXI_T_ID = 0x29
TEMPO_DISC_MAXI_THD_ID = 0x2A
TEMPO_DISC_MAXI_THPD_ID = 0x2B

_T_FIELDS = (
    (SensorLibrary.BATTERY__PERCENTAGE, 1),
    (SensorLibrary.TEMPERATURE__CELSIUS, 10),
)
_THD_FIELDS = (
    (SensorLibrary.BATTERY__PERCENTAGE, 1),
    (SensorLibrary.TEMPERATURE__CELSIUS, 10),
    (SensorLibrary.HUMIDITY__PERCENTAGE, 10),
    (SensorLibrary.DEW_POINT__TEMP_CELSIUS, 10),
)
_THPD_FIELDS = (
    (SensorLibrary.BATTERY__PERCENTAGE, 1),
    (SensorLibrary.TEMPERATURE__CELSIUS, 10),
    (SensorLibrary.HUMIDITY__PERCENTAGE, 10),
    (SensorLibrary.PRESSURE__MBAR, 10),
)
_MAXI_T_FIELDS = (
    (SensorLibrary.BATTERY__PERCENTAGE, 1),
    (SensorLibrary.TEMPERATURE__CELSIUS, 100),
)
_MAXI_THD_FIELDS = (
    *_MAXI_T_FIELDS,
    (SensorLibrary.HUMIDITY__PERCENTAGE, 100),
)
_MAXI_THPD_FIELDS = (
    *_MAXI_THD_FIELDS,
    (SensorLibrary.PRESSURE__MBAR, 100),
)

_THD = BlueMaestroDevice("Tempo Disc THD", Struct("!B4xhHh"), _THD_FIELDS)

DEVICE_TYPES = {
    TEMPERATURE_SENSOR_V8_ID: BlueMaestroDevice(
        "BlueMaestro Temperature Sensor v8", Struct("!B4xh"), _T_FIELDS
    ),
    TEMPO_DISC_T_ID: BlueMaestroDevice("Tempo Disc T", Struct("!B4xh"), _T_FIELDS),
    TEMPO_DISC_THD_LEGACY_ID: _THD,
    TEMPO_DISC_THD_ID: _THD,
    TEMPO_DISC_THPD_ID: BlueMaestroDevice(
        "Tempo Disc THPD", Struct("!B4xhHH"), _THPD_FIELDS
    ),
    TEMPO_DISC_MAXI_T_ID: BlueMaestroDevice(
        "Tempo Disc Maxi T", Struct("<B13xh"), _MAXI_T_FIELDS
    ),
    TEMPO_DISC_MAXI_THD_ID: BlueMaestroDevice(
        "Tempo Disc Maxi THD",
        Struct("<B13xhh"),
        _MAXI_THD_FIELDS,
        calculated_dew_point=True,
    ),
    TEMPO_DISC_MAXI_THPD_ID: BlueMaestroDevice(
        "Tempo Disc Maxi THPD",
        Struct("<B13xhhi"),
        _MAXI_THPD_FIELDS,
        calculated_dew_point=True,
    ),
}

MFR_ID = 0x0133


def _dew_point(temperature: float, humidity: float) -> float | None:
    """Calculate dew point for Maxi formats that do not transmit it."""
    if not 0 < humidity <= 100 or temperature == -243.5:
        return None
    alpha = math.log(humidity / 100) + 17.67 * temperature / (temperature + 243.5)
    return math.floor(243.5 * alpha / (17.67 - alpha) * 100 + 0.5) / 100


class BlueMaestroBluetoothDeviceData(BluetoothData):
    """Date update for BlueMaestro Bluetooth devices."""

    def _start_update(self, service_info: BluetoothServiceInfoBleak) -> None:
        """Update from BLE advertisement data."""
        _LOGGER.debug("Parsing bluemaestro BLE advertisement data: %s", service_info)
        if MFR_ID not in service_info.manufacturer_data:
            return
        changed_manufacturer_data = self.changed_manufacturer_data(service_info)
        if not changed_manufacturer_data or len(changed_manufacturer_data) > 1:
            # If len(changed_manufacturer_data) > 1 it means we switched
            # ble adapters so we do not know which data is the latest
            # and we need to wait for the next update.
            return
        if MFR_ID not in changed_manufacturer_data:
            return
        data = changed_manufacturer_data[MFR_ID]
        if not data:
            return
        device_id = data[0]
        if device_id not in DEVICE_TYPES:
            return
        device = DEVICE_TYPES[device_id]
        struct = device.struct
        if len(data) <= struct.size:
            return
        name = device_type = device.model
        short_addr = short_address(service_info.address)
        self.set_precision(2)
        self.set_device_type(device_type)
        self.set_title(f"{name} {short_addr}")
        self.set_device_name(f"{name} {short_addr}")
        self.set_device_manufacturer("BlueMaestro")
        values: dict[BaseSensorDescription, float] = {}
        for (description, divisor), raw in zip(
            device.fields, struct.unpack_from(data, 1), strict=True
        ):
            value = raw / divisor if divisor != 1 else raw
            values[description] = value
            self.update_predefined_sensor(description, value)
        if device.calculated_dew_point:
            self.update_predefined_sensor(
                SensorLibrary.DEW_POINT__TEMP_CELSIUS,
                _dew_point(
                    values[SensorLibrary.TEMPERATURE__CELSIUS],
                    values[SensorLibrary.HUMIDITY__PERCENTAGE],
                ),
            )
