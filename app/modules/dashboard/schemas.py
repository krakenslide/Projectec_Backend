from pydantic import BaseModel

class DashboardSummaryReponse(BaseModel):
    total_projects: int
    total_issues: int
    todo_count: int
    in_progress_count: int
    done_count: int
    high_priority_count: int
    my_assigned_count: int