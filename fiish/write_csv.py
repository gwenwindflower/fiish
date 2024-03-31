import csv
import os
from pathlib import Path


def write_csv(comments) -> Path:
    csv_filename = "issue_comments.csv"
    fieldnames = ["id", "issue_url", "user", "created_at", "updated_at", "body"]

    this = Path(__file__).resolve()
    csv_filename = this.parent / csv_filename
    # TODO: Build incremental loading,
    # for now we explicitly remove the old file if it exists
    # because I don't know what will happen otherwise yet
    os.remove(csv_filename) if os.path.exists(csv_filename) else None
    with open(csv_filename, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for comment in comments:
            writer.writerow(
                {
                    "id": comment["id"],
                    "issue_url": comment["issue_url"]
                    .replace("api.", "")
                    .replace("repos/", ""),
                    "user": comment["user"]["login"],
                    "created_at": comment["created_at"],
                    "updated_at": comment["updated_at"],
                    "body": comment["body"],
                }
            )
    return csv_filename
