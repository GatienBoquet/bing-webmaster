# Bing Webmaster API Reference

Official docs entrypoint: https://learn.microsoft.com/en-us/bingwebmaster/

## Capabilities

The API exposes rank and traffic stats, link details, keyword details, crawl stats, URL index information, URL submission, sitemap/feed submission, site verification, site roles, crawl settings, blocked URLs, and site moves.

## Auth

API key:

1. Sign in to https://www.bing.com/webmasters/.
2. Add and verify the site.
3. Open Settings > API Access.
4. Generate the user-level API key.

OAuth:

- Authorize endpoint: `GET https://www.bing.com/webmasters/OAuth/authorize`
- Token endpoint: `POST https://www.bing.com/webmasters/oauth/token`
- Scopes: `Webmaster.read` for read-only data, `Webmaster.manage` for read/write.
- OAuth access tokens are sent as `Authorization: Bearer <token>`.

## JSON Endpoint Pattern

API-key JSON calls generally use:

```text
https://ssl.bing.com/webmaster/api.svc/json/<Method>?apikey=<API_KEY>&...
```

POST requests use JSON bodies and can also use OAuth bearer tokens:

```http
POST /webmaster/api.svc/json/SubmitUrl HTTP/1.1
Host: www.bing.com
Content-Type: application/json
Authorization: Bearer <access-token>

{"siteUrl":"https://example.com/","url":"https://example.com/page"}
```

Responses often wrap data under a top-level `d` property.

## Common Read Methods

- `GetUserSites`: list sites available to the authenticated user.
- `GetRankAndTrafficStats?siteUrl=...`: traffic stats; Microsoft notes daily updates and says traffic includes Web, Chat, News, Images, Videos, and Knowledge Panel data from March 24, 2023 onward.
- `GetCrawlIssues?siteUrl=...`: URLs with Bing crawl/indexing issues; fixed issues may take days to disappear.
- `GetCrawlStats?siteUrl=...`: crawl statistics.
- `GetUrlInfo?siteUrl=...&url=...`: index details for one URL.
- `GetUrlTrafficInfo?siteUrl=...&url=...`: traffic details for one URL.
- `GetPageStats?siteUrl=...`: top page stats.
- `GetQueryStats?siteUrl=...`: top query stats.
- `GetPageQueryStats?siteUrl=...&url=...`: query stats for a page.
- `GetUrlSubmissionQuota?siteUrl=...`: remaining URL submission quota.
- `GetContentSubmissionQuota?siteUrl=...`: content submission quota.
- `GetFeeds?siteUrl=...`: submitted feeds/sitemaps.
- `GetFeedDetails?siteUrl=...&feedUrl=...`: sitemap/feed details.
- `GetUrlLinks?siteUrl=...&url=...&count=...`: inbound links for a URL.
- `GetLinkCounts?siteUrl=...&count=...`: pages with inbound link counts.

## Common Write Methods

Ask for approval before running these:

- `SubmitUrl(siteUrl, url)`: submit one URL.
- `SubmitUrlBatch(siteUrl, urlList)`: submit multiple URLs.
- `SubmitFeed(siteUrl, feedUrl)`: submit sitemap/feed.
- `AddSite(siteUrl)` and `VerifySite(siteUrl)`: add/verify a site.
- `RemoveSite(siteUrl)`, `RemoveFeed(siteUrl, feedUrl)`, role changes, blocked URL changes, crawl setting saves, site moves.

## Troubleshooting

- `InvalidApiKey`: the API key is wrong, deleted, or not accepted for the current account.
- Missing or unverified site: list `GetUserSites` and compare exact `Url` values with the requested site.
- Authorization failure with OAuth: confirm the scope, redirect URI exact match, token expiry, and whether the user revoked access.
- Empty data does not prove no Bing visibility; confirm the site is verified, exact URL form is correct, and whether the API endpoint has data for the requested surface.
