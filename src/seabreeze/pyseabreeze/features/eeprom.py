from __future__ import annotations

import sys
from typing import overload

if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal

from seabreeze.pyseabreeze.exceptions import SeaBreezeError
from seabreeze.pyseabreeze.features._base import SeaBreezeFeature
from seabreeze.pyseabreeze.protocol import OOIProtocol

from seabreeze.pyseabreeze.types import PySeaBreezeProtocol


# Definition
# ==========
#
class SeaBreezeEEPROMFeature(SeaBreezeFeature):
    identifier = "eeprom"

    def eeprom_read_slot(self, slot_number: int, strip_zero_bytes: bool = False) -> str:
        raise NotImplementedError("implement in derived class")


# OOI spectrometer implementation
# ===============================
#
class SeaBreezeEEPromFeatureOOI(SeaBreezeEEPROMFeature):
    _required_protocol_cls = OOIProtocol

    def eeprom_read_slot(self, slot_number: int, strip_zero_bytes: bool = False) -> str:
        return self._func_eeprom_read_slot(
            self.protocol, slot_number, strip_zero_bytes=strip_zero_bytes
        )

    @staticmethod
    def _func_eeprom_read_raw(protocol: PySeaBreezeProtocol, slot_number: int) -> bytes:
        protocol.send(0x05, slot_number)
        ret = protocol.receive(size=17, mode="low_speed")
        if ret[0] != 0x05 or ret[1] != int(slot_number) % 0xFF:
            raise SeaBreezeError(f"read_eeprom_slot_raw: wrong answer: {ret!r}")
        return ret

    @staticmethod
    def _func_eeprom_read_slot(
        protocol: PySeaBreezeProtocol,
        slot_number: int,
        *,
        strip_zero_bytes: bool = False,
    ) -> str:
        ret = SeaBreezeEEPromFeatureOOI._func_eeprom_read_raw(protocol, slot_number)
        data = ret[2 : ret[2:].index(0) + 2].decode("utf-8")
        if not strip_zero_bytes:
            return data
        return data.rstrip("\x00")
