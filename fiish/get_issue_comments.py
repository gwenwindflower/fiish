import os
import requests


def get_issue_comments(repo_owner: str, repo_name: str, users: list[str] | None = None):
    # Constants
    REPO_OWNER = repo_owner
    REPO_NAME = repo_name
    URL = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues/comments"
    if users is not None:
        USERS = users
    HEADERS = {
        "Authorization": f"Bearer {os.environ['GITHUB_PERSONAL_ACCESS_TOKEN']}",
        "Accept": "application/vnd.github+json",
    }
    PARAMS = {
        "per_page": 100,
        "page": 1,
        "sort": "updated",
        "direction": "desc",  # Newest first, although the model doesn't care
    }

    # Request
    comments: list[dict[str, str]] = []
    while True:
        response = requests.get(URL, headers=HEADERS, params=PARAMS)
        response.raise_for_status()  # Raise an exception for any HTTP errors
        data = response.json()

        if users:
            filtered_comments = [
                comment for comment in data if comment["user"]["login"] in USERS
            ]
            comments.extend(filtered_comments)

        else:
            comments.extend(data)
        # Check if there are more pages of comments
        if "next" in response.links:
            PARAMS["page"] += 1
        else:
            break

    return comments
