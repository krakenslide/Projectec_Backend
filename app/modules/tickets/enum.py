from enum import StrEnum


class TicketStatus(StrEnum):
    TODO = "To Do"
    IN_PROGRESS = "In Progress"
    IN_REVIEW = "In Review"
    TESTING = "Testing"
    DONE = "Done"
    CLOSED = "Closed"


class TicketPriority(StrEnum):
    P0 = "P0"
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"
    P4 = "P4"


class TicketType(StrEnum):
    FEATURE = "Feature"
    BUG = "Bug"
    TASK = "Task"
    IMPROVEMENT = "Improvement"
