from enum import Enum


class RoleEnum(str, Enum):
    ADMIN = "Admin"
    SECURITY = "Security"
    CUSTOMER = "Customer"
    ATTENDANT = "Attendant"
