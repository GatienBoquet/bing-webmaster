---
name: bing-webmaster
description: Use this skill when working with Microsoft Bing Webmaster Tools or Bing Webmaster API tasks, including checking verified sites, traffic and ranking stats, crawl issues, URL index status, inbound links, sitemap/feed submission, URL submission, URL submission quotas, OAuth/API-key setup, or comparing Bing SEO evidence with Search Console data.
---

# Bing Webmaster

Use this skill to inspect or update Bing Webmaster data through the official API and portal workflow. Prefer read-only API calls first; require explicit user approval before submitting URLs, feeds, site moves, blocks, role changes, or other write actions.

## Quick Start

Use `scripts/bing_webmaster.py` for common calls:

```powershell
$env:BING_WEBMASTER_API_KEY = "<api key>"
python scripts/bing_webmaster.py sites
python scripts/bing_webmaster.py traffic --site-url "https://example.com/"
python scripts/bing_webmaster.py crawl-issues --site-url "https://example.com/"
python scripts/bing_webmaster.py quota --site-url "https://example.com/"
python scripts/bing_webmaster.py submit-url --site-url "https://example.com/" --url "https://example.com/page" --dry-run
```

If Python is not on PATH in Codex Desktop, use the bundled runtime path from `codex_app__load_workspace_dependencies`.

## Authentication

Support either API key or OAuth:

- API key: use `BING_WEBMASTER_API_KEY`, passed as `?apikey=...`.
- OAuth bearer token: use `BING_WEBMASTER_ACCESS_TOKEN`, passed as `Authorization: Bearer ...`.

When credentials are missing or rejected, state exactly what is missing and stop before making claims from Bing data. To get an API key, the user must sign in to Bing Webmaster Tools, add and verify the site, then use Settings > API Access. OAuth requires a registered client ID, client secret, redirect URI, and one of the scopes `Webmaster.read` or `Webmaster.manage`.

## Workflow

1. Confirm the site URL exactly as Bing knows it, including scheme and trailing slash when relevant.
2. Run `sites` or a harmless `raw GetUserSites` call to verify credentials and discover verified properties.
3. For audits, gather:
   - `traffic` for impressions/clicks trend.
   - `crawl-issues` for URLs Bing reports as problematic.
   - `url-info` for specific URL index state.
   - `quota` before any URL submission.
4. Compare Bing findings with local routes, sitemaps, redirects, robots directives, and Google Search Console only after Bing API evidence is gathered or the credential gap is explicit.
5. For writes, show the exact site URL, target URLs/feed, method, and expected effect; ask for approval unless the user already explicitly requested that exact action.

## References

Read `references/api-reference.md` when you need endpoint patterns, common method names, OAuth details, or troubleshooting notes.

## Safety Notes

- Treat API keys, OAuth codes, access tokens, refresh tokens, and client secrets as secrets. Do not print them in final answers or logs.
- Use `--dry-run` for write operations until the user confirms the exact operation.
- Bing Webmaster data can lag after fixes; report API timestamps or note when the API does not expose them.
- The Microsoft docs use both `www.bing.com` and `ssl.bing.com` host examples. Prefer `https://ssl.bing.com/webmaster/api.svc/json/...` for API-key JSON calls and fall back to `https://www.bing.com/webmaster/api.svc/json/...` if needed.
