"""
Parser for BlueMaestro BLE advertisements.

This file is shamelessly copied from the following repository:
https://github.com/Ernst79/bleparser/blob/c42ae922e1abed2720c7fac993777e1bd59c0c93/package/bleparser/bluemaestro.py

MIT License applies.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from struct import Struct

from bluetooth_data_tools import short_address
from bluetooth_sensor_state_data import BluetoothData
from habluetooth import BluetoothServiceInfoBleak
from sensor_state_data import SensorLibrary

_LOGGER = logging.getLogger(__name__)


@dataclass
class BlueMaestroDevice:
    model: str
    struct: Struct


TEMPO_DISC_T_ID = 0x0D
TEMPO_DISC_THD_ID = 0x16
TEMPO_DISC_THD_ALT_ID = 0x17
TEMPO_DISC_THPD_ID = 0x1B

TEMPO_DISC_THD_IDS = frozenset({TEMPO_DISC_THD_ID, TEMPO_DISC_THD_ALT_ID})

DEVICE_TYPES = {
    TEMPO_DISC_T_ID: BlueMaestroDevice("Tempo Disc T", Struct("!BhhhH")),
    TEMPO_DISC_THD_ID: BlueMaestroDevice("Tempo Disc THD", Struct("!BhhhHhH")),
    TEMPO_DISC_THD_ALT_ID: BlueMaestroDevice("Tempo Disc THD", Struct("!BhhhHhH")),
    TEMPO_DISC_THPD_ID: BlueMaestroDevice("Tempo Disc THPD", Struct("!BhhhHhH")),
}

MFR_ID = 0x0133


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
        end = device.struct.size + 1
        if len(data) < end:
            return
        name = device_type = device.model
        self.set_precision(2)
        self.set_device_type(device_type)
        self.set_title(f"{name} {short_address(service_info.address)}")
        self.set_device_name(f"{name} {short_address(service_info.address)}")
        self.set_device_manufacturer("BlueMaestro")
        unpacked = device.struct.unpack(data[1:end])
        if device_id == TEMPO_DISC_T_ID:
            batt, _time_interval, _log_cnt, temp, _mode = unpacked
        elif device_id in TEMPO_DISC_THD_IDS:
            batt, _time_interval, _log_cnt, temp, humi, dew_point, _mode = unpacked
            self.update_predefined_sensor(
                SensorLibrary.DEW_POINT__TEMP_CELSIUS, dew_point / 10
            )
            self.update_predefined_sensor(SensorLibrary.HUMIDITY__PERCENTAGE, humi / 10)
        elif device_id == TEMPO_DISC_THPD_ID:
            batt, _time_interval, _log_cnt, temp, humi, press, _mode = unpacked
            self.update_predefined_sensor(SensorLibrary.PRESSURE__MBAR, press / 10)
            self.update_predefined_sensor(SensorLibrary.HUMIDITY__PERCENTAGE, humi / 10)
        self.update_predefined_sensor(SensorLibrary.BATTERY__PERCENTAGE, batt)
        self.update_predefined_sensor(SensorLibrary.TEMPERATURE__CELSIUS, temp / 10)
