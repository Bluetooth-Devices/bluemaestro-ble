"""Parser for BlueMaestro BLE advertisements.

This file is shamelessly copied from the following repository:
https://github.com/Ernst79/bleparser/blob/c42ae922e1abed2720c7fac993777e1bd59c0c93/package/bleparser/bluemaestro.py

MIT License applies.
"""
from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass
from struct import Struct
from typing import Any

from bluetooth_data_tools import short_address
from bluetooth_sensor_state_data import BluetoothData
from home_assistant_bluetooth import BluetoothServiceInfo
from sensor_state_data import SensorLibrary

_LOGGER = logging.getLogger(__name__)


@dataclass
class BlueMaestroDevice:

    model: str
    unpack: Callable[[bytes], tuple[Any, ...]]


DEVICE_TYPES = {
    0x16: BlueMaestroDevice("Tempo Disc THD", Struct("!BhhhHhH").unpack),
    0x17: BlueMaestroDevice("Tempo Disc THD", Struct("!BhhhHhH").unpack),
    0x1B: BlueMaestroDevice("Tempo Disc THPD", Struct("!BhhhHhH").unpack),
}

MFR_ID = 0x0133


class BlueMaestroBluetoothDeviceData(BluetoothData):
    """Date update for BlueMaestro Bluetooth devices."""

    def _start_update(self, service_info: BluetoothServiceInfo) -> None:
        """Update from BLE advertisement data."""
        _LOGGER.debug("Parsing bluemaestro BLE advertisement data: %s", service_info)
        if MFR_ID not in service_info.manufacturer_data:
            return
        changed_manufacturer_data = self.changed_manufacturer_data(service_info)
        if not changed_manufacturer_data:
            return
        data = changed_manufacturer_data[MFR_ID]
        if len(data) < 14:
            return
        device_id = data[0]
        if device_id not in DEVICE_TYPES:
            return
        device = DEVICE_TYPES[device_id]
        name = device_type = device.model
        self.set_precision(2)
        self.set_device_type(device_type)
        self.set_title(f"{name} {short_address(service_info.address)}")
        self.set_device_name(f"{name} {short_address(service_info.address)}")
        self.set_device_manufacturer("BlueMaestro")
        unpacked = device.unpack(data[1:14])
        if device_id in [0x16, 0x17]:
            (batt, time_interval, log_cnt, temp, humi, dew_point, mode) = unpacked
            self.update_predefined_sensor(
                SensorLibrary.DEW_POINT__TEMP_CELSIUS, dew_point / 10
            )
        elif device_id == 0x1B:
            (batt, time_interval, log_cnt, temp, humi, press, mode) = unpacked
            self.update_predefined_sensor(SensorLibrary.PRESSURE__MBAR, press / 10)
        self.update_predefined_sensor(SensorLibrary.BATTERY__PERCENTAGE, batt)
        self.update_predefined_sensor(SensorLibrary.TEMPERATURE__CELSIUS, temp / 10)
        self.update_predefined_sensor(SensorLibrary.HUMIDITY__PERCENTAGE, humi / 10)
