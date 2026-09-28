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


API_KEY_BASE_URL = "https://ssl.bing.com/webmaster/api.svc/json"
OAUTH_BASE_URL = "https://www.bing.com/webmaster/api.svc/json"
MAX_BATCH_URLS = 500
WRITE_METHODS = {
    name.lower()
    for name in (
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
    )
}
# Catch write methods missing from the list above (new or renamed API methods).
WRITE_PREFIXES = ("add", "remove", "submit", "save", "update", "verify", "enable", "fetch", "set", "delete")


class BingWebmasterError(RuntimeError):
    pass


def is_write_method(method: str) -> bool:
    lowered = method.lower()
    return lowered in WRITE_METHODS or lowered.startswith(WRITE_PREFIXES)


def build_url(base_url: str, method: str, params: dict[str, str], api_key: str | None) -> str:
    query = dict(params)
    if api_key:
        query["apikey"] = api_key
    encoded = urllib.parse.urlencode(query)
    url = f"{base_url.rstrip('/')}/{urllib.parse.quote(method, safe='')}"
    if encoded:
        url += f"?{encoded}"
    return url


def resolve_base_url(base_url: str | None, access_token: str | None) -> str:
    if base_url:
        return base_url
    # The OAuth docs use www.bing.com; API-key examples use ssl.bing.com.
    return OAUTH_BASE_URL if access_token else API_KEY_BASE_URL


def request_json(
    method_name: str,
    *,
    query: dict[str, str] | None = None,
    body: dict | None = None,
    http_method: str = "GET",
    base_url: str | None = None,
    api_key: str | None = None,
    access_token: str | None = None,
    timeout: int = 30,
) -> dict | list | None:
    if not api_key and not access_token:
        raise BingWebmasterError(
            "Set BING_WEBMASTER_API_KEY or BING_WEBMASTER_ACCESS_TOKEN before calling the API."
        )

    base_url = resolve_base_url(base_url, access_token)
    url = build_url(base_url, method_name, query or {}, api_key if not access_token else None)
    data = None
    headers = {"Accept": "application/json"}
    if http_method == "POST":
        data = json.dumps(body if body is not None else {}, separators=(",", ":")).encode("utf-8")
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


def credentials(args: argparse.Namespace) -> tuple[str | None, str | None]:
    api_key = args.api_key or os.environ.get("BING_WEBMASTER_API_KEY")
    access_token = args.access_token or os.environ.get("BING_WEBMASTER_ACCESS_TOKEN")
    return api_key, access_token


def call(
    args: argparse.Namespace,
    method: str,
    query: dict[str, str] | None = None,
    body: dict | None = None,
    http_method: str | None = None,
) -> None:
    http_method = http_method or ("POST" if body is not None else "GET")
    api_key, access_token = credentials(args)
    if args.dry_run:
        if access_token:
            auth = "oauth-bearer"
        elif api_key:
            auth = "api-key"
        else:
            auth = "missing"
        base_url = resolve_base_url(args.base_url, access_token)
        masked_key = "***" if api_key and not access_token else None
        pretty_print(
            {
                "dryRun": True,
                "method": method,
                "httpMethod": http_method,
                "url": build_url(base_url, method, query or {}, masked_key),
                "auth": auth,
                "query": query or {},
                "body": body if http_method == "POST" else None,
            }
        )
        return
    result = request_json(
        method,
        query=query,
        body=body,
        http_method=http_method,
        base_url=args.base_url,
        api_key=api_key,
        access_token=access_token,
        timeout=args.timeout,
    )
    pretty_print(result)


def require_write_approval(args: argparse.Namespace) -> None:
    if not (args.allow_write or args.dry_run):
        raise BingWebmasterError(
            "Refusing write call. Re-run with --dry-run to preview or --allow-write once the user approved it."
        )


def common_parser(suppress_defaults: bool) -> argparse.ArgumentParser:
    # Subparsers reuse these options with SUPPRESS defaults so a value given before
    # the subcommand is not overwritten by the subparser's default.
    def default(value: object) -> object:
        return argparse.SUPPRESS if suppress_defaults else value

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(
        "--api-key", default=default(None), help="Bing Webmaster API key. Defaults to BING_WEBMASTER_API_KEY."
    )
    parser.add_argument(
        "--access-token",
        default=default(None),
        help="OAuth access token. Defaults to BING_WEBMASTER_ACCESS_TOKEN. If set, API key is not sent.",
    )
    parser.add_argument(
        "--base-url",
        default=default(None),
        help=f"API base URL. Defaults to {API_KEY_BASE_URL} (API key) or {OAUTH_BASE_URL} (OAuth).",
    )
    parser.add_argument("--timeout", type=int, default=default(30))
    parser.add_argument(
        "--dry-run", action="store_true", default=default(False), help="Print the request shape without calling Bing."
    )
    return parser


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Call Bing Webmaster JSON API endpoints.", parents=[common_parser(suppress_defaults=False)]
    )
    sub = parser.add_subparsers(dest="command", required=True)
    common = common_parser(suppress_defaults=True)

    def add(name: str, help_text: str) -> argparse.ArgumentParser:
        return sub.add_parser(name, help=help_text, parents=[common])

    def add_write(name: str, help_text: str) -> argparse.ArgumentParser:
        p = add(name, help_text)
        p.add_argument("--allow-write", action="store_true", help="Send the write call. Without it, use --dry-run.")
        return p

    add("sites", "List authenticated user's Bing Webmaster sites.")

    for name, method in [
        ("traffic", "GetRankAndTrafficStats"),
        ("crawl-issues", "GetCrawlIssues"),
        ("crawl-stats", "GetCrawlStats"),
        ("feeds", "GetFeeds"),
        ("quota", "GetUrlSubmissionQuota"),
        ("query-stats", "GetQueryStats"),
        ("page-stats", "GetPageStats"),
    ]:
        p = add(name, f"Call {method}.")
        p.add_argument("--site-url", required=True)

    p = add("url-info", "Call GetUrlInfo for one URL.")
    p.add_argument("--site-url", required=True)
    p.add_argument("--url", required=True)

    p = add("url-traffic", "Call GetUrlTrafficInfo for one URL.")
    p.add_argument("--site-url", required=True)
    p.add_argument("--url", required=True)

    p = add("page-query-stats", "Call GetPageQueryStats for one page.")
    p.add_argument("--site-url", required=True)
    p.add_argument("--page-url", required=True)

    p = add("feed-details", "Call GetFeedDetails for one sitemap/feed.")
    p.add_argument("--site-url", required=True)
    p.add_argument("--feed-url", required=True)

    p = add("link-counts", "Call GetLinkCounts: site pages with inbound links (paged).")
    p.add_argument("--site-url", required=True)
    p.add_argument("--page", type=int, default=0, help="Zero-based result page.")

    p = add("links", "Call GetUrlLinks: inbound links for one URL (paged).")
    p.add_argument("--site-url", required=True)
    p.add_argument("--url", required=True, help="Target URL, sent as the 'link' parameter.")
    p.add_argument("--page", type=int, default=0, help="Zero-based result page.")

    p = add_write("submit-url", "Call SubmitUrl. Requires --dry-run or --allow-write.")
    p.add_argument("--site-url", required=True)
    p.add_argument("--url", required=True)

    p = add_write("submit-batch", f"Call SubmitUrlBatch (max {MAX_BATCH_URLS} URLs). Requires --dry-run or --allow-write.")
    p.add_argument("--site-url", required=True)
    p.add_argument("--url", action="append", default=[], help="URL to submit. Repeatable.")
    p.add_argument("--url-file", help="File with one URL per line.")

    p = add_write("submit-feed", "Call SubmitFeed. Requires --dry-run or --allow-write.")
    p.add_argument("--site-url", required=True)
    p.add_argument("--feed-url", required=True)

    p = add_write("raw", "Call an arbitrary API method.")
    p.add_argument("method")
    p.add_argument("--http-method", choices=["GET", "POST"], default="GET")
    p.add_argument("--query-json", type=parse_json_arg, default={})
    p.add_argument("--body-json", type=parse_json_arg)

    return parser


def read_batch_urls(args: argparse.Namespace) -> list[str]:
    urls = list(args.url)
    if args.url_file:
        with open(args.url_file, encoding="utf-8") as fh:
            urls.extend(line.strip() for line in fh if line.strip() and not line.lstrip().startswith("#"))
    if not urls:
        raise BingWebmasterError("submit-batch needs at least one --url or a --url-file.")
    if len(urls) > MAX_BATCH_URLS:
        raise BingWebmasterError(f"SubmitUrlBatch accepts at most {MAX_BATCH_URLS} URLs; got {len(urls)}.")
    return urls


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
        elif args.command == "url-traffic":
            call(args, "GetUrlTrafficInfo", {"siteUrl": args.site_url, "url": args.url})
        elif args.command == "page-query-stats":
            call(args, "GetPageQueryStats", {"siteUrl": args.site_url, "page": args.page_url})
        elif args.command == "feed-details":
            call(args, "GetFeedDetails", {"siteUrl": args.site_url, "feedUrl": args.feed_url})
        elif args.command == "link-counts":
            call(args, "GetLinkCounts", {"siteUrl": args.site_url, "page": str(args.page)})
        elif args.command == "links":
            call(args, "GetUrlLinks", {"siteUrl": args.site_url, "link": args.url, "page": str(args.page)})
        elif args.command == "submit-url":
            require_write_approval(args)
            call(args, "SubmitUrl", body={"siteUrl": args.site_url, "url": args.url})
        elif args.command == "submit-batch":
            urls = read_batch_urls(args)
            require_write_approval(args)
            call(args, "SubmitUrlBatch", body={"siteUrl": args.site_url, "urlList": urls})
        elif args.command == "submit-feed":
            require_write_approval(args)
            call(args, "SubmitFeed", body={"siteUrl": args.site_url, "feedUrl": args.feed_url})
        elif args.command == "raw":
            if is_write_method(args.method) or args.http_method == "POST":
                require_write_approval(args)
            call(
                args,
                args.method,
                query=args.query_json,
                body=args.body_json if args.http_method == "POST" else None,
                http_method=args.http_method,
            )
        return 0
    except (BingWebmasterError, OSError) as exc:
        print(f"bing_webmaster.py: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
