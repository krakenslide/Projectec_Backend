from enum import StrEnum


class PermissionName(StrEnum):
    # ==========================================================
    # Organization
    # ==========================================================

    ORGANIZATION_VIEW = "organization:view"
    ORGANIZATION_CREATE = "organization:create"
    ORGANIZATION_UPDATE = "organization:update"
    ORGANIZATION_DELETE = "organization:delete"

    ORGANIZATION_MEMBER_VIEW = "organization_member:view"
    ORGANIZATION_MEMBER_ADD = "organization_member:add"
    ORGANIZATION_MEMBER_REMOVE = "organization_member:remove"

    # ==========================================================
    # User
    # ==========================================================

    USER_VIEW = "user:view"
    USER_CREATE = "user:create"
    USER_UPDATE = "user:update"
    USER_INVITE = "user:invite"
    USER_REMOVE = "user:remove"

    # ==========================================================
    # Role
    # ==========================================================

    ROLE_VIEW = "role:view"
    ROLE_CREATE = "role:create"
    ROLE_UPDATE = "role:update"
    ROLE_DELETE = "role:delete"
    ROLE_ASSIGN = "role:assign"

    # ==========================================================
    # Team
    # ==========================================================

    TEAM_VIEW = "team:view"
    TEAM_CREATE = "team:create"
    TEAM_UPDATE = "team:update"
    TEAM_DELETE = "team:delete"

    # ==========================================================
    # Project
    # ==========================================================

    PROJECT_VIEW = "project:view"
    PROJECT_CREATE = "project:create"
    PROJECT_UPDATE = "project:update"
    PROJECT_DELETE = "project:delete"

    PROJECT_MEMBER_VIEW = "project_member:view"
    PROJECT_MEMBER_ADD = "project_member:add"
    PROJECT_MEMBER_REMOVE = "project_member:remove"

    # ==========================================================
    # Ticket
    # ==========================================================

    TICKET_VIEW = "ticket:view"
    TICKET_CREATE = "ticket:create"
    TICKET_UPDATE = "ticket:update"
    TICKET_ASSIGN = "ticket:assign"
    TICKET_CLOSE = "ticket:close"
    TICKET_REOPEN = "ticket:reopen"
    TICKET_DELETE = "ticket:delete"

    # ==========================================================
    # Comment
    # ==========================================================

    COMMENT_VIEW = "comment:view"
    COMMENT_CREATE = "comment:create"
    COMMENT_UPDATE = "comment:update"
    COMMENT_DELETE = "comment:delete"

    # ==========================================================
    # Attachment
    # ==========================================================

    ATTACHMENT_VIEW = "attachment:view"
    ATTACHMENT_UPLOAD = "attachment:upload"
    ATTACHMENT_DELETE = "attachment:delete"

    # ==========================================================
    # Label
    # ==========================================================

    LABEL_VIEW = "label:view"
    LABEL_CREATE = "label:create"
    LABEL_UPDATE = "label:update"
    LABEL_DELETE = "label:delete"

    # ==========================================================
    # Workflow
    # ==========================================================

    WORKFLOW_VIEW = "workflow:view"
    WORKFLOW_CREATE = "workflow:create"
    WORKFLOW_UPDATE = "workflow:update"
    WORKFLOW_DELETE = "workflow:delete"

    # ==========================================================
    # Dashboard
    # ==========================================================

    DASHBOARD_VIEW = "dashboard:view"

    # ==========================================================
    # Reports
    # ==========================================================

    REPORT_VIEW = "report:view"
    REPORT_EXPORT = "report:export"

    # ==========================================================
    # Knowledge Base
    # ==========================================================

    KNOWLEDGE_BASE_VIEW = "knowledge_base:view"
    KNOWLEDGE_BASE_CREATE = "knowledge_base:create"
    KNOWLEDGE_BASE_UPDATE = "knowledge_base:update"
    KNOWLEDGE_BASE_DELETE = "knowledge_base:delete"

    # ==========================================================
    # Automation
    # ==========================================================

    AUTOMATION_VIEW = "automation:view"
    AUTOMATION_CREATE = "automation:create"
    AUTOMATION_UPDATE = "automation:update"
    AUTOMATION_DELETE = "automation:delete"

    # ==========================================================
    # Notification
    # ==========================================================

    NOTIFICATION_VIEW = "notification:view"
    NOTIFICATION_SEND = "notification:send"

    # ==========================================================
    # API Tokens
    # ==========================================================

    API_TOKEN_VIEW = "api_token:view"
    API_TOKEN_CREATE = "api_token:create"
    API_TOKEN_DELETE = "api_token:delete"

    # ==========================================================
    # Audit Logs
    # ==========================================================

    AUDIT_LOG_VIEW = "audit_log:view"

    # ==========================================================
    # Integrations
    # ==========================================================

    INTEGRATION_VIEW = "integration:view"
    INTEGRATION_CREATE = "integration:create"
    INTEGRATION_UPDATE = "integration:update"
    INTEGRATION_DELETE = "integration:delete"
