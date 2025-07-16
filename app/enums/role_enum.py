from enum import Enum


class RoleEnum(str, Enum):
    ADMIN = "Admin"
    SECURITY = "Security"
    POLICE = "Police"
    ATTENDANT = "Attendant"
