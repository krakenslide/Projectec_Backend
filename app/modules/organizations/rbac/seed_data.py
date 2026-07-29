from .permissions import PermissionName
from .roles import OrganizationRole, ProjectRole

DEFAULT_PERMISSIONS = [permission.value for permission in PermissionName]

DEFAULT_ORGANIZATION_ROLE_PERMISSIONS = {

    OrganizationRole.OWNER: [
        PermissionName.ORGANIZATION_VIEW,
        PermissionName.ORGANIZATION_CREATE,
        PermissionName.ORGANIZATION_UPDATE,
        PermissionName.ORGANIZATION_DELETE,

        PermissionName.ORGANIZATION_MEMBER_VIEW,
        PermissionName.ORGANIZATION_MEMBER_ADD,
        PermissionName.ORGANIZATION_MEMBER_REMOVE,

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

        PermissionName.TEAM_VIEW,
        PermissionName.TEAM_CREATE,
        PermissionName.TEAM_UPDATE,
        PermissionName.TEAM_DELETE,

        PermissionName.PROJECT_CREATE,
        PermissionName.PROJECT_DELETE,

        PermissionName.DASHBOARD_VIEW,
        PermissionName.REPORT_VIEW,
        PermissionName.REPORT_EXPORT,

        PermissionName.AUDIT_LOG_VIEW,
    ],

    OrganizationRole.ADMINISTRATOR: [
        PermissionName.ORGANIZATION_VIEW,
        PermissionName.ORGANIZATION_UPDATE,

        PermissionName.ORGANIZATION_MEMBER_VIEW,
        PermissionName.ORGANIZATION_MEMBER_ADD,
        PermissionName.ORGANIZATION_MEMBER_REMOVE,

        PermissionName.USER_VIEW,
        PermissionName.USER_CREATE,
        PermissionName.USER_UPDATE,
        PermissionName.USER_INVITE,
        PermissionName.USER_REMOVE,

        PermissionName.ROLE_VIEW,
        PermissionName.ROLE_CREATE,
        PermissionName.ROLE_UPDATE,
        PermissionName.ROLE_ASSIGN,

        PermissionName.TEAM_VIEW,
        PermissionName.TEAM_CREATE,
        PermissionName.TEAM_UPDATE,

        PermissionName.PROJECT_CREATE,

        PermissionName.DASHBOARD_VIEW,
        PermissionName.REPORT_VIEW,
    ],

    OrganizationRole.MEMBER: [
        PermissionName.ORGANIZATION_VIEW,
        PermissionName.DASHBOARD_VIEW,
    ],
}


DEFAULT_PROJECT_ROLE_PERMISSIONS = {

    ProjectRole.PROJECT_OWNER: [
        PermissionName.PROJECT_VIEW,
        PermissionName.PROJECT_UPDATE,

        PermissionName.PROJECT_MEMBER_VIEW,
        PermissionName.PROJECT_MEMBER_ADD,
        PermissionName.PROJECT_MEMBER_REMOVE,

        PermissionName.TICKET_VIEW,
        PermissionName.TICKET_CREATE,
        PermissionName.TICKET_UPDATE,
        PermissionName.TICKET_ASSIGN,
        PermissionName.TICKET_CLOSE,
        PermissionName.TICKET_REOPEN,
        PermissionName.TICKET_DELETE,

        PermissionName.COMMENT_VIEW,
        PermissionName.COMMENT_CREATE,
        PermissionName.COMMENT_UPDATE,
        PermissionName.COMMENT_DELETE,

        PermissionName.ATTACHMENT_VIEW,
        PermissionName.ATTACHMENT_UPLOAD,
        PermissionName.ATTACHMENT_DELETE,

        PermissionName.LABEL_VIEW,
        PermissionName.LABEL_CREATE,
        PermissionName.LABEL_UPDATE,
        PermissionName.LABEL_DELETE,

        PermissionName.WORKFLOW_VIEW,
        PermissionName.WORKFLOW_CREATE,
        PermissionName.WORKFLOW_UPDATE,
        PermissionName.WORKFLOW_DELETE,
    ],

    ProjectRole.PROJECT_ADMIN: [
        PermissionName.PROJECT_VIEW,
        PermissionName.PROJECT_UPDATE,

        PermissionName.PROJECT_MEMBER_VIEW,
        PermissionName.PROJECT_MEMBER_ADD,
        PermissionName.PROJECT_MEMBER_REMOVE,

        PermissionName.TICKET_VIEW,
        PermissionName.TICKET_CREATE,
        PermissionName.TICKET_UPDATE,
        PermissionName.TICKET_ASSIGN,
        PermissionName.TICKET_CLOSE,
        PermissionName.TICKET_REOPEN,

        PermissionName.COMMENT_VIEW,
        PermissionName.COMMENT_CREATE,
        PermissionName.COMMENT_UPDATE,

        PermissionName.ATTACHMENT_VIEW,
        PermissionName.ATTACHMENT_UPLOAD,

        PermissionName.LABEL_VIEW,
        PermissionName.LABEL_CREATE,
        PermissionName.LABEL_UPDATE,

        PermissionName.WORKFLOW_VIEW,
        PermissionName.WORKFLOW_UPDATE,
    ],

    ProjectRole.ENGINEER: [
        PermissionName.PROJECT_VIEW,

        PermissionName.TICKET_VIEW,
        PermissionName.TICKET_CREATE,
        PermissionName.TICKET_UPDATE,
        PermissionName.TICKET_CLOSE,

        PermissionName.COMMENT_VIEW,
        PermissionName.COMMENT_CREATE,
        PermissionName.COMMENT_UPDATE,

        PermissionName.ATTACHMENT_VIEW,
        PermissionName.ATTACHMENT_UPLOAD,
    ],

    ProjectRole.QA: [
        PermissionName.PROJECT_VIEW,

        PermissionName.TICKET_VIEW,
        PermissionName.TICKET_UPDATE,
        PermissionName.TICKET_CLOSE,
        PermissionName.TICKET_REOPEN,

        PermissionName.COMMENT_VIEW,
        PermissionName.COMMENT_CREATE,

        PermissionName.ATTACHMENT_VIEW,
        PermissionName.ATTACHMENT_UPLOAD,
    ],

    ProjectRole.REPORTER: [
        PermissionName.PROJECT_VIEW,

        PermissionName.TICKET_VIEW,
        PermissionName.TICKET_CREATE,

        PermissionName.COMMENT_VIEW,
        PermissionName.COMMENT_CREATE,

        PermissionName.ATTACHMENT_VIEW,
        PermissionName.ATTACHMENT_UPLOAD,
    ],

    ProjectRole.VIEWER: [
        PermissionName.PROJECT_VIEW,

        PermissionName.TICKET_VIEW,

        PermissionName.COMMENT_VIEW,

        PermissionName.ATTACHMENT_VIEW,
    ],
}