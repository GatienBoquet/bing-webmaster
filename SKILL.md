---
name: bing-webmaster
description: Use this skill when working with Microsoft Bing Webmaster Tools or Bing Webmaster API tasks, including checking verified sites, traffic and ranking stats, crawl issues, URL index status, inbound links, sitemap/feed submission, URL submission, URL submission quotas, OAuth/API-key setup, or comparing Bing SEO evidence with Search Console data.
---

# Bing Webmaster

Use this skill to inspect or update Bing Webmaster data through the official API and portal workflow. Prefer read-only API calls first; require explicit user approval before submitting URLs, feeds, site moves, blocks, role changes, or other write actions.

## Quick Start

Use `scripts/bing_webmaster.py` (Python 3.8+, standard library only) for common calls. Options such as `--dry-run`, `--api-key`, and `--access-token` work before or after the subcommand.

PowerShell:

```powershell
$env:BING_WEBMASTER_API_KEY = "<api key>"
python scripts/bing_webmaster.py sites
python scripts/bing_webmaster.py traffic --site-url "https://example.com/"
```

bash/zsh:

```bash
export BING_WEBMASTER_API_KEY="<api key>"
python3 scripts/bing_webmaster.py sites
python3 scripts/bing_webmaster.py traffic --site-url "https://example.com/"
```

Read commands:

```text
sites                                             GetUserSites
traffic          --site-url                       GetRankAndTrafficStats
crawl-issues     --site-url                       GetCrawlIssues
crawl-stats      --site-url                       GetCrawlStats
query-stats      --site-url                       GetQueryStats
page-stats       --site-url                       GetPageStats
page-query-stats --site-url --page-url            GetPageQueryStats
url-info         --site-url --url                 GetUrlInfo
url-traffic      --site-url --url                 GetUrlTrafficInfo
feeds            --site-url                       GetFeeds
feed-details     --site-url --feed-url            GetFeedDetails
quota            --site-url                       GetUrlSubmissionQuota
link-counts      --site-url [--page N]            GetLinkCounts
links            --site-url --url [--page N]      GetUrlLinks
raw <Method> [--query-json '{...}']               any read method
```

Write commands refuse to run unless given `--dry-run` (preview only) or `--allow-write` (send):

```text
submit-url   --site-url --url                            SubmitUrl
submit-batch --site-url --url ... | --url-file FILE      SubmitUrlBatch (max 500 URLs)
submit-feed  --site-url --feed-url                       SubmitFeed
raw <WriteMethod> --http-method POST --body-json '{...}'
```

```bash
python3 scripts/bing_webmaster.py submit-url --site-url "https://example.com/" --url "https://example.com/page" --dry-run
# only after the user approves the exact request:
python3 scripts/bing_webmaster.py submit-url --site-url "https://example.com/" --url "https://example.com/page" --allow-write
```

If Python is not on PATH in Codex Desktop, use the bundled runtime path from `codex_app__load_workspace_dependencies`.

## Authentication

Support either API key or OAuth:

- API key: use `BING_WEBMASTER_API_KEY`, passed as `?apikey=...` to `https://ssl.bing.com/webmaster/api.svc/json/`.
- OAuth bearer token: use `BING_WEBMASTER_ACCESS_TOKEN`, passed as `Authorization: Bearer ...` to `https://www.bing.com/webmaster/api.svc/json/`. When a token is set, the API key is not sent.

When credentials are missing or rejected, state exactly what is missing and stop before making claims from Bing data. To get an API key, the user must sign in to Bing Webmaster Tools, add and verify the site, open Settings > API Access, accept the terms, and generate the key. There is one key per user, and it works for all of that user's verified sites. OAuth requires a registered client ID, client secret, redirect URI, and the scope `webmaster.read` or `webmaster.manage`.

## Workflow

1. Confirm the site URL exactly as Bing knows it, including scheme and trailing slash when relevant.
2. Run `sites` to verify credentials and discover verified properties.
3. For audits, gather:
   - `traffic` for impressions/clicks trend.
   - `crawl-issues` for URLs Bing reports as problematic.
   - `url-info` / `url-traffic` for specific URL index state and performance.
   - `link-counts` / `links` for inbound link evidence.
   - `quota` before any URL submission.
4. Compare Bing findings with local routes, sitemaps, redirects, robots directives, and Google Search Console only after Bing API evidence is gathered or the credential gap is explicit.
5. For writes, run the command with `--dry-run` and show the output (HTTP method, URL with the key masked, auth mode, body) and the expected effect. Ask for approval unless the user already explicitly requested that exact action, then re-run with `--allow-write`.

## References

Read `references/api-reference.md` when you need endpoint patterns, method parameters, OAuth details, response quirks, or troubleshooting notes.

## Safety Notes

- Treat API keys, OAuth codes, access tokens, refresh tokens, and client secrets as secrets. Do not print them in final answers or logs. The `--dry-run` output masks the API key.
- Never pass `--allow-write` before the user confirms the exact operation.
- Bing Webmaster data can lag after fixes; report API timestamps or note when the API does not expose them.
- For frequent or large-scale URL notifications, suggest IndexNow (https://www.indexnow.org/) instead of spending the Webmaster API submission quota.
