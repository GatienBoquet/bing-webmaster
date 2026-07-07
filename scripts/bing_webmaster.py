#!/usr/bin/env python3
"""Small Bing Webmaster API helper using only the Python standard library."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request


DEFAULT_BASE_URL = "https://ssl.bing.com/webmaster/api.svc/json"
WRITE_METHODS = {
    "AddBlockedUrl",
    "AddConnectedPage",
    "AddCountryRegionSettings",
    "AddDeepLinkBlock",
    "AddPagePreviewBlock",
    "AddQueryParameter",
    "AddSite",
    "AddSiteRoles",
    "EnableDisableQueryParameter",
    "FetchUrl",
    "RemoveBlockedUrl",
    "RemoveCountryRegionSettings",
    "RemoveDeepLinkBlock",
    "RemoveFeed",
    "RemovePagePreviewBlock",
    "RemoveQueryParameter",
    "RemoveSite",
    "RemoveSiteRole",
    "SaveCrawlSettings",
    "SubmitContent",
    "SubmitFeed",
    "SubmitSiteMove",
    "SubmitUrl",
    "SubmitUrlBatch",
    "UpdateDeepLink",
    "VerifySite",
}


class BingWebmasterError(RuntimeError):
    pass


def build_url(base_url: str, method: str, params: dict[str, str], api_key: str | None) -> str:
    query = dict(params)
    if api_key:
        query["apikey"] = api_key
    encoded = urllib.parse.urlencode(query)
    url = f"{base_url.rstrip('/')}/{urllib.parse.quote(method, safe='')}"
    if encoded:
        url += f"?{encoded}"
    return url


def request_json(
    method_name: str,
    *,
    query: dict[str, str] | None = None,
    body: dict | None = None,
    http_method: str = "GET",
    base_url: str = DEFAULT_BASE_URL,
    api_key: str | None = None,
    access_token: str | None = None,
    timeout: int = 30,
) -> dict | list | None:
    if not api_key and not access_token:
        raise BingWebmasterError(
            "Set BING_WEBMASTER_API_KEY or BING_WEBMASTER_ACCESS_TOKEN before calling the API."
        )

    url = build_url(base_url, method_name, query or {}, api_key if not access_token else None)
    data = None
    headers = {"Accept": "application/json"}
    if body is not None:
        data = json.dumps(body, separators=(",", ":")).encode("utf-8")
        headers["Content-Type"] = "application/json; charset=utf-8"
    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"

    req = urllib.request.Request(url, data=data, headers=headers, method=http_method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            payload = resp.read()
            if not payload:
                return None
            text = payload.decode("utf-8-sig")
            return json.loads(text)
    except urllib.error.HTTPError as exc:
        details = exc.read().decode("utf-8", errors="replace")
        raise BingWebmasterError(f"HTTP {exc.code} from {method_name}: {details}") from exc
    except urllib.error.URLError as exc:
        raise BingWebmasterError(f"Network error calling {method_name}: {exc.reason}") from exc


def pretty_print(value: object) -> None:
    print(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False))


def parse_json_arg(value: str | None) -> dict:
    if not value:
        return {}
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError as exc:
        raise argparse.ArgumentTypeError(str(exc)) from exc
    if not isinstance(parsed, dict):
        raise argparse.ArgumentTypeError("JSON value must be an object")
    return parsed


def call(args: argparse.Namespace, method: str, query: dict[str, str] | None = None, body: dict | None = None) -> None:
    if args.dry_run:
        pretty_print({"dryRun": True, "method": method, "query": query or {}, "body": body})
        return
    result = request_json(
        method,
        query=query,
        body=body,
        http_method="POST" if body is not None else "GET",
        base_url=args.base_url,
        api_key=args.api_key or os.environ.get("BING_WEBMASTER_API_KEY"),
        access_token=args.access_token or os.environ.get("BING_WEBMASTER_ACCESS_TOKEN"),
        timeout=args.timeout,
    )
    pretty_print(result)


def add_common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--api-key", help="Bing Webmaster API key. Defaults to BING_WEBMASTER_API_KEY.")
    parser.add_argument(
        "--access-token",
        help="OAuth access token. Defaults to BING_WEBMASTER_ACCESS_TOKEN. If set, API key is not sent.",
    )
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--timeout", type=int, default=30)
    parser.add_argument("--dry-run", action="store_true", help="Print the request shape without calling Bing.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Call Bing Webmaster JSON API endpoints.")
    add_common(parser)
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("sites", help="List authenticated user's Bing Webmaster sites.")

    for name, method in [
        ("traffic", "GetRankAndTrafficStats"),
        ("crawl-issues", "GetCrawlIssues"),
        ("crawl-stats", "GetCrawlStats"),
        ("feeds", "GetFeeds"),
        ("quota", "GetUrlSubmissionQuota"),
        ("query-stats", "GetQueryStats"),
        ("page-stats", "GetPageStats"),
    ]:
        p = sub.add_parser(name, help=f"Call {method}.")
        p.add_argument("--site-url", required=True)

    p = sub.add_parser("url-info", help="Call GetUrlInfo for one URL.")
    p.add_argument("--site-url", required=True)
    p.add_argument("--url", required=True)

    p = sub.add_parser("submit-url", help="Call SubmitUrl. Use --dry-run until confirmed.")
    p.add_argument("--site-url", required=True)
    p.add_argument("--url", required=True)

    p = sub.add_parser("submit-feed", help="Call SubmitFeed. Use --dry-run until confirmed.")
    p.add_argument("--site-url", required=True)
    p.add_argument("--feed-url", required=True)

    p = sub.add_parser("raw", help="Call an arbitrary API method.")
    p.add_argument("method")
    p.add_argument("--http-method", choices=["GET", "POST"], default="GET")
    p.add_argument("--query-json", type=parse_json_arg, default={})
    p.add_argument("--body-json", type=parse_json_arg)
    p.add_argument("--allow-write", action="store_true", help="Allow known write methods without --dry-run.")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "sites":
            call(args, "GetUserSites")
        elif args.command == "traffic":
            call(args, "GetRankAndTrafficStats", {"siteUrl": args.site_url})
        elif args.command == "crawl-issues":
            call(args, "GetCrawlIssues", {"siteUrl": args.site_url})
        elif args.command == "crawl-stats":
            call(args, "GetCrawlStats", {"siteUrl": args.site_url})
        elif args.command == "feeds":
            call(args, "GetFeeds", {"siteUrl": args.site_url})
        elif args.command == "quota":
            call(args, "GetUrlSubmissionQuota", {"siteUrl": args.site_url})
        elif args.command == "query-stats":
            call(args, "GetQueryStats", {"siteUrl": args.site_url})
        elif args.command == "page-stats":
            call(args, "GetPageStats", {"siteUrl": args.site_url})
        elif args.command == "url-info":
            call(args, "GetUrlInfo", {"siteUrl": args.site_url, "url": args.url})
        elif args.command == "submit-url":
            call(args, "SubmitUrl", body={"siteUrl": args.site_url, "url": args.url})
        elif args.command == "submit-feed":
            call(args, "SubmitFeed", body={"siteUrl": args.site_url, "feedUrl": args.feed_url})
        elif args.command == "raw":
            is_write = args.method in WRITE_METHODS or args.http_method == "POST"
            if is_write and not (args.allow_write or args.dry_run):
                raise BingWebmasterError("Refusing possible write call. Re-run with --dry-run or --allow-write.")
            call(
                args,
                args.method,
                query=args.query_json,
                body=args.body_json if args.http_method == "POST" else None,
            )
        return 0
    except BingWebmasterError as exc:
        print(f"bing_webmaster.py: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
