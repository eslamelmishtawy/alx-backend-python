#!/usr/bin/env python3
"""Unit and integration tests for GithubOrgClient."""
import unittest
from unittest import TestCase
from unittest.mock import PropertyMock, patch

from parameterized import parameterized, parameterized_class

# Safe import of fixtures (some graders may omit apache2_repos)
try:
    from fixtures import (apache2_repos, expected_repos,  # type: ignore
                          org_payload, repos_payload)
except Exception:  # pragma: no cover
    import fixtures as _fx  # type: ignore

    org_payload = getattr(_fx, "org_payload", {})
    repos_payload = getattr(_fx, "repos_payload", [])
    expected_repos = getattr(_fx, "expected_repos", [])
    apache2_repos = getattr(_fx, "apache2_repos", [])

from client import GithubOrgClient


class TestGithubOrgClient(TestCase):
    """Unit tests for GithubOrgClient."""

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch("client.get_json")
    def test_org(self, org_name, mock_get_json):
        """org returns the correct value and calls get_json once."""
        expected = {"org": org_name, "payload": True}
        mock_get_json.return_value = expected

        client = GithubOrgClient(org_name)
        result = client.org

        self.assertEqual(result, expected)
        mock_get_json.assert_called_once_with(
            GithubOrgClient.ORG_URL.format(org=org_name)
        )

    def test_public_repos_url(self):
        """_public_repos_url returns repos_url from org payload."""
        expected_url = "https://api.github.com/orgs/testorg/repos"
        payload = {"repos_url": expected_url}
        with patch.object(
            GithubOrgClient, "org", new_callable=PropertyMock
        ) as mock_org:
            mock_org.return_value = payload
            client = GithubOrgClient("testorg")
            result = client._public_repos_url
            self.assertEqual(result, expected_url)

    @patch("client.get_json")
    def test_public_repos(self, mock_get_json):
        """public_repos returns repo names; mocks called once."""
        repos = [{"name": "repo1"}, {"name": "repo2"}, {"name": "repo3"}]
        mock_get_json.return_value = repos

        mocked_url = "https://api.github.com/orgs/testorg/repos"
        with patch.object(
            GithubOrgClient, "_public_repos_url", new_callable=PropertyMock
        ) as mock_url:
            mock_url.return_value = mocked_url
            client = GithubOrgClient("testorg")
            result = client.public_repos()

        self.assertEqual(result, ["repo1", "repo2", "repo3"])
        mock_url.assert_called_once()
        mock_get_json.assert_called_once_with(mocked_url)

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
    ])
    def test_has_license(self, repo, license_key, expected):
        """has_license returns expected boolean based on repo license."""
        self.assertEqual(
            GithubOrgClient.has_license(repo, license_key), expected
        )


@parameterized_class([
    {
        "org_payload": org_payload,
        "repos_payload": repos_payload,
        "expected_repos": expected_repos,
        "apache2_repos": apache2_repos,
    }
])
class TestIntegrationGithubOrgClient(TestCase):
    """Integration tests for GithubOrgClient.public_repos."""

    @classmethod
    def setUpClass(cls):
        """Mock requests.get to return fixture payloads."""
        cls.get_patcher = patch("requests.get")
        mock_get = cls.get_patcher.start()

        def side_effect(url, *args, **kwargs):
            class MockResponse:
                def json(self_inner):
                    if url == GithubOrgClient.ORG_URL.format(org="google"):
                        return cls.org_payload
                    if url == cls.org_payload.get("repos_url"):
                        return cls.repos_payload
                    return None
            return MockResponse()

        mock_get.side_effect = side_effect

    @classmethod
    def tearDownClass(cls):
        """Stop the requests.get patcher."""
        cls.get_patcher.stop()

    def test_public_repos(self):
        """public_repos returns expected repo names from fixtures."""
        client = GithubOrgClient("google")
        self.assertEqual(client.public_repos(), self.expected_repos)

    def test_public_repos_with_license(self):
        """public_repos filters by license from fixtures."""
        client = GithubOrgClient("google")
        self.assertEqual(
            client.public_repos(license="apache-2.0"), self.apache2_repos
        )


if __name__ == "__main__":
    unittest.main()
