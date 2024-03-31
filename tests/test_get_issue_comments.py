import os
from unittest.mock import Mock, patch

import pytest
from fiish.get_issue_comments import get_issue_comments


def test_get_issue_comments_with_users():
    with patch("requests.get") as mock_get:
        mock_response = Mock()
        mock_response.json.return_value = [
            {
                "id": 1,
                "user": {"login": "legolas"},
                "issue_url": "https://api.github.com/repos/owner/repo/issues/1",
                "created_at": "2024-03-21",
                "updated_at": "2024-03-21",
                "body": "Gimli is my bff",
            },
            {
                "id": 2,
                "user": {"login": "aragorn"},
                "issue_url": "https://api.github.com/repos/owner/repo/issues/2",
                "created_at": "2024-03-21",
                "updated_at": "2024-03-21",
                "body": "Arwen is bae",
            },
        ]
        mock_response.links = {}
        mock_get.return_value = mock_response

        comments = get_issue_comments("owner", "repo", ["legolas"])

        mock_get.assert_called_once_with(
            "https://api.github.com/repos/owner/repo/issues/comments",
            headers={
                "Authorization": f"Bearer {os.environ['GITHUB_PERSONAL_ACCESS_TOKEN']}",
                "Accept": "application/vnd.github+json",
            },
            params={"per_page": 100, "page": 1, "sort": "updated", "direction": "desc"},
        )

        expected_response = [
            {
                "id": 1,
                "user": {"login": "legolas"},
                "issue_url": "https://api.github.com/repos/owner/repo/issues/1",
                "created_at": "2024-03-21",
                "updated_at": "2024-03-21",
                "body": "Gimli is my bff",
            },
        ]

        assert comments == expected_response


def test_get_issue_comments_without_users():
    with patch("requests.get") as mock_get:
        mock_response = Mock()
        mock_response.json.return_value = [
            {
                "id": 1,
                "user": {"login": "legolas"},
                "issue_url": "https://api.github.com/repos/owner/repo/issues/1",
                "created_at": "2024-03-21",
                "updated_at": "2024-03-21",
                "body": "Gimli is my bff",
            },
            {
                "id": 2,
                "user": {"login": "aragorn"},
                "issue_url": "https://api.github.com/repos/owner/repo/issues/2",
                "created_at": "2024-03-21",
                "updated_at": "2024-03-21",
                "body": "Arwen is bae",
            },
        ]
        mock_response.links = {}
        mock_get.return_value = mock_response

        comments = get_issue_comments("owner", "repo")

        mock_get.assert_called_once_with(
            "https://api.github.com/repos/owner/repo/issues/comments",
            headers={
                "Authorization": f"Bearer {os.environ['GITHUB_PERSONAL_ACCESS_TOKEN']}",
                "Accept": "application/vnd.github+json",
            },
            params={"per_page": 100, "page": 1, "sort": "updated", "direction": "desc"},
        )

        expected_response = [
            {
                "id": 1,
                "user": {"login": "legolas"},
                "issue_url": "https://api.github.com/repos/owner/repo/issues/1",
                "created_at": "2024-03-21",
                "updated_at": "2024-03-21",
                "body": "Gimli is my bff",
            },
            {
                "id": 2,
                "user": {"login": "aragorn"},
                "issue_url": "https://api.github.com/repos/owner/repo/issues/2",
                "created_at": "2024-03-21",
                "updated_at": "2024-03-21",
                "body": "Arwen is bae",
            },
        ]

        assert comments == expected_response


def test_get_issue_comments_error_handling():
    # Mock the requests.get function to raise an exception
    with patch("requests.get") as mock_get:
        mock_get.side_effect = Exception("An error occurred")
        with pytest.raises(Exception) as excinfo:
            comments = get_issue_comments("owner", "repo")
            assert comments == []
        assert str(excinfo.value) == "An error occurred"
