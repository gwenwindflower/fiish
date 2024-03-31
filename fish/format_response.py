from rich.text import Text
from rich.panel import Panel
from datetime import datetime


def format_response(answer) -> tuple[Panel, Panel]:
    model_output: str = answer["model_output"]
    referenced_issues = answer["references"]

    issue_references: str = ""
    for issue in referenced_issues:
        timestamp = datetime.strptime(
            issue.metadata["updated_at"], "%Y-%m-%dT%H:%M:%SZ"
        )
        formatted_date = timestamp.strftime("%Y-%m-%d")
        issue_references += f"""- {issue.metadata['issue_url']} from {issue.metadata['user']} on {formatted_date}
"""

    summary: Text = Text(model_output)
    references: Text = Text(issue_references)
    summary_panel: Panel = Panel(
        Text.assemble(summary),
        width=80,
        title="📝Model summary✨",
    )
    references_panel: Panel = Panel(
        Text.assemble(references),
        width=80,
        title="📚Based on these issues🔍",
    )
    return summary_panel, references_panel
