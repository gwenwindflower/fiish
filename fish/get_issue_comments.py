import os
import requests
import csv
from pathlib import Path


def get_issue_comments():
    # Constants
    REPO_OWNER = "dbt-labs"
    REPO_NAME = "dbt-core"
    URL = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues/comments"
    USERS = ["jtcohen6", "dbeatty10", "MichelleArk", "graciegoheen"]
    HEADERS = {
        "Authorization": f"Bearer {os.environ['GITHUB_PERSONAL_ACCESS_TOKEN']}",
        "Accept": "application/vnd.github+json",
    }
    PARAMS = {
        "per_page": 100,  # Number of comments to retrieve per page
        "page": 1,  # Starting page number
        "sort": "updated",
        "direction": "desc",
    }

    # Request
    comments = []
    while True:
        response = requests.get(URL, headers=HEADERS, params=PARAMS)
        response.raise_for_status()  # Raise an exception for any HTTP errors
        data = response.json()

        filtered_comments = [
            comment for comment in data if comment["user"]["login"] in USERS
        ]
        comments.extend(filtered_comments)

        # Check if there are more pages of comments
        if "next" in response.links:
            PARAMS["page"] += 1
        else:
            break

    # Write to CSV
    csv_filename = "issue_comments.csv"
    fieldnames = ["id", "issue_url", "user", "created_at", "updated_at", "body"]

    this = Path(__file__).resolve()
    csv_filename = this.parent / csv_filename
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
