"""Parser for BlueMaestro BLE advertisements.

Originally based on Ernst79/bleparser's BlueMaestro parser (MIT license).
Current formats are independently implemented from bmLogger advertisement behavior.
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass
from typing import Literal

from bluetooth_data_tools import short_address
from bluetooth_sensor_state_data import BluetoothData
from habluetooth import BluetoothServiceInfoBleak
from sensor_state_data import SensorLibrary

_LOGGER = logging.getLogger(__name__)
MFR_ID = 0x0133


@dataclass(frozen=True)
class BlueMaestroDevice:
    """An advertisement version and its minimum measurement payload."""

    model: str
    length: int
    humidity: bool = False
    pressure: bool = False
    modern: bool = False


DEVICE_TYPES = {
    0x08: BlueMaestroDevice("BlueMaestro Temperature Sensor v8", 8),
    0x0D: BlueMaestroDevice("Tempo Disc T", 8),
    # Retain the previously supported format; bmLogger no longer dispatches it.
    0x16: BlueMaestroDevice("Tempo Disc THD", 14, humidity=True),
    0x17: BlueMaestroDevice("Tempo Disc THD", 10, humidity=True),
    0x1B: BlueMaestroDevice("Tempo Disc THPD", 12, humidity=True, pressure=True),
    0x29: BlueMaestroDevice("Tempo Disc Maxi T", 17, modern=True),
    0x2A: BlueMaestroDevice("Tempo Disc Maxi THD", 19, humidity=True, modern=True),
    0x2B: BlueMaestroDevice(
        "Tempo Disc Maxi THPD", 23, humidity=True, pressure=True, modern=True
    ),
}


def _dew_point(temperature: float, humidity: float, scale: int) -> float | None:
    """Calculate dew point with bmLogger's constants and rounding."""
    if not 0 < humidity <= 100 or temperature == -243.5:
        return None
    alpha = math.log(humidity / 100) + 17.67 * temperature / (temperature + 243.5)
    if alpha == 17.67:
        return None
    result = 243.5 * alpha / (17.67 - alpha)
    return math.floor(result * scale + 0.5) / scale


class BlueMaestroBluetoothDeviceData(BluetoothData):
    """Update sensor data from BlueMaestro Bluetooth advertisements."""

    def _start_update(self, service_info: BluetoothServiceInfoBleak) -> None:
        """Update from BLE advertisement data."""
        if MFR_ID not in service_info.manufacturer_data:
            return
        changed = self.changed_manufacturer_data(service_info)
        # Multiple changed manufacturers may contain stale data after an adapter switch.
        if len(changed) != 1 or MFR_ID not in changed:
            return
        data = changed[MFR_ID]
        if not data or (device := DEVICE_TYPES.get(data[0])) is None:
            return
        if len(data) < device.length:
            _LOGGER.debug(
                "Incomplete BlueMaestro v%s advertisement: %s bytes", data[0], len(data)
            )
            return

        name = f"{device.model} {short_address(service_info.address)}"
        self.set_precision(2)
        self.set_device_type(device.model)
        self.set_title(name)
        self.set_device_name(name)
        self.set_device_manufacturer("BlueMaestro")

        offset = 15 if device.modern else 6
        order: Literal["little", "big"] = "little" if device.modern else "big"
        scale = 100 if device.modern else 10
        temperature = (
            int.from_bytes(data[offset : offset + 2], order, signed=True) / scale
        )
        self.update_predefined_sensor(SensorLibrary.BATTERY__PERCENTAGE, data[1])
        self.update_predefined_sensor(SensorLibrary.TEMPERATURE__CELSIUS, temperature)
        if device.humidity:
            humidity = (
                int.from_bytes(
                    data[offset + 2 : offset + 4], order, signed=device.modern
                )
                / scale
            )
            self.update_predefined_sensor(SensorLibrary.HUMIDITY__PERCENTAGE, humidity)
            dew_point: float | None
            if data[0] == 0x16:
                dew_point = int.from_bytes(data[10:12], "big", signed=True) / 10
            else:
                dew_point = _dew_point(temperature, humidity, scale)
            # Publish None too, so a dry reading clears an earlier finite dew point.
            self.update_predefined_sensor(
                SensorLibrary.DEW_POINT__TEMP_CELSIUS, dew_point
            )
        if device.pressure:
            size = 4 if device.modern else 2
            pressure = (
                int.from_bytes(
                    data[offset + 4 : offset + 4 + size], order, signed=device.modern
                )
                / scale
            )
            self.update_predefined_sensor(SensorLibrary.PRESSURE__MBAR, pressure)
