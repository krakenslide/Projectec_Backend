from enum import StrEnum


class RoleName(StrEnum):
    OWNER = "Owner"
    ADMINISTRATOR = "Administrator"
    MANAGER = "Manager"
    ENGINEER = "Engineer"
    QA = "QA"
    REPORTER = "Reporter"
    VIEWER = "Viewer"
    GUEST = "Guest"