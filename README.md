# Bing Webmaster Codex Skill

Use Microsoft Bing Webmaster Tools from Codex to audit Bing SEO visibility, crawl issues, URL index status, search traffic, sitemap feeds, and URL submissions.

This repository packages a reusable Codex skill plus a small Python helper for the official Bing Webmaster API. It is designed for SEO operators, site owners, and AI coding agents that need repeatable Bing Webmaster evidence instead of manual portal screenshots.

## What This Skill Does

- Lists verified Bing Webmaster Tools properties for an authenticated account.
- Checks Bing search traffic and ranking stats for a verified site.
- Reviews Bing crawl issues for URLs that need technical SEO attention.
- Looks up URL index information for individual pages.
- Checks URL submission quota before submitting pages.
- Submits URLs or sitemap feeds with explicit dry-run safety.
- Documents API key and OAuth usage for Microsoft Bing Webmaster API workflows.

## Best For

- Bing SEO audits
- Technical SEO monitoring
- Crawl issue triage
- URL indexing checks
- Sitemap and feed submission workflows
- Comparing Bing Webmaster Tools data with Google Search Console
- Agent-ready website diagnostics in Codex

## Repository Contents

~~~text
.
|-- SKILL.md
|-- agents/
|   `-- openai.yaml
|-- references/
|   `-- api-reference.md
`-- scripts/
    `-- bing_webmaster.py
~~~

## Install The Skill

Clone or copy this folder into your Codex skills directory:

~~~powershell
git clone https://github.com/GatienBoquet/bing-webmaster.git "$env:USERPROFILE\.codex\skills\bing-webmaster"
~~~

Then invoke it in Codex:

~~~text
Use $bing-webmaster to audit Bing crawl issues and traffic for https://example.com/
~~~

## Connect Bing Webmaster Tools

The simplest authentication method is an API key.

1. Open [Bing Webmaster Tools](https://www.bing.com/webmasters/).
2. Sign in.
3. Add and verify your site.
4. Open **Settings > API Access**.
5. Generate an API key.
6. Set it only in your local shell session:

~~~powershell
$env:BING_WEBMASTER_API_KEY = "your-api-key"
~~~

Do not commit API keys, OAuth access tokens, refresh tokens, .env files, or credential exports.

## Quick API Checks

List verified sites:

~~~powershell
python scripts/bing_webmaster.py sites
~~~

Check Bing traffic stats:

~~~powershell
python scripts/bing_webmaster.py traffic --site-url "https://example.com/"
~~~

Check Bing crawl issues:

~~~powershell
python scripts/bing_webmaster.py crawl-issues --site-url "https://example.com/"
~~~

Check URL submission quota:

~~~powershell
python scripts/bing_webmaster.py quota --site-url "https://example.com/"
~~~

Preview a URL submission without sending it:

~~~powershell
python scripts/bing_webmaster.py submit-url --site-url "https://example.com/" --url "https://example.com/page" --dry-run
~~~

Submit only after confirming the target URL and quota:

~~~powershell
python scripts/bing_webmaster.py submit-url --site-url "https://example.com/" --url "https://example.com/page"
~~~

## Safety Model

Read-only calls are preferred by default. Write actions such as URL submission, feed submission, site verification, blocked URL changes, and site moves should be run only after the exact target is confirmed.

The helper supports --dry-run so agents can show the request shape before touching Bing Webmaster Tools.

## Environment Variables

~~~text
BING_WEBMASTER_API_KEY       API key from Bing Webmaster Tools
BING_WEBMASTER_ACCESS_TOKEN  OAuth bearer token for Bing Webmaster API
~~~

API key auth is usually enough for personal and site-owner workflows. OAuth is useful for delegated applications that need Webmaster.read or Webmaster.manage scopes.

## Microsoft Bing Webmaster API References

- [Bing Webmaster API documentation](https://learn.microsoft.com/en-us/bingwebmaster/)
- [Getting access to the Bing Webmaster Tools API](https://learn.microsoft.com/en-us/bingwebmaster/getting-access)
- [Bing Webmaster OAuth 2.0](https://learn.microsoft.com/en-us/bingwebmaster/oauth2)
- [IWebmasterApi method reference](https://learn.microsoft.com/en-us/dotnet/api/microsoft.bing.webmaster.api.interfaces.iwebmasterapi?view=bing-webmaster-dotnet)

## Keywords

Bing Webmaster API, Bing Webmaster Tools, Codex skill, SEO audit, technical SEO, crawl issues, URL indexing, URL submission, sitemap submission, search traffic, webmaster tools automation, Microsoft Bing SEO.
