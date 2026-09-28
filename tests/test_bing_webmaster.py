"""Offline tests for scripts/bing_webmaster.py. Run: python -m unittest discover -s tests"""

from __future__ import annotations

import contextlib
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import bing_webmaster as bw  # noqa: E402

SITE = "https://example.com/"


class FakeResponse:
    def __init__(self, payload: bytes = b'{"d":null}') -> None:
        self.payload = payload

    def read(self) -> bytes:
        return self.payload

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, *exc: object) -> None:
        return None


def run(argv: list[str], env: dict[str, str] | None = None) -> tuple[int, str, str, list]:
    requests: list = []

    def fake_urlopen(req, timeout):  # noqa: ANN001
        requests.append(req)
        return FakeResponse()

    out, err = io.StringIO(), io.StringIO()
    environ = {"BING_WEBMASTER_API_KEY": "secret-key"} if env is None else env
    with mock.patch.dict(os.environ, environ, clear=True), mock.patch.object(
        bw.urllib.request, "urlopen", fake_urlopen
    ), contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = bw.main(argv)
    return code, out.getvalue(), err.getvalue(), requests


class DryRunTests(unittest.TestCase):
    def test_dry_run_after_subcommand(self) -> None:
        code, out, _, reqs = run(["submit-url", "--site-url", SITE, "--url", SITE + "page", "--dry-run"])
        self.assertEqual(code, 0)
        self.assertEqual(reqs, [])
        shown = json.loads(out)
        self.assertEqual(shown["httpMethod"], "POST")
        self.assertEqual(shown["auth"], "api-key")
        self.assertIn("apikey=%2A%2A%2A", shown["url"])
        self.assertNotIn("secret-key", out)

    def test_dry_run_before_subcommand(self) -> None:
        code, _, _, reqs = run(["--dry-run", "submit-url", "--site-url", SITE, "--url", SITE])
        self.assertEqual(code, 0)
        self.assertEqual(reqs, [])

    def test_common_options_after_subcommand(self) -> None:
        code, out, _, _ = run(["sites", "--access-token", "tok", "--dry-run"], env={})
        self.assertEqual(code, 0)
        shown = json.loads(out)
        self.assertEqual(shown["auth"], "oauth-bearer")
        self.assertTrue(shown["url"].startswith(bw.OAUTH_BASE_URL))


class WriteGuardTests(unittest.TestCase):
    def test_submit_url_refuses_without_approval(self) -> None:
        code, _, err, reqs = run(["submit-url", "--site-url", SITE, "--url", SITE])
        self.assertEqual(code, 2)
        self.assertIn("Refusing write call", err)
        self.assertEqual(reqs, [])

    def test_submit_feed_refuses_without_approval(self) -> None:
        code, _, _, reqs = run(["submit-feed", "--site-url", SITE, "--feed-url", SITE + "sitemap.xml"])
        self.assertEqual(code, 2)
        self.assertEqual(reqs, [])

    def test_submit_url_with_allow_write(self) -> None:
        code, _, _, reqs = run(["submit-url", "--site-url", SITE, "--url", SITE, "--allow-write"])
        self.assertEqual(code, 0)
        self.assertEqual(len(reqs), 1)
        self.assertEqual(reqs[0].get_method(), "POST")
        self.assertEqual(json.loads(reqs[0].data), {"siteUrl": SITE, "url": SITE})

    def test_raw_write_check_is_case_insensitive(self) -> None:
        code, _, _, reqs = run(["raw", "submiturl", "--query-json", '{"siteUrl":"x"}'])
        self.assertEqual(code, 2)
        self.assertEqual(reqs, [])

    def test_raw_unknown_write_prefix_is_guarded(self) -> None:
        code, _, _, reqs = run(["raw", "RemoveSomethingNew"])
        self.assertEqual(code, 2)
        self.assertEqual(reqs, [])

    def test_raw_read_is_allowed(self) -> None:
        code, _, _, reqs = run(["raw", "GetUserSites"])
        self.assertEqual(code, 0)
        self.assertEqual(reqs[0].get_method(), "GET")

    def test_raw_post_without_body_stays_post(self) -> None:
        code, _, _, reqs = run(["raw", "GetUserSites", "--http-method", "POST", "--allow-write"])
        self.assertEqual(code, 0)
        self.assertEqual(reqs[0].get_method(), "POST")
        self.assertEqual(reqs[0].data, b"{}")


class BatchTests(unittest.TestCase):
    def test_batch_from_file(self) -> None:
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as fh:
            fh.write(f"{SITE}a\n\n# comment\n{SITE}b\n")
        self.addCleanup(os.unlink, fh.name)
        code, out, _, _ = run(["submit-batch", "--site-url", SITE, "--url-file", fh.name, "--dry-run"])
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out)["body"]["urlList"], [SITE + "a", SITE + "b"])

    def test_batch_file_with_bom(self) -> None:
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8-sig") as fh:
            fh.write(f"{SITE}a\n{SITE}b\n")
        self.addCleanup(os.unlink, fh.name)
        code, out, _, _ = run(["submit-batch", "--site-url", SITE, "--url-file", fh.name, "--dry-run"])
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out)["body"]["urlList"], [SITE + "a", SITE + "b"])

    def test_batch_limit(self) -> None:
        argv = ["submit-batch", "--site-url", SITE, "--dry-run"]
        for i in range(bw.MAX_BATCH_URLS + 1):
            argv += ["--url", f"{SITE}{i}"]
        code, _, err, _ = run(argv)
        self.assertEqual(code, 2)
        self.assertIn("at most 500", err)


class ReadCommandTests(unittest.TestCase):
    def query_of(self, argv: list[str]) -> dict:
        code, out, _, _ = run(argv + ["--dry-run"])
        self.assertEqual(code, 0)
        return json.loads(out)["query"]

    def test_links_uses_link_and_page(self) -> None:
        self.assertEqual(
            self.query_of(["links", "--site-url", SITE, "--url", SITE + "x", "--page", "2"]),
            {"siteUrl": SITE, "link": SITE + "x", "page": "2"},
        )

    def test_link_counts_uses_page(self) -> None:
        self.assertEqual(self.query_of(["link-counts", "--site-url", SITE]), {"siteUrl": SITE, "page": "0"})

    def test_api_key_request_uses_ssl_host(self) -> None:
        code, _, _, reqs = run(["traffic", "--site-url", SITE])
        self.assertEqual(code, 0)
        self.assertTrue(reqs[0].full_url.startswith(bw.API_KEY_BASE_URL + "/GetRankAndTrafficStats?"))
        self.assertIn("apikey=secret-key", reqs[0].full_url)

    def test_oauth_request_uses_bearer_and_no_key(self) -> None:
        env = {"BING_WEBMASTER_API_KEY": "secret-key", "BING_WEBMASTER_ACCESS_TOKEN": "tok"}
        code, _, _, reqs = run(["sites"], env=env)
        self.assertEqual(code, 0)
        self.assertEqual(reqs[0].get_header("Authorization"), "Bearer tok")
        self.assertNotIn("apikey", reqs[0].full_url)
        self.assertTrue(reqs[0].full_url.startswith(bw.OAUTH_BASE_URL))


if __name__ == "__main__":
    unittest.main()
