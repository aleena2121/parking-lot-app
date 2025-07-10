from enum import Enum


class VehicleEnum(str, Enum):
    TWOWHEELER = "2-Wheeler"
    THREEWHEELER = "3-Wheeler"
    FOURWHEELER = "4-Wheeler"
    LARGE = "Large"
