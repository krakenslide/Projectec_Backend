from .permissions import PermissionName
from .roles import RoleName

DEFAULT_ROLES = [ role.value for role in RoleName ]

DEFAULT_PERMISSIONS = [ permission.value for permission in PermissionName ]

DEFAULT_ROLE_PERMISSIONS = {

    RoleName.OWNER: [
        PermissionName.ORGANIZATION_VIEW,
        PermissionName.ORGANIZATION_CREATE,
        PermissionName.ORGANIZATION_UPDATE,
        PermissionName.ORGANIZATION_DELETE,

        PermissionName.USER_VIEW,
        PermissionName.USER_CREATE,
        PermissionName.USER_UPDATE,
        PermissionName.USER_INVITE,
        PermissionName.USER_REMOVE,

        PermissionName.ROLE_VIEW,
        PermissionName.ROLE_CREATE,
        PermissionName.ROLE_UPDATE,
        PermissionName.ROLE_DELETE,
        PermissionName.ROLE_ASSIGN,

        PermissionName.PROJECT_VIEW,
        PermissionName.PROJECT_CREATE,
        PermissionName.PROJECT_UPDATE,
        PermissionName.PROJECT_DELETE,

        PermissionName.TICKET_VIEW,
        PermissionName.TICKET_CREATE,
        PermissionName.TICKET_UPDATE,
        PermissionName.TICKET_ASSIGN,
        PermissionName.TICKET_CLOSE,
        PermissionName.TICKET_REOPEN,
        PermissionName.TICKET_DELETE,
    ],

    RoleName.ADMINISTRATOR: [

        PermissionName.ORGANIZATION_VIEW,
        PermissionName.ORGANIZATION_UPDATE,

        PermissionName.USER_VIEW,
        PermissionName.USER_CREATE,
        PermissionName.USER_UPDATE,
        PermissionName.USER_INVITE,
        PermissionName.USER_REMOVE,

        PermissionName.ROLE_VIEW,
        PermissionName.ROLE_CREATE,
        PermissionName.ROLE_UPDATE,
        PermissionName.ROLE_ASSIGN,

        PermissionName.PROJECT_VIEW,
        PermissionName.PROJECT_CREATE,
        PermissionName.PROJECT_UPDATE,
        PermissionName.PROJECT_DELETE,

        PermissionName.TICKET_VIEW,
        PermissionName.TICKET_CREATE,
        PermissionName.TICKET_UPDATE,
        PermissionName.TICKET_ASSIGN,
        PermissionName.TICKET_CLOSE,
        PermissionName.TICKET_REOPEN,
        PermissionName.TICKET_DELETE,
    ],

    RoleName.MANAGER: [

        PermissionName.PROJECT_VIEW,
        PermissionName.PROJECT_UPDATE,

        PermissionName.TICKET_VIEW,
        PermissionName.TICKET_CREATE,
        PermissionName.TICKET_UPDATE,
        PermissionName.TICKET_ASSIGN,
        PermissionName.TICKET_CLOSE,
        PermissionName.TICKET_REOPEN,
    ],

    RoleName.ENGINEER: [

        PermissionName.TICKET_VIEW,
        PermissionName.TICKET_CREATE,
        PermissionName.TICKET_UPDATE,
        PermissionName.TICKET_CLOSE,
    ],

    RoleName.QA: [

        PermissionName.TICKET_VIEW,
        PermissionName.TICKET_UPDATE,
        PermissionName.TICKET_CLOSE,
        PermissionName.TICKET_REOPEN,
    ],

    RoleName.REPORTER: [

        PermissionName.TICKET_VIEW,
        PermissionName.TICKET_CREATE,
    ],

    RoleName.VIEWER: [

        PermissionName.ORGANIZATION_VIEW,
        PermissionName.PROJECT_VIEW,
        PermissionName.TICKET_VIEW,
    ],

    RoleName.GUEST: [

        PermissionName.TICKET_VIEW,
    ],
}