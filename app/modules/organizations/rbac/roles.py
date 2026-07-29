from enum import StrEnum

class ProjectRole(StrEnum):
    PROJECT_OWNER = "Project Owner"
    PROJECT_ADMIN = "Project Admin"
    ENGINEER = "Engineer"
    QA = "QA"
    REPORTER = "Reporter"
    VIEWER = "Viewer"

class OrganizationRole(StrEnum):
    OWNER = "Owner"
    ADMINISTRATOR = "Administrator"
    MEMBER = "Member"

class RoleType(StrEnum):
    ORGANIZATION = "organization"
    PROJECT = "project"