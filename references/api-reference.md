# Bing Webmaster API Reference

Official docs entrypoint: https://learn.microsoft.com/en-us/bingwebmaster/

Method reference: https://learn.microsoft.com/en-us/dotnet/api/microsoft.bing.webmaster.api.interfaces.iwebmasterapi?view=bing-webmaster-dotnet

## Capabilities

The API exposes rank and traffic stats, link details, keyword details, crawl stats, URL index information, URL submission, sitemap/feed submission, site verification, site roles, crawl settings, blocked URLs, and site moves. It is available as JSON, POX (XML), and SOAP; this skill uses JSON.

## Auth

API key:

1. Sign in to https://www.bing.com/webmasters/.
2. Add and verify the site.
3. Open Settings > API Access and accept the terms.
4. Generate the API key.

Only one API key exists per user. It is tied to the user, not to a site, so it works for every site that user has verified.

OAuth:

- Authorize endpoint: `GET https://www.bing.com/webmasters/OAuth/authorize`
- Token endpoint: `POST https://www.bing.com/webmasters/oauth/token`
- Scopes: `webmaster.read` for read-only data, `webmaster.manage` for read/write.
- The authorization code is valid for only 5 minutes; exchange it for tokens right away.
- When the access token expires, use the refresh token to get a new one. Refresh tokens are effectively single-use: store the new refresh token returned by every refresh, and do not refresh concurrently. Reusing an old refresh token returns `invalid_grant`.
- Access tokens are sent as `Authorization: Bearer <token>`.

## JSON Endpoint Pattern

API-key JSON calls use:

```text
https://ssl.bing.com/webmaster/api.svc/json/<Method>?apikey=<API_KEY>&...
```

Example from the docs:

```http
GET /webmaster/api.svc/json/GetQueryStats?siteUrl=http://example.com&apikey=<API_KEY> HTTP/1.1
Host: ssl.bing.com
```

OAuth examples use `www.bing.com`. POST requests use JSON bodies:

```http
POST /webmaster/api.svc/json/SubmitUrl HTTP/1.1
Host: www.bing.com
Content-Type: application/json; charset=utf-8
Authorization: Bearer <access-token>

{"siteUrl":"https://example.com/","url":"https://example.com/page"}
```

Response notes:

- Responses wrap data under a top-level `d` property.
- Dates use the WCF format `"/Date(1700000000000)/"` (milliseconds since the Unix epoch, sometimes with a `-0700` offset). Convert before reporting.
- Paged methods (`GetLinkCounts`, `GetUrlLinks`) take a zero-based `page` and return `TotalPages`.

## Common Read Methods

Query-string parameters are listed as they are sent over JSON.

- `GetUserSites`: list sites available to the authenticated user.
- `GetRankAndTrafficStats?siteUrl=`: traffic stats; Microsoft notes daily updates and says traffic includes Web, Chat, News, Images, Videos, and Knowledge Panel data from March 24, 2023 onward.
- `GetCrawlIssues?siteUrl=`: URLs with Bing crawl/indexing issues; fixed issues may take days to disappear.
- `GetCrawlStats?siteUrl=`: crawl statistics.
- `GetUrlInfo?siteUrl=&url=`: index details for one URL.
- `GetUrlTrafficInfo?siteUrl=&url=`: clicks/impressions for one URL.
- `GetPageStats?siteUrl=`: top page stats.
- `GetQueryStats?siteUrl=`: top query stats.
- `GetPageQueryStats?siteUrl=&page=`: query stats for one page (`page` is the page URL). The only supported way to get per-page query metrics; loop over URLs for bulk data.
- `GetQueryPageStats?siteUrl=&query=`: page stats for one query.
- `GetQueryPageDetailStats?siteUrl=&query=&page=`: detailed stats for one query/page pair.
- `GetUrlSubmissionQuota?siteUrl=`: remaining daily and monthly URL submission quota.
- `GetContentSubmissionQuota?siteUrl=`: content submission quota.
- `GetFeeds?siteUrl=`: submitted feeds/sitemaps.
- `GetFeedDetails?siteUrl=&feedUrl=`: sitemap/feed details.
- `GetLinkCounts?siteUrl=&page=`: site pages that have inbound links, with counts (paged).
- `GetUrlLinks?siteUrl=&link=&page=`: inbound links (anchor text and source URL) for the page given in `link` (paged).

## Common Write Methods

Ask for approval before running these:

- `SubmitUrl(siteUrl, url)`: submit one URL.
- `SubmitUrlBatch(siteUrl, urlList)`: submit up to 500 URLs in one call, still limited by the remaining daily/monthly quota.
- `SubmitFeed(siteUrl, feedUrl)`: submit sitemap/feed.
- `AddSite(siteUrl)` and `VerifySite(siteUrl)`: add/verify a site.
- `RemoveSite(siteUrl)`, `RemoveFeed(siteUrl, feedUrl)`, role changes, blocked URL changes, crawl setting saves, site moves.

For frequent URL change notifications, IndexNow (https://www.indexnow.org/) is Bing's recommended protocol and does not use this API's quota.

## Troubleshooting

- `InvalidApiKey`: the API key is wrong, deleted, or not accepted for the current account.
- Missing or unverified site: list `GetUserSites` and compare exact `Url` values with the requested site.
- Authorization failure with OAuth: confirm the scope, redirect URI exact match, token expiry, and whether the user revoked access.
- `invalid_grant` on refresh: an old refresh token was reused; restart the authorization flow and store each new refresh token.
- Quota errors on submission: check `GetUrlSubmissionQuota` and split batches to fit the remaining daily quota.
- Empty data does not prove no Bing visibility; confirm the site is verified, exact URL form is correct, and whether the API endpoint has data for the requested surface. Link methods in particular can return empty results for verified sites.
