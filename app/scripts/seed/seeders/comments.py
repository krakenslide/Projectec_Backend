import random
from sqlalchemy.orm import Session
from app.models.comment import Comment
from app.scripts.seed.config import (
    MAX_COMMENTS_PER_TICKET,
    MIN_COMMENTS_PER_TICKET,
)
from app.scripts.seed.context import SeedContext

# COMMENT_TEMPLATES = [
#     "Ankit has Started working on this.",
#     "Ankit has Fixed the reported issue.",
#     "Ankit has pushed code for review.",
#     "Ankit has pushed latest changes.",
#     "Ankit needs clarification on the acceptance criteria.",
#     "Ankit has Tested on staging and everything looks good.",
#     "Ankit has Updated according to review comments.",
#     "Ankit is Investigating the root cause.",
#     "Ankit has Reproduced the issue successfully.",
#     "Ankit is Waiting for deployment to production.",
# ]
COMMENT_TEMPLATES = [
    "Assigned to Ankit. ETA: Somewhere between tomorrow and the next sprint.",
    "Ankit said 'it's a 5-minute fix.' We all know what that means.",
    "Waiting for Ankit to stop saying 'works on my machine.'",
    "Ankit has reviewed the code. New bugs have also been reviewed.",
    "The build passed. Ankit is investigating why.",
    "Ankit renamed the variable. Productivity increased by exactly 0%.",
    "Reminder: Never ask Ankit 'one quick question' before lunch.",
    "Merged after Ankit promised he tested it. We admire his confidence.",
    "Issue resolved after convincing Ankit that restarting the server isn't a permanent fix.",
    "Ankit approved the PR with the legendary comment: 'LGTM'... without opening the files.",
    "Ankit is asleep. Please come back later.",
    "Ankit is not in the mood to work he'd rather watch some reels"
]
def seed_comments(
    db: Session,
    context: SeedContext,
) -> None:

    comments: list[Comment] = []

    for ticket in context.tickets:

        project_members = context.project_members.get(
            ticket.project_id,
            [],
        )

        if not project_members:
            continue

        comment_count = random.randint(
            MIN_COMMENTS_PER_TICKET,
            MAX_COMMENTS_PER_TICKET,
        )

        for _ in range(comment_count):

            author = random.choice(project_members)

            comment = Comment(
                ticket_id=ticket.id,
                description = random.choice(COMMENT_TEMPLATES),
                has_attachment=False,
                created_by=author.id,
                updated_by=author.id,
                is_deleted=False,
            )

            comments.append(comment)

    db.add_all(comments)
    db.flush()

    context.comments = comments