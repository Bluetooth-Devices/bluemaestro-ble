# bluemaestro-ble

<p align="center">
  <a href="https://github.com/bluetooth-devices/bluemaestro-ble/actions?query=workflow%3ACI">
    <img src="https://img.shields.io/github/actions/workflow/status/bluetooth-devices/bluemaestro-ble/ci.yml?branch=main&label=CI&logo=github&style=flat-square" alt="CI Status" >
  </a>
  <a href="https://bluemaestro-ble.readthedocs.io">
    <img src="https://img.shields.io/readthedocs/bluemaestro-ble.svg?logo=read-the-docs&logoColor=fff&style=flat-square" alt="Documentation Status">
  </a>
  <a href="https://codecov.io/gh/bluetooth-devices/bluemaestro-ble">
    <img src="https://img.shields.io/codecov/c/github/bluetooth-devices/bluemaestro-ble.svg?logo=codecov&logoColor=fff&style=flat-square" alt="Test coverage percentage">
  </a>
</p>
<p align="center">
  <a href="https://python-poetry.org/">
    <img src="https://img.shields.io/badge/packaging-poetry-299bd7?style=flat-square&logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA4AAAASCAYAAABrXO8xAAAACXBIWXMAAAsTAAALEwEAmpwYAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAJJSURBVHgBfZLPa1NBEMe/s7tNXoxW1KJQKaUHkXhQvHgW6UHQQ09CBS/6V3hKc/AP8CqCrUcpmop3Cx48eDB4yEECjVQrlZb80CRN8t6OM/teagVxYZi38+Yz853dJbzoMV3MM8cJUcLMSUKIE8AzQ2PieZzFxEJOHMOgMQQ+dUgSAckNXhapU/NMhDSWLs1B24A8sO1xrN4NECkcAC9ASkiIJc6k5TRiUDPhnyMMdhKc+Zx19l6SgyeW76BEONY9exVQMzKExGKwwPsCzza7KGSSWRWEQhyEaDXp6ZHEr416ygbiKYOd7TEWvvcQIeusHYMJGhTwF9y7sGnSwaWyFAiyoxzqW0PM/RjghPxF2pWReAowTEXnDh0xgcLs8l2YQmOrj3N7ByiqEoH0cARs4u78WgAVkoEDIDoOi3AkcLOHU60RIg5wC4ZuTC7FaHKQm8Hq1fQuSOBvX/sodmNJSB5geaF5CPIkUeecdMxieoRO5jz9bheL6/tXjrwCyX/UYBUcjCaWHljx1xiX6z9xEjkYAzbGVnB8pvLmyXm9ep+W8CmsSHQQY77Zx1zboxAV0w7ybMhQmfqdmmw3nEp1I0Z+FGO6M8LZdoyZnuzzBdjISicKRnpxzI9fPb+0oYXsNdyi+d3h9bm9MWYHFtPeIZfLwzmFDKy1ai3p+PDls1Llz4yyFpferxjnyjJDSEy9CaCx5m2cJPerq6Xm34eTrZt3PqxYO1XOwDYZrFlH1fWnpU38Y9HRze3lj0vOujZcXKuuXm3jP+s3KbZVra7y2EAAAAAASUVORK5CYII=" alt="Poetry">
  </a>
  <a href="https://github.com/astral-sh/ruff">
    <img src="https://img.shields.io/badge/code%20style-ruff-261230.svg?style=flat-square" alt="Ruff">
  </a>
  <a href="https://github.com/pre-commit/pre-commit">
    <img src="https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white&style=flat-square" alt="pre-commit">
  </a>
</p>
<p align="center">
  <a href="https://pypi.org/project/bluemaestro-ble/">
    <img src="https://img.shields.io/pypi/v/bluemaestro-ble.svg?logo=python&logoColor=fff&style=flat-square" alt="PyPI Version">
  </a>
  <img src="https://img.shields.io/pypi/pyversions/bluemaestro-ble.svg?style=flat-square&logo=python&amp;logoColor=fff" alt="Supported Python versions">
  <img src="https://img.shields.io/pypi/l/bluemaestro-ble.svg?style=flat-square" alt="License">
</p>

A Python library for decoding BlueMaestro Bluetooth Low Energy sensor advertisements.

## Supported advertisement formats

| Version | Device family                         | Readings                                                       |
| ------- | ------------------------------------- | -------------------------------------------------------------- |
| 8       | Legacy BlueMaestro temperature sensor | Temperature, battery                                           |
| 13      | Tempo Disc / Disc Mini temperature    | Temperature, battery                                           |
| 22      | Legacy Tempo Disc THD                 | Temperature, humidity, transmitted dew point, battery          |
| 23      | Tempo Disc THD / Disc Mini 3-in-1     | Temperature, humidity, transmitted dew point, battery          |
| 27      | Tempo Disc THPD / Disc Mini 4-in-1    | Temperature, humidity, pressure, battery                       |
| 41      | Disc Maxi temperature                 | Temperature, battery                                           |
| 42      | Disc Maxi 3-in-1                      | Temperature, humidity, calculated dew point, battery           |
| 43      | Disc Maxi 4-in-1                      | Temperature, humidity, pressure, calculated dew point, battery |

All devices also expose signal strength. Versions 22/23 use transmitted dew point;
Maxi 3-in-1/4-in-1 calculate it and report unknown at zero humidity. Truncated
packets are ignored and trailing data is accepted.

New formats were checked against synthetic bmLogger 13.8.4 readings. Physical
v13/v23 packets were also tested; other formats remain unverified on hardware.
Version 8's exact commercial model name is unconfirmed. See
[fixture provenance](tests/fixtures/README.md) for validation details.

## Installation

Install this via pip (or your favourite package manager):

`pip install bluemaestro-ble`

## Contributors ✨

Thanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):

<!-- prettier-ignore-start -->
<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- markdownlint-disable -->
<!-- markdownlint-enable -->
<!-- ALL-CONTRIBUTORS-LIST:END -->
<!-- prettier-ignore-end -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!

## Credits

This package was created with
[Cookiecutter](https://github.com/audreyr/cookiecutter) and the
[browniebroke/cookiecutter-pypackage](https://github.com/browniebroke/cookiecutter-pypackage)
project template.
