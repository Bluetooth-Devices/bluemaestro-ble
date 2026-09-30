"""Parser for BlueMaestro BLE advertisements.

Originally based on Ernst79/bleparser's BlueMaestro parser (MIT license).
Current formats are independently implemented from bmLogger advertisement behavior.
"""

from __future__ import annotations

import logging
import math
from collections.abc import Callable
from dataclasses import dataclass
from struct import Struct
from typing import Any

from bluetooth_data_tools import short_address
from bluetooth_sensor_state_data import BluetoothData
from habluetooth import BluetoothServiceInfoBleak
from sensor_state_data import SensorLibrary

_LOGGER = logging.getLogger(__name__)


@dataclass
class BlueMaestroDevice:

    model: str
    unpack: Callable[[bytes], tuple[Any, ...]]
    length: int


DEVICE_TYPES = {
    0x08: BlueMaestroDevice(
        "BlueMaestro Temperature Sensor v8", Struct("!B4xh").unpack, 8
    ),
    0x0D: BlueMaestroDevice("Tempo Disc T", Struct("!B4xh").unpack, 8),
    0x16: BlueMaestroDevice("Tempo Disc THD", Struct("!BhhhHhH").unpack, 14),
    0x17: BlueMaestroDevice("Tempo Disc THD", Struct("!BhhhHhH").unpack, 14),
    0x1B: BlueMaestroDevice("Tempo Disc THPD", Struct("!BhhhHH").unpack, 12),
    0x29: BlueMaestroDevice("Tempo Disc Maxi T", Struct("<B13xh").unpack, 17),
    0x2A: BlueMaestroDevice("Tempo Disc Maxi THD", Struct("<B13xhh").unpack, 19),
    0x2B: BlueMaestroDevice("Tempo Disc Maxi THPD", Struct("<B13xhhi").unpack, 23),
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
        length = device.length
        if len(data) < length:
            return
        name = device_type = device.model
        self.set_precision(2)
        self.set_device_type(device_type)
        self.set_title(f"{name} {short_address(service_info.address)}")
        self.set_device_name(f"{name} {short_address(service_info.address)}")
        self.set_device_manufacturer("BlueMaestro")
        unpacked = device.unpack(data[1:length])
        if device_id in [0x08, 0x0D]:
            batt, temp = unpacked
            self.update_predefined_sensor(SensorLibrary.BATTERY__PERCENTAGE, batt)
            self.update_predefined_sensor(SensorLibrary.TEMPERATURE__CELSIUS, temp / 10)
            return
        if device_id in [0x29, 0x2A, 0x2B]:
            batt, temp = unpacked[:2]
            self.update_predefined_sensor(SensorLibrary.BATTERY__PERCENTAGE, batt)
            self.update_predefined_sensor(
                SensorLibrary.TEMPERATURE__CELSIUS, temp / 100
            )
            if device_id in [0x2A, 0x2B]:
                humi = unpacked[2]
                self.update_predefined_sensor(
                    SensorLibrary.HUMIDITY__PERCENTAGE, humi / 100
                )
                self.update_predefined_sensor(
                    SensorLibrary.DEW_POINT__TEMP_CELSIUS,
                    _dew_point(temp / 100, humi / 100),
                )
            if device_id == 0x2B:
                self.update_predefined_sensor(
                    SensorLibrary.PRESSURE__MBAR, unpacked[3] / 100
                )
            return
        if device_id in [0x16, 0x17]:
            batt, time_interval, log_cnt, temp, humi, dew_point, mode = unpacked
            self.update_predefined_sensor(
                SensorLibrary.DEW_POINT__TEMP_CELSIUS, dew_point / 10
            )
        elif device_id == 0x1B:
            batt, time_interval, log_cnt, temp, humi, press = unpacked
            self.update_predefined_sensor(SensorLibrary.PRESSURE__MBAR, press / 10)
        self.update_predefined_sensor(SensorLibrary.BATTERY__PERCENTAGE, batt)
        self.update_predefined_sensor(SensorLibrary.TEMPERATURE__CELSIUS, temp / 10)
        self.update_predefined_sensor(SensorLibrary.HUMIDITY__PERCENTAGE, humi / 10)
